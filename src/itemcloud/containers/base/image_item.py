from __future__ import annotations
import os
from PIL import Image, ImageDraw, ImageFilter, ImagePalette, _typing
from typing import Any, Dict, IO, Literal
from collections.abc import Sequence
import matplotlib.pyplot as plt
import numpy as np
from itemcloud.containers.base.item_types import ItemType, IMAGE_FILEPATH
from itemcloud.containers.base.item import PrimitiveItem
from itemcloud.box import Box, RotateDirection 
from itemcloud.util.display_map import (
    DISPLAY_MAP_TYPE,
    create_display_map,
    MapFillType
)
from itemcloud.size import Size
from itemcloud.logger.base_logger import BaseLogger, get_logger_instance
from itemcloud.util.parsers import validate_row, to_unused_filepath
from itemcloud.util.csv_utils import write_rows

ResamplingType = Image.Resampling
RESAMPLING_TYPES = [member.name for member in ResamplingType]
MODE_TYPES = Image.MODES

g_resize_resampling: ResamplingType = ResamplingType.NEAREST
g_rotate_resampling: ResamplingType = ResamplingType.NEAREST
g_max_alpha_value_for_transparency: int = 0
g_image_mode: str | None = None

def set_global_image_settings(
    mode: str,
    opacity_pct: int,
    resize_resampling: ResamplingType,
    rotate_resampling: ResamplingType
) -> None:
    global g_image_mode
    global g_max_alpha_value_for_transparency
    global g_resize_resampling
    global g_rotate_resampling

    if not(mode in MODE_TYPES):
        raise ValueError(f"Image Mode {mode} Expected one of {'|'.join(MODE_TYPES)}")
    if not(0 <= opacity_pct and opacity_pct <= 100):
        raise ValueError(f"Image Opacity {opacity_pct}  Expected value between 0 and 100.")

    g_image_mode = mode
    g_max_alpha_value_for_transparency = round(opacity_pct/100 * 255)
    g_resize_resampling = resize_resampling
    g_rotate_resampling = rotate_resampling

def is_transparent(img_pixel) -> bool:
    global g_max_alpha_value_for_transparency
    return len(img_pixel) == 4 and img_pixel[3] <= g_max_alpha_value_for_transparency

def from_img_size(img: Image.Image) -> Size:
    return Size(img.width, img.height)

def to_img_size(size: Size) -> tuple[int, int]:
    return (size.width, size.height)

def from_img_box(box: tuple[int, int, int, int]) -> Box:
    return Box(box[0], box[1], box[2], box[3])

def to_img_box(box: Box) -> tuple[int, int, int, int]:
    return (box.left, box.upper, box.right, box.lower)

def to_img_xy(box: Box) -> tuple[int, int]:
    return (box.left, box.upper)

def to_filepath_parts(filepath: str) -> Dict[str, str]:
    return {
        'path': os.path.dirname(os.path.abspath(filepath)),
        'name': os.path.splitext(os.path.basename(filepath))[0],
        'ext': os.path.splitext(os.path.basename(filepath))[1]
    }

def from_filepath_parts(filepath_parts: Dict[str, str]) -> str:
    return os.path.join(filepath_parts['path'], filepath_parts['name']) + filepath_parts['ext']

def extend_filename(filepath: str, added_name: str) -> str:
    parts = to_filepath_parts(filepath)
    parts['name'] = parts['name'] + added_name
    return from_filepath_parts(parts)

def img_to_display_map(image: ImageItem, map_fill_type: MapFillType = MapFillType.TRANSPARENT) -> DISPLAY_MAP_TYPE:
    img = image._rendered_image
    result = create_display_map(Size(img.width, img.height), 1)
    if map_fill_type == MapFillType.TRANSPARENT:
        if img.has_transparency_data:
            pixels = img.load()
            for x in range(img.width):
                for y in range(img.height):
                    pixel = pixels[x,y]
                    if is_transparent(pixel):
                        result[y,x] = 0 # y == rows, x == cols
    if not(1 in result):
        raise ValueError('Empty Image')
    return result

