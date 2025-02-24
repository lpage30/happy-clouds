import csv
from PIL import Image, ImageColor, ImageDraw, ImageFont
from itemcloud.containers.named_item import NamedItem
from itemcloud.util.parsers import (to_unused_filepath, is_empty)
from itemcloud.size import Size
from itemcloud.box import Box

class NamedText(NamedItem):

    def __init__(
        self,
        name: str,
        text: str,
        font_name_path: str,
        min_font_size: float,
        max_font_size: float,
        foreground_color: str | None,
        background_color: str | None
    ) -> None:
        super().__init__(name, 0,0)
        self.text = text
        self.font_name_path = font_name_path
        self.min_font_size = min_font_size
        self.max_font_size = max_font_size
        self.foreground_color = foreground_color
        self.background_color = background_color
        self.font_size: float = min_font_size + (max_font_size - min_font_size)/2
        self.font, self.box = load_text_box(self.text, self.font_name_path, self.font_size)
        self.width = self.box.width
        self.height = self.box.height

    def update_named_text(self, other) -> None:
        self.text = other.text
        self.font_name_path = other.font_name_path
        self.min_font_size = other.min_font_size
        self.max_font_size = other.max_font_size
        self.foreground_color = other.foreground_color
        self.background_color = other.background_color
        self.font_size = other.font_size
        self.font = other.font
        self.box = other.box
        self.width = other.box.width
        self.height = other.box.height
    
    def to_image(self) -> Image.Image:
        if self.background_color is not None:
            bg_color = ImageColor.getcolor(self.background_color)
            result = Image.new("RGB", (self.width, self.height), bg_color)
        else:
            result = Image.new("RGBA", (self.width, self.height))
        draw = ImageDraw.Draw(result)
        if self.foreground_color is not None:
            fg_color = ImageColor.getcolor(self.foreground_color)
            if '\n' in self.text:
                draw.multiline_text((0, 0), self.text, fill=fg_color, font=self.font, anchor="mm")
            else:
                draw.text((0, 0), self.text, fill=fg_color, font=self.font, anchor="mm")
        else:
            if '\n' in self.text:
                draw.multiline_text((0, 0), self.text, font=self.font, anchor="mm")
            else:
                draw.text((0, 0), self.text, font=self.font, anchor="mm")
        return result

    def write_item(self, item_name: str, layout_directory: str) -> str:
        csv_filepath = to_unused_filepath(layout_directory, item_name, '.csv')
        with open(csv_filepath, 'w') as file:
            csv_writer = csv.DictWriter(file, fieldnames=TEXT_HEADERS)
            csv_writer.writeheader()
            csv_writer.writerow({
                TEXT_NAME: self.name,
                TEXT_TEXT: self.text,
                TEXT_FONT_NAME_PATH: self.font_name_path,
                TEXT_MIN_FONT_SIZE: self.min_font_size,
                TEXT_FONT_SIZE: self.font_size,
                TEXT_MAX_FONT_SIZE: self.max_font_size,
                TEXT_FOREGROUND_COLOR: self.foreground_color,
                TEXT_BACKGROUND_COLOR: self.background_color
            })
        return csv_filepath

    @staticmethod
    def load_item(item_filepath: str) -> "NamedText":
        with open(item_filepath, 'r') as file:
            csv_reader = csv.DictReader(file, fieldnames=TEXT_HEADERS)
            next(csv_reader)
            for row in csv_reader:
                result = NamedText(
                    row[TEXT_NAME],
                    row[TEXT_TEXT],
                    row[TEXT_FONT_NAME_PATH],
                    float(row[TEXT_MIN_FONT_SIZE]),
                    float(row[TEXT_MAX_FONT_SIZE]),
                    None if is_empty(row[TEXT_FOREGROUND_COLOR]) else row[TEXT_FOREGROUND_COLOR],
                    None if is_empty(row[TEXT_BACKGROUND_COLOR]) else row[TEXT_BACKGROUND_COLOR]
                )
                result.font_size = float(row[TEXT_FONT_SIZE])
                result.font, result.box = load_text_box(result.text, result.font_name_path, result.font_size)
                result.width = result.box.width
                result.height = result.box.height
                return result

def resize_named_text(named_text: NamedText, size: Size) -> NamedText:
    if named_text.is_equal(size):
            return named_text
    increment = 1 if named_text.is_less_than(size) else -1
    font = named_text.font
    box = named_text.box
    font_size = named_text.font_size
    while True:
        new_font_size = font_size + increment
        new_font, new_box = load_text_box(named_text.text, named_text.font_name_path, new_font_size)
        if (0 < increment and new_box.size.is_less_than(size)) or (increment < 0 and size.is_less_than(new_box.size)):
            font_size = new_font_size
            font = new_font
            box = new_box
        else:
            break
    result = NamedText(
         named_text.name,
         named_text.text,
         named_text.font_name_path,
         named_text.min_font_size,
         named_text.max_font_size,
         named_text.foreground_color,
         named_text.background_color)
    
    result.font_size = font_size
    result.font = font
    result.box = box
    result.width = result.box.width
    result.height = result.box.height
    return result

def load_text_box(text: str, font_name_path: str, font_size: float) -> tuple[ImageFont.FreeTypeFont, Box]:
    font = ImageFont.truetype(font_name_path, font_size)
    text_bbox = font.getbbox(text)
    return (
        font,
        Box(int(text_bbox[0]), int(text_bbox[1]), int(text_bbox[2]), int(text_bbox[3]))
    )

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