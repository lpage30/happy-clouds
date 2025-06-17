from __future__ import annotations
from typing import List, Dict, Any
from itemcloud.size import Size
from itemcloud.util.colors import (Color, NamedColor, pick_color, ColorSource)
from itemcloud.util.fonts import (Font, FontName, FontSize, FontTextAttributes,pick_font, pick_font_size)
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
        version_stack: List[TextItem] = list(),
        has_transparency: bool = False
    ) -> None:
        image = font.to_image(
            text,
            foreground_color,
            background_color
        )

        self._text = text
        self._font = font
        self._foreground_color = foreground_color
        self._background_color = background_color
        self._rendered_image = image._image
        self._display_map = image.display_map
        self._versions = version_stack
        self._has_transparency = has_transparency

    @property
    def type(self) -> ItemType:
        return ItemType.TEXT

    @property
    def display_map(self) -> DISPLAY_MAP_TYPE:
        return self._display_map

    @property
    def version_count(self) -> int:
        return len(self._versions)

    @property
    def width(self) -> int:
        return self._rendered_image.width

    @property
    def height(self) -> int:
        return self._rendered_image.height

    def all_versions(self) -> List[TextItem]:
        versions = self._versions.copy()
        versions.append(self)
        return versions
    
    def get_version(self, versionNo: int) -> TextItem | None:
        if versionNo < len(self._versions):
            return self._versions[versionNo]
        return None

    def reset_to_version(self, versionNo: int = 0) -> bool:
        reset_version = self.get_version(versionNo)
        if reset_version is None:
            return False
        self._text = reset_version.text
        self._font = reset_version.font
        self._width = reset_version.width
        self._height = reset_version.height
        self._foreground_color = reset_version.foreground_color
        self._background_color = reset_version.background_color
        self._versions = reset_version.version_stack
        self._rendered_image = reset_version._rendered_image
        self._display_map = reset_version._display_map
        self._has_transparency = reset_version._has_transparency
        return True    

    def reset_to_original_version(self) -> bool:
        return self.reset_to_version()


    def resize_item(self, size: Size) -> Item:
        if self.is_equal(size):
            return self
        new_font = self._font.find_best_fit(self._text, size)
        result = TextItem(
            self._text,
            new_font,
            self._foreground_color,
            self._background_color,
            self.all_versions(),
            self._has_transparency
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
            self.all_versions(),
            self._has_transparency
        )

    def copy_item(self) -> Item:
        return TextItem(
            self._text,
            self._font,
            self._foreground_color,
            self._background_color,
            self._has_transparency
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
        return self._font.to_image(
            self._text,
            self._foreground_color,
            self._background_color,
            rotated_degrees,
            size,
            logger,
            as_watermark
        )

    def show(self, title: str | None = None) -> None:
        self.to_image().show(title)

    def to_csv_row(self) -> Dict[str, Any]:
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
            TEXT_FOREGROUND_COLOR: self._foreground_color.name,
            TEXT_BACKGROUND_COLOR: self._background_color.name if self._background_color is not None else ''
        }

    def write_row(self, name: str, directory: str, row: Dict[str, Any]) -> str:
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
            get_value_or_default(TEXT_LAYOUT, row, None, int),
            get_value_or_default(TEXT_STROKE_WIDTH, row, None, int),
            get_value_or_default(TEXT_ANCHOR, row, None),
            get_value_or_default(TEXT_ALIGN, row, None)
        )
        fg_color = get_value_or_default(
            TEXT_FOREGROUND_COLOR,
            row,
            None,
            lambda v: pick_color(ColorSource.NAME) if v.lower().strip() == 'random' else NamedColor(v)
        )
        bg_color = get_value_or_default(
            TEXT_BACKGROUND_COLOR,
            row,
            None,
            lambda v: pick_color(ColorSource.NAME) if v.lower().strip() == 'random' else NamedColor(v)
        )
        
        result = TextItem(
            row[TEXT_TEXT],
            Font(font_name, font_size, text_attributes),
            fg_color,
            bg_color
        )
        if field_exists(TEXT_FONT_SIZE, row):
            result.font.font_size = float(row[TEXT_FONT_SIZE])
            text_box = result.font.to_box(result.text)
            result.width = text_box.width
            result.height = text_box.height
            result.reset_display_map()     

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