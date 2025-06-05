from __future__ import annotations
import csv
import os
from PIL import Image, ImageDraw, ImageFilter, ImagePalette, _typing
from typing import Any, Dict, IO, List, Literal
from collections.abc import Sequence
import matplotlib.pyplot as plt
import numpy as np
from itemcloud.containers.base.item import (Item, ItemType)
from itemcloud.box import RotateDirection 
from itemcloud.util.display_map import (
    DISPLAY_MAP_TYPE,
    img_to_display_mask
)
from itemcloud.size import Size
from itemcloud.logger.base_logger import BaseLogger
from itemcloud.util.parsers import validate_row, to_unused_filepath


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

class ImageItem(Item):
    def __init__(self, image: Image.Image, filepath: str, version_stack: List[ImageItem] = list()) -> None:
        self._image = image
        self._filepath = filepath
        self._versions = version_stack
        self._display_mask = img_to_display_mask(image)

    @property
    def type(self) -> ItemType:
        return ItemType.IMAGE

    @property
    def display_mask(self) -> DISPLAY_MAP_TYPE:
        return self._display_mask

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
    
    @property
    def version_count(self) -> int:
        return len(self._versions)
    
    def all_versions(self) -> List[ImageItem]:
        versions = self._versions.copy()
        versions.append(self)
        return versions
    
    def get_version(self, versionNo: int) -> ImageItem | None:
        if versionNo < len(self._versions):
            return self._versions[versionNo]
        return None

    def reset_to_version(self, versionNo: int = 0) -> bool:
        reset_version = self.get_version(versionNo)
        if reset_version is None:
            return False
        self._image = reset_version._image
        self._filepath = reset_version._filepath
        self._versions = reset_version._versions
        self._display_mask = reset_version._display_mask
        return True    

    def reset_to_original_version(self) -> Item:
        return self.reset_to_version()

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
        if rotated_degrees is not None and 0 < rotated_degrees:
            if logger:
                logger.info('Rotating Image {0} degrees'.format(rotated_degrees))
            # always rotate clockwise (negative degrees)
            new_image = new_image.rotate(-rotated_degrees, expand=1)
        
        if size is not None and new_image.size != size.image_tuple:
            if logger:
                logger.info('Resizing Image ({0},{1}) -> {2}'.format(
                    new_image.width, new_image.height,
                    size.size_to_string()
                ))
            new_image = new_image.resize(size.image_tuple)
        if as_watermark:
            new_image = new_image.convert('RGBA')
        return new_image

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
     
    def resize(self, size: tuple[int, int]) -> ImageItem:
        return ImageItem(self._image.resize(size), self.filepath, self.all_versions())

    def resize_item(self, size: tuple[int, int]) -> Item:
        return self.resize(size)

    def rotate(
        self,
        angle: float,
        resample: Image.Resampling = Image.Resampling.NEAREST,
        expand: int | bool = False,
        center: tuple[float, float] | None = None,
        translate: tuple[int, int] | None = None,
        fillcolor: float | tuple[float, ...] | str | None = None
    ) -> ImageItem:
        return ImageItem(self._image.rotate(
            angle,
            resample,
            expand,
            center,
            translate,
            fillcolor
        ), self.filepath, self.all_versions())
    
    def rotate_item(self, angle: float, direction: RotateDirection = RotateDirection.CLOCKWISE) -> Item:
        return self.rotate(angle if direction == RotateDirection.CLOCKWISE else -1.0 * angle)

    def copy(self) -> ImageItem:
        return ImageItem(self._image, extend_filename(self.filepath, '-copy'))
    
    def copy_item(self) -> Item:
        return self.copy()
    
    def convert(
        self,
        mode: str | None = None,
        matrix: tuple[float, ...] | None = None,
        dither: Image.Dither | None = None,
        palette: Image.Palette = Image.Palette.WEB,
        colors: int = 256,
    ) -> ImageItem:
        return ImageItem(self._image.convert(
            mode,
            matrix,
            dither,
            palette,
            colors,
        ), self.filepath, self.all_versions())
    
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
        return ImageItem(self._image.filter(filter), self.filepath, self.all_versions())
    
    def load(self) -> Any | None:
        return self._image.load()
    
    def show(self, title: str | None = None) -> None:
        self._image.show(title)

    def paste(
        self,
        im: ImageItem | str | float | tuple[float, ...],
        box: ImageItem | tuple[int, int, int, int] | tuple[int, int] | None = None,
        mask: ImageItem | None = None,
    ) -> None:
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
        return ImageItem(Image.fromarray(obj, mode), "from-array")
    
    @staticmethod
    def alpha_composite(im1: ImageItem, im2: ImageItem) -> ImageItem:
        return ImageItem(Image.alpha_composite(im1._image, im2._image), im1.filepath + im2.filepath)

    @staticmethod
    def new(
        mode: str,
        size: tuple[int, int] | list[int],
        color: float | tuple[float, ...] | str | None = 0,
    ) -> ImageItem:
        return ImageItem(Image.new(mode, size, color), 'new-image')
    
    @staticmethod
    def open(
        fp: _typing.StrOrBytesPath | IO[bytes],
        mode: Literal["r"] = "r",
        formats: list[str] | tuple[str, ...] | None = None,
    ) -> ImageItem:
        return ImageItem(Image.open(fp, mode, formats), str(fp))

    def to_csv_row(self) -> Dict[str, Any]:
        return {
            IMAGE_FILEPATH: self.filepath
        }

    def write_row(self, name: str, directory: str, row: Dict[str, Any]) -> str:
        image_filepath = to_unused_filepath(directory, name, 'png')
        self._image.save(image_filepath, 'png')
        row[IMAGE_FILEPATH] = image_filepath
        csv_filepath = to_unused_filepath(directory, name, 'csv')
        with open(csv_filepath, 'w') as file:
            csv_writer = csv.DictWriter(file, fieldnames=list(row.keys()))
            csv_writer.writeheader()
            csv_writer.writerow(row)
        return csv_filepath        

    @staticmethod
    def load_image(row: Dict[str, Any]) -> ImageItem:
        validate_row(row, [IMAGE_FILEPATH])
        return ImageItem.open(row[IMAGE_FILEPATH])

    @staticmethod
    def load_item(row: Dict[str, Any]) -> Item:
        return ImageItem.load_image(row)


IMAGE_FILEPATH = 'image_filepath'