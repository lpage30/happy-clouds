from __future__ import annotations
from typing import Any, Dict, List
from itemcloud.size import Size
from itemcloud.containers.base.item_types import ItemType
from itemcloud.containers.base.item import Item
from itemcloud.containers.base.image_item import (
    extend_filename,
    ImageItem
)
from itemcloud.containers.base.text_item import TextItem
from itemcloud.util.colors import RGBAColor
from itemcloud.box import RotateDirection 
from itemcloud.util.display_map import (
    DISPLAY_MAP_TYPE
)
from itemcloud.logger.base_logger import BaseLogger
from itemcloud.util.parsers import get_value_or_default

class TextImageItem(Item):
    def __init__(
        self,
        image: ImageItem,
        text: TextItem,
        watermark_transparency: float = 1.0
    ) -> None:
        self._image = image
        self._text = text

        self._watermark_transparency = watermark_transparency

        if not(text._has_transparency):
            if self._text._foreground_color:
                self._text._foreground_color = self._text._foreground_color.to_transparent(watermark_transparency)
            else:
                self._text._foreground_color = RGBAColor(255,255,255, watermark_transparency * 255)
            self._text._background_color = None

            self._text = TextItem(
                text=self._text._text,
                font=self._text._font,
                foreground_color=self._text._foreground_color,
                background_color=self._text._background_color,
                has_transparency=True
            )
        textimage = self._text.draw_on_image(
            image = image,
            as_watermark = True
        )
        self._rendered_image = textimage._image
        self._display_map = textimage.display_map

    @property
    def type(self) -> ItemType:
        return ItemType.TEXTIMAGE

    @property
    def display_map(self) -> DISPLAY_MAP_TYPE:
        return self._display_map

    @property
    def name(self) -> str:
        return self._image.name

    @property
    def width(self) -> int:
        return self._rendered_image.width

    @property
    def height(self) -> int:
        return self._rendered_image.height

    def resize_item(self, size: Size) -> Item:
        if self.item_size.is_equal(size):
            return self
        shrink = size.is_less_than(self.item_size)
        new_image = self._image
        new_text = self._text
        if shrink:
            if size.is_less_than(new_image.item_size):
                new_image = new_image.resize_item(size)
            if size.is_less_than(new_text.item_size):
                new_text = new_text.resize_item(size)
        else:
            if new_image.item_size.is_less_than(size):
                new_image = new_image.resize_item(size)
            if new_text.item_size.is_less_than(size):
                new_text = new_text.resize_item(size)

        return TextImageItem(
            image=new_image,
            text=new_text,
            watermark_transparency=self._watermark_transparency
        )

    def rotate_item(self, angle: float, direction: RotateDirection = RotateDirection.CLOCKWISE) -> Item:
        return TextImageItem(
            image=self._image.rotate_item(angle, direction),
            text=self._text.rotate_item(angle, direction),
            watermark_transparency=self._watermark_transparency
        )

    def copy_item(self) -> Item:
        return TextImageItem(
            image=self._image.copy_item(),
            text=self._text.copy_item(),
            watermark_transparency=self._watermark_transparency,
        )

    def to_image(
        self,
        rotated_degrees: int | None = None,
        size: Size | None = None,
        logger: BaseLogger | None = None,
        _as_watermark: bool = False
    ) -> ImageItem:
        image = self._image.to_image(
            rotated_degrees,
            size,
            logger
        )
        image = self._text.draw_on_image(
            image,
            rotated_degrees,
            size,
            logger,
            True
        )
        image.filepath = extend_filename(self._image.filepath, 'text-image')
        return image

    def show(self, title: str | None = None) -> None:
        self.to_image().show(title)
    
    def to_csv_row(self, directory: str = '.') -> Dict[str, Any]:
        result = self._image.to_csv_row(directory)
        result.update(self._text.to_csv_row(directory))
        result.update({
            TEXT_TRANSPARENCY_PERCENT: self._watermark_transparency
        })
        return result

    def write_row(self, directory: str, name: str, row: Dict[str, Any]) -> str:
        return self._image.write_row(directory, name, row)

    @staticmethod
    def load_row(row: Dict[str, Any]) -> Item:
        image = ImageItem.load_row(row)
        text = TextItem.load_row(row)
        return TextImageItem(
            image,
            text,
            get_value_or_default(TEXT_TRANSPARENCY_PERCENT, row, 1.0, float)
        )
    
TEXT_TRANSPARENCY_PERCENT = 'transparency_percent'