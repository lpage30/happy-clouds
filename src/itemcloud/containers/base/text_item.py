from __future__ import annotations
from typing import Dict, Any
from itemcloud.size import Size
from itemcloud.util.colors import (Color, to_color)
from itemcloud.util.fonts import (Font, FontName, FontSize, FontTextAttributes, pick_font, pick_font_size, value_to_FontLayout)
from itemcloud.util.font_categories import (FontTypeCategories, FontUsageCategory)
from itemcloud.util.display_map import (
    DISPLAY_MAP_TYPE
)
from itemcloud.containers.base.image_item import (
    ImageItem
)
from itemcloud.containers.base.item_types import ItemType, TEXT_TEXT
from itemcloud.containers.base.item import Item
from itemcloud.logger.base_logger import BaseLogger
from itemcloud.box import RotateDirection
from itemcloud.util.parsers import (
    get_value_or_default,
    get_complex_value_or_default,
    validate_row,
    field_exists
)
from itemcloud.util.csv_utils import write_rows
class TextItem(Item):
    def __init__(
        self,
        text: str,
        font: Font,
        foreground_color: Color | None,
        background_color: Color | None,
        has_transparency: bool = False,
        size: Size | None = None
    ) -> None:
        image = font.to_image(
            text=text,
            fg_color=foreground_color,
            bg_color=background_color,
            size=size
        )
        self._size = image.item_size
        
        self._text = text
        self._font = font
        self._foreground_color = foreground_color
        self._background_color = background_color
        self._rendered_image = image._image
        self._display_map = image.display_map
        self._has_transparency = has_transparency

    @property
    def type(self) -> ItemType:
        return ItemType.TEXT

    @property
    def display_map(self) -> DISPLAY_MAP_TYPE:
        return self._display_map

    @property
    def width(self) -> int:
        return self._rendered_image.width

    @property
    def height(self) -> int:
        return self._rendered_image.height

    def resize_item(self, size: Size) -> Item:
        if self.is_equal(size):
            return self
        new_font = self._font.find_best_fit(self._text, size)
        result = TextItem(
            self._text,
            new_font,
            self._foreground_color,
            self._background_color,
            self._has_transparency,
            size
        )
        return result    
    
    def rotate_item(self, angle: float, direction: RotateDirection = RotateDirection.CLOCKWISE) -> Item:
        angle = angle if RotateDirection.CLOCKWISE == direction else -angle
        font = self._font.to_image_font(
            self._text,
            angle,
            self.item_size
        )
        return TextItem(
            self._text,
            font,
            self._foreground_color,
            self._background_color,
            self._has_transparency,
            self.item_size   
        )

    def copy_item(self) -> Item:
        return TextItem(
            self._text,
            self._font,
            self._foreground_color,
            self._background_color,
            self._has_transparency,
            self.item_size
        )

    def draw_on_image(
        self,
        image: ImageItem,
        rotated_degrees: int | None = None,
        size: Size | None = None,
        logger: BaseLogger | None = None,
        as_watermark: bool = False,
        xy: tuple[float, float] | None = None,
    ) -> ImageItem:
        return self._font.draw_on_image(
            self._text,
            image,
            self._foreground_color,
            rotated_degrees,
            size,
            logger,
            as_watermark,
            xy
        )

    def to_image(
        self,
        rotated_degrees: int | None = None,
        size: Size | None = None,
        logger: BaseLogger | None = None,
        as_watermark: bool = False
    ) -> ImageItem:
        expected_size = self.item_size if size is None else size
        result = self._font.to_image(
            self._text,
            self._foreground_color,
            self._background_color,
            rotated_degrees,
            expected_size,
            logger,
            as_watermark
        )
        return result

    def show(self, title: str | None = None) -> None:
        self.to_image().show(title)

    def to_csv_row(self, _directory: str = '.') -> Dict[str, Any]:
        return {
            TEXT_TEXT: self._text,
            TEXT_FONT_NAME_PATH: self._font.font_name,
            TEXT_MIN_FONT_SIZE: self._font.min_font_size,
            TEXT_FONT_SIZE: self._font.font_size,
            TEXT_MAX_FONT_SIZE: self._font.max_font_size,
            TEXT_LAYOUT: self._font.layout,
            TEXT_STROKE_WIDTH: self._font.stroke_width if not None else '',
            TEXT_ANCHOR: self._font.anchor,
            TEXT_ALIGN: self._font.align,
            TEXT_FOREGROUND_COLOR: self._foreground_color.name if self._foreground_color is not None else '',
            TEXT_BACKGROUND_COLOR: self._background_color.name if self._background_color is not None else ''
        }

    def write_row(self, directory: str, name: str, row: Dict[str, Any]) -> str:
        return write_rows(self.to_write_item_filename(directory, name), [row])

    @staticmethod
    def load_row(row: Dict[str, Any]) -> Item:
        validate_row(row, [TEXT_TEXT])

        font_name = get_value_or_default(
            TEXT_FONT_NAME_PATH, row,
            pick_font(), lambda v: pick_font() if v.lower().strip() == 'random' else FontName(v, FontTypeCategories.CUSTOM)
        )
        font_size = get_complex_value_or_default(
            [TEXT_MIN_FONT_SIZE, TEXT_MAX_FONT_SIZE],
            row,
            pick_font_size(),
            lambda va: pick_font_size() if any([v.lower().strip() == 'random' for v in va]) else FontSize(FontUsageCategory.CUSTOM, float(va[0]), float(va[1]))
        )

        text_attributes = FontTextAttributes(
            value_to_FontLayout(get_value_or_default(TEXT_LAYOUT, row, None, int)),
            get_value_or_default(TEXT_STROKE_WIDTH, row, None, int),
            get_value_or_default(TEXT_ANCHOR, row, None),
            get_value_or_default(TEXT_ALIGN, row, None)
        )
        fg_color = get_value_or_default(
            TEXT_FOREGROUND_COLOR,
            row,
            None,
            lambda v: to_color(v.strip())
        )
        bg_color = get_value_or_default(
            TEXT_BACKGROUND_COLOR,
            row,
            None,
            lambda v: to_color(v.strip())
        )
        
        result = TextItem(
            row[TEXT_TEXT],
            Font(font_name, font_size, text_attributes),
            fg_color,
            bg_color
        )
        if field_exists(TEXT_FONT_SIZE, row):
            result._font.font_size = float(row[TEXT_FONT_SIZE])
            text_box = result._font.to_box(result._text)
            result._width = text_box.width
            result._height = text_box.height

        return result


TEXT_FONT_NAME_PATH = 'font_name_path'
TEXT_MIN_FONT_SIZE = 'min_font_size'
TEXT_FONT_SIZE = 'font_size'
TEXT_MAX_FONT_SIZE = 'max_font_size'
TEXT_LAYOUT = 'text_layout'
TEXT_STROKE_WIDTH = 'text_stroke_width'
TEXT_ANCHOR = 'text_anchor'
TEXT_ALIGN = 'text_align'
TEXT_FOREGROUND_COLOR = 'foreground_color'
TEXT_BACKGROUND_COLOR = 'background_color'

TEXT_ITEM_HEADERS = [
    TEXT_TEXT,
    TEXT_FONT_NAME_PATH,
    TEXT_MIN_FONT_SIZE,
    TEXT_FONT_SIZE,
    TEXT_MAX_FONT_SIZE,
    TEXT_LAYOUT,
    TEXT_STROKE_WIDTH,
    TEXT_ANCHOR,
    TEXT_ALIGN,
    TEXT_FOREGROUND_COLOR,
    TEXT_BACKGROUND_COLOR
]