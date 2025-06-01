import csv
from typing import Dict, Any
from itemcloud.image_item import ImageItem
from itemcloud.containers.base.named_item import NamedItem
from itemcloud.util.parsers import (
    to_unused_filepath,
    get_value_or_default,
    get_complex_value_or_default,
    validate_row,
    field_exists
)
from itemcloud.size import Size
from itemcloud.util.colors import (Color, NamedColor, pick_color, ColorSource)
from itemcloud.util.fonts import (Font, FontName, FontSize, FontTextAttributes,pick_font, pick_font_size)
from itemcloud.util.font_categories import (FontTypeCategories, FontUsageCategory)
from itemcloud.logger.base_logger import BaseLogger


class NamedText(NamedItem):

    def __init__(
        self,
        name: str,
        text: str,
        font: Font,
        foreground_color: Color | None,
        background_color: Color | None
    ) -> None:
        super().__init__(name, 0,0)
        self.text = text
        self.font = font
        box_size = self.font.to_box(text)
        self.width = box_size.width
        self.height = box_size.height
        self.foreground_color = foreground_color
        self.background_color = background_color

    def copy_named_text(self) -> "NamedText":
        return NamedText(
            self.name,
            self.text,
            self.font,
            self.foreground_color,
            self.background_color
        )

    def resize(self, size: Size) -> "NamedText":
        if self.is_equal(size):
            return self
        new_font = self.font.find_best_fit(self.text, size)
        result = NamedText(
            self.name,
            self.text,
            new_font,
            self.foreground_color,
            self.background_color
        )
        text_box = new_font.to_box(self.text)
        result.width = text_box.width
        result.height = text_box.height
        return result    

    def draw_on_image(
        self,
        image: ImageItem,
        rotated_degrees: int | None = None,
        size: Size | None = None,
        logger: BaseLogger | None = None,
        as_watermark: bool = False,
        xy: tuple[float, float] | None = None,
    ) -> ImageItem:
        return self.font.draw_on_image(
            self.text,
            image,
            self.foreground_color,
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
        return self.font.to_image(
            self.text,
            self.foreground_color,
            self.background_color,
            rotated_degrees,
            size,
            logger,
            as_watermark
        )
    
    def to_csv_row(self) -> Dict[str, Any]:
        return {
            TEXT_NAME: self.name,
            TEXT_TEXT: self.text,
            TEXT_FONT_NAME_PATH: self.font.font_name,
            TEXT_MIN_FONT_SIZE: self.font.min_font_size,
            TEXT_FONT_SIZE: self.font.font_size,
            TEXT_MAX_FONT_SIZE: self.font.max_font_size,
            TEXT_LAYOUT: self.font.layout,
            TEXT_STROKE_WIDTH: self.font.stroke_width if not None else '',
            TEXT_ANCHOR: self.font.anchor,
            TEXT_ALIGN: self.font.align,
            TEXT_FOREGROUND_COLOR: self.foreground_color.name,
            TEXT_BACKGROUND_COLOR: self.background_color.name if self.background_color is not None else ''
        }

    def write_row(self, item_name: str, layout_directory: str, row: Dict[str, Any]) -> str:
        csv_filepath = to_unused_filepath(layout_directory, item_name, 'csv')
        with open(csv_filepath, 'w') as file:
            csv_writer = csv.DictWriter(file, fieldnames=list(row.keys()))
            csv_writer.writeheader()
            csv_writer.writerow(row)
        return csv_filepath        

    def write_item(self, item_name: str, layout_directory: str) -> str:
        return self.write_row(item_name, layout_directory, self.to_csv_row())

    @staticmethod
    def load_item(item_filepath: str) -> "NamedText":
        with open(item_filepath, 'r', encoding='utf-8-sig') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                return NamedText.load(row)

    @staticmethod
    def load(row: Dict[str, Any]) -> "NamedText":
        validate_row(row, [TEXT_NAME, TEXT_TEXT])

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
        
        result = NamedText(
            row[TEXT_NAME],
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

        return result


TEXT_NAME = 'name'
TEXT_TEXT = 'text'
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

TEXT_HEADERS = [
    TEXT_NAME,
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