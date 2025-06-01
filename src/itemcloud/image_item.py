from PIL import Image, ImageDraw, ImageFilter, ImagePalette, _typing
from typing import Any, IO, Literal
from collections.abc import Sequence
import matplotlib.pyplot as plt
import numpy as np


class ImageItem:
    def __init__(self, image: Image.Image) -> None:
        self._image = image

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
        return ImageItem(self._image.resize(size))

    def rotate(
        self,
        angle: float,
        resample: Image.Resampling = Image.Resampling.NEAREST,
        expand: int | bool = False,
        center: tuple[float, float] | None = None,
        translate: tuple[int, int] | None = None,
        fillcolor: float | tuple[float, ...] | str | None = None
    ):
        return ImageItem(self._image.rotate(
            angle,
            resample,
            expand,
            center,
            translate,
            fillcolor
        ))

    def convert(
        self,
        mode: str | None = None,
        matrix: tuple[float, ...] | None = None,
        dither: Image.Dither | None = None,
        palette: Image.Palette = Image.Palette.WEB,
        colors: int = 256,
    ):
        return ImageItem(self._image.convert(
            mode,
            matrix,
            dither,
            palette,
            colors,
        ))
    
    def putpalette(
        self,
        data: ImagePalette.ImagePalette | bytes | Sequence[int],
        rawmode: str = "RGB",
    ) -> None:
        self._image.putpalette(data, rawmode)

    def filter(self, filter: ImageFilter.Filter | type[ImageFilter.Filter]):
        return ImageItem(self._image.filter(filter))
    
    def load(self) -> Any | None:
        return self._image.load()
    
    def show(self, title: str | None = None) -> None:
        self._image.show(title)

    def create_draw(self) -> ImageDraw:
        return ImageDraw.Draw(self._image)

    def plt_imshow(self) -> None:
        plt.imshow(self._image)

    def to_nparray(self) -> np.ndarray[Any]:
        return np.array(self._image)

    def paste(
        self,
        im,
        box = None,
        mask = None,
    ) -> None:
        self._image.paste(
            im if isinstance(im, str) or isinstance(im, float) or isinstance(im, tuple) else im._image,
            None if box is None else box if isinstance(box, tuple) else box._image,
            None if mask is None else mask._image
        )


    @staticmethod
    def fromarray(obj: Image.SupportsArrayInterface, mode: str | None = None):
        return ImageItem(Image.fromarray(obj, mode))
    
    @staticmethod
    def alpha_composite(im1, im2):
        return ImageItem(Image.alpha_composite(im1._image, im2._image))

    @staticmethod
    def new(
        mode: str,
        size: tuple[int, int] | list[int],
        color: float | tuple[float, ...] | str | None = 0,
    ):
        return ImageItem(Image.new(mode, size, color))
    
    @staticmethod
    def open(
        fp: _typing.StrOrBytesPath | IO[bytes],
        mode: Literal["r"] = "r",
        formats: list[str] | tuple[str, ...] | None = None,
    ):
        return ImageItem(Image.open(fp, mode, formats))

    def save(
        self,
        fp: _typing.StrOrBytesPath | IO[bytes],
        format: str | None = None,
        **params: Any
    ) -> None:
        self._image.save(fp, format, **params)
