import csv
from PIL import Image
from typing import Dict, Any
from itemcloud.containers.named_item import NamedItem
from itemcloud.util.parsers import (to_unused_filepath, is_empty)
from itemcloud.size import Size
from itemcloud.util.colors import (Color, NamedColor, pick_color, ColorSource)
from textcloud.util.fonts import (Font, FontName, FontSize, pick_font, pick_font_size)
from textcloud.util.font_categories import (FontTypeCategories, FontUsageCategory)


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

    def update_named_text(self, other) -> None:
        self.text = other.text
        self.font = other.font
        self.foreground_color = other.foreground_color
        self.background_color = other.background_color
        self.width = other.width
        self.height = other.height
    
    def to_image(self) -> Image.Image:
        return self.font.to_image(
            self.text,
            self.foreground_color,
            self.background_color
        )

    def write_item(self, item_name: str, layout_directory: str) -> str:
        csv_filepath = to_unused_filepath(layout_directory, item_name, 'csv')
        with open(csv_filepath, 'w') as file:
            csv_writer = csv.DictWriter(file, fieldnames=TEXT_HEADERS)
            csv_writer.writeheader()
            csv_writer.writerow({
                TEXT_NAME: self.name,
                TEXT_TEXT: self.text,
                TEXT_FONT_NAME_PATH: self.font.font_name,
                TEXT_MIN_FONT_SIZE: self.font.min_font_size,
                TEXT_FONT_SIZE: self.font.font_size,
                TEXT_MAX_FONT_SIZE: self.font.max_font_size,
                TEXT_FOREGROUND_COLOR: self.foreground_color.name,
                TEXT_BACKGROUND_COLOR: self.background_color.name if self.background_color is not None else ''
            })
        return csv_filepath

    def load(row: Dict[str, Any]) -> "NamedText":
        if is_empty(row[TEXT_FONT_NAME_PATH]) or row[TEXT_FONT_NAME_PATH].lower().strip() == 'random':
            font_name = pick_font()
        else:
            font_name = FontName(row[TEXT_FONT_NAME_PATH], FontTypeCategories.CUSTOM)
        if is_empty(row[TEXT_MIN_FONT_SIZE]) or row[TEXT_MIN_FONT_SIZE].lower().strip() == 'random' or is_empty(row[TEXT_MAX_FONT_SIZE]) or row[TEXT_MAX_FONT_SIZE].lower().strip() == 'random' :
            font_size = pick_font_size()
            if not(is_empty(row[TEXT_MIN_FONT_SIZE])) and row[TEXT_MIN_FONT_SIZE].lower().strip() != 'random':
                font_size = FontSize(FontUsageCategory.CUSTOM, float(row[TEXT_MIN_FONT_SIZE]), font_size.max)
            if not(is_empty(row[TEXT_MAX_FONT_SIZE])) and row[TEXT_MAX_FONT_SIZE].lower().strip() != 'random':
                font_size = FontSize(FontUsageCategory.CUSTOM, font_size.min, float(row[TEXT_MAX_FONT_SIZE]))
        else:
            font_size = FontSize(FontUsageCategory.CUSTOM, float(row[TEXT_MIN_FONT_SIZE]), float(row[TEXT_MAX_FONT_SIZE]))

        if is_empty(row[TEXT_FOREGROUND_COLOR]):
            fg_color = None
        elif row[TEXT_FOREGROUND_COLOR].lower().strip() == 'random':
            fg_color = pick_color(ColorSource.NAME)
        else:
            fg_color = NamedColor(row[TEXT_FOREGROUND_COLOR])
        
        if is_empty(row[TEXT_BACKGROUND_COLOR]):
            bg_color = None
        elif row[TEXT_BACKGROUND_COLOR].lower().strip() == 'random':
            bg_color = pick_color(ColorSource.NAME)
        else:
            bg_color = NamedColor(row[TEXT_BACKGROUND_COLOR])
        result = NamedText(
            row[TEXT_NAME],
            row[TEXT_TEXT],
            Font(font_name, font_size),
            fg_color,
            bg_color
        )
        if TEXT_FONT_SIZE in row and not(is_empty(row[TEXT_FONT_SIZE])):
            result.font.font_size = float(row[TEXT_FONT_SIZE])
            text_box = result.font.to_box(result.text)
            result.width = text_box.width
            result.height = text_box.height
        return result

    @staticmethod
    def load_item(item_filepath: str) -> "NamedText":
        with open(item_filepath, 'r') as file:
            csv_reader = csv.DictReader(file, fieldnames=TEXT_HEADERS)
            next(csv_reader)
            for row in csv_reader:
                return NamedText.load(row)

def resize_named_text(named_text: NamedText, size: Size) -> NamedText:
    if named_text.is_equal(size):
            return named_text
    new_font = named_text.font.find_best_fit(named_text.text, size)
    result = NamedText(
         named_text.name,
         named_text.text,
         new_font,
         named_text.foreground_color,
         named_text.background_color
    )
    text_box = new_font.to_box(named_text.text)
    result.width = text_box.width
    result.height = text_box.height
    return result

TEXT_NAME = 'name'
TEXT_TEXT = 'text'
TEXT_FONT_NAME_PATH = 'font_name_path'
TEXT_MIN_FONT_SIZE = 'min_font_size'
TEXT_FONT_SIZE = 'font_size'
TEXT_MAX_FONT_SIZE = 'max_font_size'
TEXT_FOREGROUND_COLOR = 'foreground_color'
TEXT_BACKGROUND_COLOR = 'background_color'

TEXT_HEADERS = [
    TEXT_NAME,
    TEXT_TEXT,
    TEXT_FONT_NAME_PATH,
    TEXT_MIN_FONT_SIZE,
    TEXT_FONT_SIZE,
    TEXT_MAX_FONT_SIZE,
    TEXT_FOREGROUND_COLOR,
    TEXT_BACKGROUND_COLOR
]