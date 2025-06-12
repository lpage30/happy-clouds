import numpy as np
from itemcloud.logger.base_logger import BaseLogger
from itemcloud.containers.named_image import NamedImage
from itemcloud.size import (Size, ResizeType)
from itemcloud.util.search_types import SearchPattern
from itemcloud.reservations import (
    Reservations,
)
from itemcloud.util.display_map import (
    create_display_map,
    DISPLAY_MAP_TYPE,
    DISPLAY_NP_DATA_TYPE
)
from itemcloud.util.parsers import (
    field_exists,
    validate_row,
    get_value_or_default,
    get_complex_value_or_default,
    to_unused_filepath,
    to_existing_filepath
)
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import io
import os
from PIL import ImageFilter
from typing import Any, Dict
import csv
import traceback
from itemcloud.containers.base.image_item import ImageItem
from itemcloud.util.colors import (
    Color,
    ColorSource,
    generate_colors,
    to_ImagePalette
) 
from itemcloud.layout.base.layout_item import LayoutItem
import itemcloud.layout.base.layout_defaults as layout_defaults
import itemcloud.item_cloud_defaults as item_cloud_defaults
  
class LayoutCanvas:
    def __init__(
        self,
        size: Size,
        mode: str,
        background_color: str | None,
        reservation_map: DISPLAY_MAP_TYPE | None,
        name: str | None = None
    ) -> None:
        self._name = name if name else 'itemcloud'
        self._size = size
        self._mode = mode
        self._background_color = background_color
        self._reservation_map = reservation_map if reservation_map is not None else create_display_map(size)
        self._reservation_colors = [*generate_colors(ColorSource.PICKED, self._reservation_map.max() + 1)]

    
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, v: str) -> None:
        self._name = v
    
    @property
    def size(self) -> Size:
        return self._size

    @property
    def mode(self) -> str:
        return self._mode
    
    @property
    def background_color(self) -> str | None:
        return self._background_color
    
    @property
    def reservation_map(self) -> DISPLAY_MAP_TYPE:
        return self._reservation_map
    
    @property
    def reservation_colors(self) -> list[Color]:
        return self._reservation_colors
    
    def to_image(self, scale: float = 1.0) -> NamedImage:
        image = ImageItem.new(
            self.mode, 
            self.size.scale(scale).image_tuple,
            self.background_color
        )
        return NamedImage(image, self.name)
    
    def to_reservation_image(self) -> NamedImage:
        image = ImageItem.new(
            'P',
            (self.reservation_map.shape[1], self.reservation_map.shape[0])
        )
        image.putpalette(to_ImagePalette(self.reservation_colors))
        pixels = image.load()
        for y in range(self.reservation_map.shape[0]):
            for x in range(self.reservation_map.shape[1]):
                pixels[x, y] = int(self.reservation_map[y,x])
        
        return NamedImage(image, '{0}.reservation_map'.format(self.name))
    
    def write(self, layout_directory: str) -> Dict[str,Any]:
        reservation_map_csv_filepath = to_unused_filepath(layout_directory, '{0}.reservation_map'.format(self.name), 'csv')
        np.savetxt(
            fname=reservation_map_csv_filepath,
            X=self._reservation_map,
            fmt='%d',
            delimiter=','
        )
        return {
            layout_defaults.LAYOUT_CANVAS_NAME: self.name,
            layout_defaults.LAYOUT_CANVAS_MODE: self.mode,
            layout_defaults.LAYOUT_CANVAS_BACKGROUND_COLOR: self.background_color if self.background_color is not None else '',
            layout_defaults.LAYOUT_CANVAS_SIZE_WIDTH: self.size.width,
            layout_defaults.LAYOUT_CANVAS_SIZE_HEIGHT: self.size.height,
            layout_defaults.LAYOUT_CANVAS_RESERVATION_MAP_FILEPATH: reservation_map_csv_filepath
        }

    @staticmethod
    def empty_csv_data() -> Dict[str,Any]:
        return { header:'' for header in layout_defaults.LAYOUT_CANVAS_HEADERS }

    @staticmethod
    def load(row: Dict[str,Any], _row_no: int, layout_directory: str):
        validate_row(row, [
            layout_defaults.LAYOUT_CANVAS_SIZE_WIDTH,
            layout_defaults.LAYOUT_CANVAS_SIZE_HEIGHT,
            layout_defaults.LAYOUT_CANVAS_MODE
        ])
        
        return LayoutCanvas(
            Size(int(row[layout_defaults.LAYOUT_CANVAS_SIZE_WIDTH]), int(row[layout_defaults.LAYOUT_CANVAS_SIZE_HEIGHT])),
            row[layout_defaults.LAYOUT_CANVAS_MODE],
            get_value_or_default(layout_defaults.LAYOUT_CANVAS_BACKGROUND_COLOR, row, None),
            get_value_or_default(layout_defaults.LAYOUT_CANVAS_RESERVATION_MAP_FILEPATH, row, None, lambda v: np.loadtxt(
                fname=to_existing_filepath(v, layout_directory),
                dtype=DISPLAY_NP_DATA_TYPE,
                delimiter=','
            )),
            get_value_or_default(layout_defaults.LAYOUT_CANVAS_NAME, row, None),
        )

