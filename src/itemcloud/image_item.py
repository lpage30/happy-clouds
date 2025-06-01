from __future__ import annotations
from PIL import Image, ImageDraw, ImageFilter, ImagePalette, _typing
from typing import Any, IO, List, Literal
from collections.abc import Sequence
import matplotlib.pyplot as plt
import numpy as np
from itemcloud.util.display_map import (
    DISPLAY_MAP_TYPE,
    img_to_display_mask
)

class ImageItem:
    def __init__(self, image: Image.Image, version_stack: List[ImageItem] = list()) -> None:
        self._image = image
        self._versions = version_stack
        self._display_mask = img_to_display_mask(image)        

    # ImageItem-specific properties/methods
    @property
    def display_mask(self) -> DISPLAY_MAP_TYPE:
        return self._display_mask

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
        self._versions = reset_version._versions
        self._display_mask = reset_version._display_mask
        return True    

    def create_draw(self) -> ImageDraw:
        return ImageDraw.Draw(self._image)

    def plt_imshow(self) -> None:
        plt.imshow(self._image)

    def to_nparray(self) -> np.ndarray[Any]:
        return np.array(self._image)
    

    # supported PIL.Image.Image properties/methods
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
     
    def resize(self, size: tuple[int, int]):
        return ImageItem(self._image.resize(size), self.all_versions())

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
        ), self.all_versions())

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
        ), self.all_versions())
    
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
        return ImageItem(self._image.filter(filter), self.all_versions())
    
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
        return ImageItem(Image.fromarray(obj, mode))
    
    @staticmethod
    def alpha_composite(im1: ImageItem, im2: ImageItem) -> ImageItem:
        return ImageItem(Image.alpha_composite(im1._image, im2._image))

    @staticmethod
    def new(
        mode: str,
        size: tuple[int, int] | list[int],
        color: float | tuple[float, ...] | str | None = 0,
    ) -> ImageItem:
        return ImageItem(Image.new(mode, size, color))
    
    @staticmethod
    def open(
        fp: _typing.StrOrBytesPath | IO[bytes],
        mode: Literal["r"] = "r",
        formats: list[str] | tuple[str, ...] | None = None,
    ) -> ImageItem:
        return ImageItem(Image.open(fp, mode, formats))