class ImageItem(PrimitiveItem):
    def __init__(self, image: Image.Image, filepath: str) -> None:
        self._image = image
        self._filepath = filepath
        self._display_map = None
        self._rendered_image = image

    @property
    def image(self) -> Image.Image:
        return self._image
    
    @property
    def type(self) -> ItemType:
        return ItemType.IMAGE

    @property
    def display_map(self) -> DISPLAY_MAP_TYPE:
        if self._display_map is None:
            self._display_map = img_to_display_map(self)
        return self._display_map

    @property
    def filepath(self) -> str:
        return self._filepath
    
    @filepath.setter
    def filepath(self, filepath: str) -> None:
        self._filepath = filepath

    @property
    def name(self) -> str:
        return to_filepath_parts(self.filepath)['name']
    
    @name.setter
    def name(self, name: str) -> None:
        fp_parts = to_filepath_parts(self.filepath)
        fp_parts['name'] = name
        self.filepath = from_filepath_parts(fp_parts)
    
    def create_draw(self) -> ImageDraw:
        return ImageDraw.Draw(self._image)

    def plt_imshow(self) -> None:
        plt.imshow(self._image)

    def to_nparray(self) -> np.ndarray[Any]:
        return np.array(self._image)
    
    def to_image(
        self,
        rotated_degrees: int | None = None,
        size: Size | None = None,
        logger: BaseLogger | None = None,
        as_watermark: bool = False
    ) -> ImageItem:
        new_image = self
        if as_watermark:
            new_image = new_image.convert('RGBA')
        if rotated_degrees is not None and 0 < rotated_degrees:
            if logger:
                logger.info('Rotating Image {0} degrees'.format(rotated_degrees))
            # always rotate clockwise (negative degrees)
            new_image = new_image.rotate_item(rotated_degrees, RotateDirection.CLOCKWISE)
        
        if size is not None and new_image.size != to_img_size(size):
            if logger:
                logger.info('Resizing Image ({0},{1}) -> {2}'.format(
                    new_image.width, new_image.height,
                    size.size_to_string()
                ))
            new_image = new_image.resize(to_img_size(size))
        return new_image

    def show(self, title: str | None = None) -> None:
        self._image.show(title)

    @property
    def width(self) -> int:
        return self._image.width

    @property
    def height(self) -> int:
        return self._image.height
    
    @property
    def size(self) -> tuple[int, int]:
        return self._image.size    

    @property
    def mode(self) -> str:
        return self._image.mode
    
    @property
    def has_transparency_data(self) -> bool:
        return self._image.has_transparency_data
    
    def resize(self, size: tuple[int, int]) -> ImageItem:
        global g_resize_resampling
        result = ImageItem(self._image.resize(size=size, resample=g_resize_resampling), self.filepath)
        result.original_item = self.original_item
        return result

    def resize_item(self, size: Size) -> Item:
        return self.resize(to_img_size(size))

    def rotate(
        self,
        angle: float,
        resample: Image.Resampling = g_rotate_resampling,
        expand: int | bool = False,
        center: tuple[float, float] | None = None,
        translate: tuple[int, int] | None = None,
        fillcolor: float | tuple[float, ...] | str | None = None
    ) -> ImageItem:
        result = ImageItem(self._image.rotate(
            angle,
            resample,
            expand,
            center,
            translate,
            fillcolor
        ), self.filepath)
        result.original_item = self.original_item
        return result
    
    def rotate_item(self, angle: float, direction: RotateDirection = RotateDirection.CLOCKWISE) -> Item:
        global g_rotate_resampling
        result = self.rotate(angle=(angle if direction == RotateDirection.CLOCKWISE else -1.0 * angle), resample=g_rotate_resampling, expand=True)
        return result


    def copy_item(self) -> Item:
        result = ImageItem(self._image, extend_filename(self.filepath, '-copy'))
        result.original_item = self.original_item
        return result

    def convert(
        self,
        mode: str | None = None,
        matrix: tuple[float, ...] | None = None,
        dither: Image.Dither | None = None,
        palette: Image.Palette = Image.Palette.WEB,
        colors: int = 256,
    ) -> ImageItem:
        result = ImageItem(self._image.convert(
            mode,
            matrix,
            dither,
            palette,
            colors,
        ), self.filepath)
        result.original_item = self.original_item
        return result
    
    def putpalette(
        self,
        data: ImagePalette.ImagePalette | bytes | Sequence[int],
        rawmode: str = "RGB",
    ) -> None:
        self._image.putpalette(data, rawmode)

    def filter(
            self,
            filter: ImageFilter.Filter | type[ImageFilter.Filter]
    ) -> ImageItem:
        result = ImageItem(self._image.filter(filter), self.filepath)
        result.original_item = self.original_item
        return result
    
    def load(self) -> Any | None:
        return self._image.load()
    
    def paste(
        self,
        im: ImageItem | str | float | tuple[float, ...],
        box: ImageItem | tuple[int, int, int, int] | tuple[int, int] | None = None,
        mask: ImageItem | None = None,
    ) -> None:
        if not(isinstance(im, str) or isinstance(im, float) or isinstance(im, tuple)) and im._image.mode != self._image.mode:
            get_logger_instance().warning("Converting {0} to mode {1} for pasting into {2}".format(im.name, self._image.mode, self.name))
            im._image = im._image.convert(self._image.mode)

        if not(box is None or isinstance(box, tuple)) and box._image.mode != self._image.mode:
            get_logger_instance().warning("Converting {0} to mode {1} for box argument pasting {2} into {3}".format(box.name, self._image.mode, im.name, self.name))
            box._image = box._image.convert(self._image.mode)

        if not(mask is None) and mask._image.mode != self._image.mode:
            get_logger_instance().warning("Converting {0} to mode {1} for mask argument pasting {2} into {3}".format(mask.name, self._image.mode, im.name, self.name))
            mask._image = mask._image.convert(self._image.mode)
    
        self._image.paste(
            im if isinstance(im, str) or isinstance(im, float) or isinstance(im, tuple) else im._image,
            None if box is None else box if isinstance(box, tuple) else box._image,
            None if mask is None else mask._image
        )

    def save(
        self,
        fp: _typing.StrOrBytesPath | IO[bytes],
        format: str | None = None,
        **params: Any
    ) -> None:
        self._image.save(fp, format, **params)

    @staticmethod
    def fromarray(obj: Image.SupportsArrayInterface, mode: str | None = None) -> ImageItem:
        result = ImageItem(Image.fromarray(obj, mode), "from-array")
        result.original_item = result
        return result
    
    def alpha_composite(self, im: ImageItem, dest: Sequence[int] = (0, 0), source: Sequence[int] = (0, 0)) -> None:
        self._image.alpha_composite(im=im._image, dest=dest, source=source)

    @staticmethod
    def new_alpha_composite(im1: ImageItem, im2: ImageItem) -> ImageItem:
        result = ImageItem(Image.alpha_composite(im1._image, im2._image), im1.filepath + im2.filepath)
        result.original_item = result
        return result

    @staticmethod
    def new(
        mode: str,
        size: tuple[int, int] | list[int],
        color: float | tuple[float, ...] | str | None = 0,
    ) -> ImageItem:
        result = ImageItem(Image.new(mode, size, color), 'new-image')
        result.original_item = result
        return result
    
    @staticmethod
    def open(
        fp: _typing.StrOrBytesPath | IO[bytes],
        mode: Literal["r"] = "r",
        formats: list[str] | tuple[str, ...] | None = None,
    ) -> ImageItem:
        result = ImageItem(Image.open(fp, mode, formats), str(fp))
        result.original_item = result
        return result

    def to_csv_row(self, _directory: str = '.') -> Dict[str, Any]:
        return {
            IMAGE_FILEPATH: self.filepath
        }

    def write_row(self, directory: str, name: str, row: Dict[str, Any]) -> str:
        image_filepath = to_unused_filepath(directory, name, 'png')
        self._image.save(image_filepath, 'png')
        row[IMAGE_FILEPATH] = image_filepath
        return write_rows(self.to_write_item_filename(directory, name), [row])

    @staticmethod
    def load_row(row: Dict[str, Any]) -> Item:
        global g_image_mode
        validate_row(row, [IMAGE_FILEPATH])
        result = ImageItem.open(row[IMAGE_FILEPATH])
        if g_image_mode is not None and g_image_mode != result.mode:
            result = result.convert(g_image_mode)
        result.original_item = result
        return result


IMAGE_FORMATS = [
    'blp',
    'bmp',
    'dds',
    'dib',
    'eps',
    'gif',
    'icns',
    'ico',
    'im',
    'jpeg',
    'mpo',
    'msp',
    'pcx',
    'pfm',
    'png',
    'ppm',
    'sgi',
    'webp',
    'xbm'
]