class LayoutContour:
    
    def __init__(
        self,
        mask: np.ndarray | None,
        width: float,
        color: str
    ) -> None:
        self._mask = mask
        self._width = width
        self._color = color
    
    @property
    def mask(self) -> np.ndarray | None:
        return self._mask
    
    @property
    def width(self) -> float:
        return self._width
    
    @property
    def color(self) -> str:
        return self._color
    
    def to_image(self, image: NamedImage) -> NamedImage:
        if self.mask == None or self.width == 0:
            return image
        
        contour = ImageItem.fromarray(self.mask.astype(np.uint8))
        contour = contour.resize(image.image.size)
        contour = contour.filter(ImageFilter.FIND_EDGES)
        contour = contour.to_nparray()

        # make sure borders are not drawn before changing width
        contour[[0, -1], :] = 0
        contour[:, [0, -1]] = 0

        # use gaussian to change width, divide by 10 to give more resolution
        radius = self.width / 10
        contour = ImageItem.fromarray(contour)
        contour = contour.filter(ImageFilter.GaussianBlur(radius=radius))
        contour = contour.to_nparray() > 0
        contour = np.dstack((contour, contour, contour))

        # color the contour
        ret = image.image.to_nparray() * np.invert(contour)
        if self.color != 'black':
            color = ImageItem.new(image.image.mode, image.image.size, self.color)
            ret += color.to_nparray() * contour

        return NamedImage(
            ImageItem.fromarray(ret),
            image.name
        )

    def write(self, layout_name: str, layout_directory: str) -> Dict[str,Any]:
        mask_filepath = ''
        if self.mask is not None:
            mask_filepath = to_unused_filepath(layout_directory, '{0}.contour_mask'.format(layout_name), 'png')
            ImageItem.fromarray(self.mask).save(mask_filepath)

        return {     
            layout_defaults.LAYOUT_CONTOUR_MASK_IMAGE_FILEPATH: mask_filepath,
            layout_defaults.LAYOUT_CONTOUR_WIDTH: self.width,
            layout_defaults.LAYOUT_CONTOUR_COLOR: self.color
        }

    @staticmethod
    def empty_csv_data() -> Dict[str,Any]:
        return { header:'' for header in layout_defaults.LAYOUT_CONTOUR_HEADERS }

    @staticmethod
    def load(row: Dict[str,Any], _row_no: int, layout_directory: str):
        validate_row(row, [
            layout_defaults.LAYOUT_CONTOUR_WIDTH,
            layout_defaults.LAYOUT_CONTOUR_COLOR
        ])

        return LayoutContour(
            get_value_or_default(layout_defaults.LAYOUT_CONTOUR_MASK_IMAGE_FILEPATH, row, None,
                lambda v: NamedImage.load(to_existing_filepath(v, layout_directory)).image.to_nparray()
            ),
            float(row[layout_defaults.LAYOUT_CONTOUR_WIDTH]),
            row[layout_defaults.LAYOUT_CONTOUR_COLOR]
        )


class Layout:
    def __init__(
        self,
        canvas: LayoutCanvas,
        contour: LayoutContour,
        items: list[LayoutItem],
        max_items: int | None = None,
        min_item_size: Size | None = None,
        item_step: int | None = None,
        item_rotation_increment: int | None = None,
        resize_type: ResizeType | None = None,
        scale: float | None = None,
        margin: int | None = None,
        name: str | None = None,
        total_threads: int | None = None,
        latency_str: str = '',
        search_pattern: SearchPattern | None = None

    ) -> None:
        self._name = name if name else 'imagecloud.layout'
        self._canvas = canvas
        self._contour = contour
        self._items = items
        for item in items:
            item.reservation_color = canvas.reservation_colors[item.reservation_no]
            
        self.max_items = max_items if max_items is not None else int(item_cloud_defaults.DEFAULT_MAX_ITEMS)
        self.min_item_size = min_item_size if min_item_size is not None else int(item_cloud_defaults.DEFAULT_MIN_ITEM_SIZE)
        self.item_step = item_step if item_step is not None else int(item_cloud_defaults.DEFAULT_STEP_SIZE)
        self.item_rotation_increment = item_rotation_increment if item_rotation_increment is not None else int(item_cloud_defaults.DEFAULT_ROTATION_INCREMENT)
        self.resize_type = resize_type if resize_type is not None else ResizeType[item_cloud_defaults.DEFAULT_RESIZE_TYPE]
        self.scale = scale if scale is not None else int(item_cloud_defaults.DEFAULT_SCALE)

        self.margin = margin if margin is not None else int(item_cloud_defaults.DEFAULT_MARGIN)
        self.total_threads = total_threads if total_threads is not None else int(item_cloud_defaults.DEFAULT_TOTAL_THREADS)
        self._latency_str = latency_str
        self._search_pattern = search_pattern if search_pattern is not None else SearchPattern[item_cloud_defaults.DEFAULT_SEARCH_PATTERN]
    
    @property
    def name(self) -> str:
        return self._name

    def set_names(self, layout: str, canvas: str) -> None:
        self._name = layout
        self.canvas.name = canvas
        
    @property
    def canvas(self) -> LayoutCanvas:
        return self._canvas
    
    @property
    def contour(self) -> LayoutContour:
        return self._contour

    @property
    def items(self) -> list[LayoutItem]:
        return self._items
    
    def reconstruct_reservation_map(self,logger: BaseLogger ) -> DISPLAY_MAP_TYPE:
        return Reservations.create_reservation_map(
            logger,
            self.canvas.size,
            [item.reservation_box for item in self.items]
        )
    
    def to_image(
        self,
        logger: BaseLogger,
        scale: float = 1.0
    ) -> NamedImage:
        logger.reset_context()
        canvas = self.canvas.to_image(scale)

        total = len(self.items)
        logger.info('pasting {0} images into imagecloud canvas'.format(total))

        for i in range(total):
            item: LayoutItem = self.items[i]
            logger.info('pasting Image[{0}/{1}] {2} into imagecloud canvas'.format(i + 1, total, item.name))            
            image = item.to_image(logger, scale)
            box = item.placement_box.scale(scale)
            try:
                canvas.image.paste(
                    im=image.image,
                    box=box.image_tuple
                )
            except Exception as e:
                logger.error('Error pasting {0} into {1}. {2} \n{3}'.format(image.name, canvas.name, str(e), '\n'.join(traceback.format_exception(e))))

        return self.contour.to_image(canvas)

    def to_reservation_chart_image(self) -> NamedImage:
        reservation_image: NamedImage = self.canvas.to_reservation_image()
        legend_handles: list[mpatches.Patch] = [
            mpatches.Patch(
                color=self.canvas.reservation_colors[0].hex_code,
                label='UNRESERVED'
            ),
            *[item.to_legend_handle() for item in self.items]
        ]
        reservation_image.image.plt_imshow()
        plt.legend(handles=legend_handles, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.axis('off')
        plt.grid(True)
        plt.tight_layout()        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image = ImageItem.open(buf)
        image.load()
        result = NamedImage(
            image,
            reservation_image.name
        )
        buf.close()
        return result

    def write(self, csv_filepath: str) -> None:
        layout_directory = os.path.dirname(csv_filepath)
        layout_data = {
            layout_defaults.LAYOUT_MAX_ITEMS: self.max_items,
            layout_defaults.LAYOUT_MIN_ITEM_SIZE_WIDTH: self.min_item_size.width,
            layout_defaults.LAYOUT_MIN_ITEM_SIZE_HEIGHT: self.min_item_size.height,
            layout_defaults.LAYOUT_ITEM_STEP: self.item_step,
            layout_defaults.LAYOUT_ITEM_ROTATION_INCREMENT: self.item_rotation_increment,
            layout_defaults.LAYOUT_RESIZE_TYPE: self.resize_type.name,
            layout_defaults.LAYOUT_SCALE: self.scale,
            layout_defaults.LAYOUT_MARGIN: self.margin,
            layout_defaults.LAYOUT_NAME: self.name,
            layout_defaults.LAYOUT_TOTAL_THREADS: self.total_threads,
            layout_defaults.LAYOUT_LATENCY: self._latency_str,
            layout_defaults.LAYOUT_SEARCH_PATTERN: self._search_pattern.name,
        }
        with open(csv_filepath, 'w') as file:
            csv_writer = csv.DictWriter(file, fieldnames=layout_defaults.LAYOUT_CSV_HEADERS)
            csv_writer.writeheader()
            for i in range(len(self.items)):
                csv_writer.writerow({
                    **(layout_data if i == 0 else { header:'' for header in layout_defaults.LAYOUT_HEADERS }),
                    **(self.canvas.write(layout_directory) if i == 0 else LayoutCanvas.empty_csv_data()),
                    **(self.contour.write(self.name, layout_directory) if i == 0 else LayoutContour.empty_csv_data()),
                    **(self.items[i].write(layout_directory))
                })
                
        
    @staticmethod
    def load(csv_filepath: str):
        try:
            canvas: LayoutCanvas | None = None
            items: list[LayoutItem] = list()
            contour: LayoutContour | None = None
            layout_directory: str = os.path.dirname(csv_filepath)
            layout_data: Dict[str,Any] = {}
            with open(csv_filepath, 'r', encoding='utf-8-sig') as file:    
                csv_reader = csv.DictReader(file)
                row_no = 0
                for row in csv_reader:
                    row_no += 1
                    if all([field_exists(header, row) for header in layout_defaults.LAYOUT_HEADERS]):
                        layout_data = {}
                        for header in layout_defaults.LAYOUT_HEADERS:
                            layout_data[header] = row[header]

                    if canvas == None:
                        canvas = LayoutCanvas.load(row, row_no, layout_directory)
                    if contour == None:
                        contour = LayoutContour.load(row, row_no, layout_directory)
                    items.append(LayoutItem.load(row, row_no, layout_directory, create_layout_item))
            
            if canvas == None or contour == None or 0 == len(items):
                return None
            
            max_items = get_value_or_default(layout_defaults.LAYOUT_MAX_ITEMS, layout_data, None, int)
            min_item_size = get_complex_value_or_default([
                layout_defaults.LAYOUT_MIN_ITEM_SIZE_WIDTH,
                layout_defaults.LAYOUT_MIN_ITEM_SIZE_HEIGHT
                ], layout_data, None, lambda va: Size(int(va[0]), int(va[1]))
             )
            item_step = get_value_or_default(layout_defaults.LAYOUT_ITEM_STEP, layout_data, None, int)
            resize_type = get_value_or_default(layout_defaults.LAYOUT_RESIZE_TYPE, layout_data, None, lambda v: ResizeType[v])
            scale = get_value_or_default(layout_defaults.LAYOUT_SCALE, layout_data, None, float)
            margin = get_value_or_default(layout_defaults.LAYOUT_MARGIN, layout_data, None, int)
            name = get_value_or_default(layout_defaults.LAYOUT_NAME, layout_data, None)  
            total_threads = get_value_or_default(layout_defaults.LAYOUT_TOTAL_THREADS, layout_data, None, int)
            latency_str = get_value_or_default(layout_defaults.LAYOUT_LATENCY, layout_data, '')
            search_pattern =  get_value_or_default(layout_defaults.LAYOUT_SEARCH_PATTERN, layout_data, None, lambda v: SearchPattern[v])
            return Layout(
                canvas,
                contour,
                items,
                max_items,
                min_item_size,
                item_step,
                resize_type,
                scale,
                margin,
                name,
                total_threads,
                latency_str,
                search_pattern
            )
        except Exception as e:
            raise Exception(str(e))


