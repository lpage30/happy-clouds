import csv
from typing import Dict, Any, List
from textcloud.containers.named_text import (
    NamedText,
    resize_named_text,
    TEXT_NAME,
    TEXT_TEXT,
    TEXT_FONT_NAME_PATH,
    TEXT_MIN_FONT_SIZE,
    TEXT_MAX_FONT_SIZE,
    TEXT_FOREGROUND_COLOR,
    TEXT_BACKGROUND_COLOR
)
from itemcloud.containers.weighted_item import WeightedItem
from itemcloud.layout.layout_item import LayoutItem
from itemcloud.box import Box
from itemcloud.size import Size
from textcloud.layout.layout_text import LayoutText
from itemcloud.util.colors import Color
from textcloud.util.fonts import Font

class WeightedText(WeightedItem, NamedText):
    
    def __init__(
        self, 
        weight: float,
        name: str,
        text: str,
        font: Font,
        foreground_color: Color,
        background_color: Color | None
    ) -> None:
        NamedText.__init__(self, name, text, font, foreground_color, background_color)
        WeightedItem.__init__(self, weight, name, self.width, self.height)
        
    def to_layout_item(
        self,
        placement_box: Box,
        rotated_degrees: int,
        reservation_box: Box,        
        reservation_no: int,
        latency_str: str
    ) -> LayoutItem:
        named_text: NamedText = self
        item =  LayoutText(
            self.name,
            placement_box,
            rotated_degrees,
            reservation_box,
            reservation_no,
            latency_str
        )
        item._original_text = named_text
        return item
        
    
    def to_fitted_weighted_item(self, weight: float, width: int, height: int) -> "WeightedItem":
        new_named_text = resize_named_text(self, Size(width, height))
        result = WeightedText(
            weight,
            self.name,
            self.text,
            self.font,
            self.foreground_color,
            self.background_color
        )
        result.update_named_text(new_named_text)
        return result
    
    @staticmethod
    def load(row: Dict[str, Any]) -> "WeightedText":
        named_text = NamedText.load(row)
        result = WeightedText(
            float(row[WEIGHTED_TEXT_WEIGHT]),
            row[WEIGHTED_TEXT_NAME],
            named_text.text,
            named_text.font,
            named_text.foreground_color,
            named_text.background_color
        )
        result.update_named_text(named_text)
        return result

WEIGHTED_TEXT_NAME = TEXT_NAME
WEIGHTED_TEXT_NAME_HELP = '<name>'
WEIGHTED_TEXT_WEIGHT = 'weight'
WEIGHTED_TEXT_WEIGHT_HELP = '<float>'
WEIGHTED_TEXT_TEXT = TEXT_TEXT
WEIGHTED_TEXT_TEXT_HELP = 'text|phrase|prose'
WEIGHTED_TEXT_FONT_NAME_PATH = TEXT_FONT_NAME_PATH
WEIGHTED_TEXT_FONT_NAME_PATH_HELP = '<path-to-your-font>|<name-of-font>|empty(random)'
WEIGHTED_TEXT_MIN_FONT_SIZE = TEXT_MIN_FONT_SIZE
WEIGHTED_TEXT_MIN_FONT_SIZE_HELP = '<float>|empty(random)'
WEIGHTED_TEXT_MAX_FONT_SIZE = TEXT_MAX_FONT_SIZE
WEIGHTED_TEXT_MAX_FONT_SIZE_HELP = '<float>|empty(random)'
WEIGHTED_TEXT_FOREGROUND_COLOR = TEXT_FOREGROUND_COLOR
WEIGHTED_TEXT_FOREGROUND_COLOR_HELP = '<color-name>|#RRGGBB|empty|random'
WEIGHTED_TEXT_BACKGROUND_COLOR = TEXT_BACKGROUND_COLOR
WEIGHTED_TEXT_BACKGROUND_COLOR_HELP = '<color-name>|#RRGGBB|empty|random'
WEIGHTED_TEXT_HEADERS = [
    WEIGHTED_TEXT_NAME,
    WEIGHTED_TEXT_TEXT,
    WEIGHTED_TEXT_WEIGHT,
    WEIGHTED_TEXT_FONT_NAME_PATH,
    WEIGHTED_TEXT_MIN_FONT_SIZE,
    WEIGHTED_TEXT_MAX_FONT_SIZE,
    WEIGHTED_TEXT_FOREGROUND_COLOR,
    WEIGHTED_TEXT_BACKGROUND_COLOR
]
WEIGHTED_TEXT_HEADERS_HELP = [
    WEIGHTED_TEXT_NAME_HELP,
    WEIGHTED_TEXT_TEXT_HELP,
    WEIGHTED_TEXT_WEIGHT_HELP,
    WEIGHTED_TEXT_FONT_NAME_PATH_HELP,
    WEIGHTED_TEXT_MIN_FONT_SIZE_HELP,
    WEIGHTED_TEXT_MAX_FONT_SIZE_HELP,
    WEIGHTED_TEXT_FOREGROUND_COLOR_HELP,
    WEIGHTED_TEXT_BACKGROUND_COLOR_HELP,
]
WEIGHTED_TEXTS_CSV_FILE_HELP = '''csv file for weighted text with following format:
"{0}"
{1}
'''.format('","'.join(WEIGHTED_TEXT_HEADERS), ','.join(WEIGHTED_TEXT_HEADERS_HELP))

def load_weighted_texts(csv_filepath: str) -> list[WeightedText]:
    try:
        result: List[WeightedText] = list()
        with open(csv_filepath, 'r') as file:    
            csv_reader = csv.DictReader(file, fieldnames=WEIGHTED_TEXT_HEADERS)
            next(csv_reader)
            for row in csv_reader:
                result.append(WeightedText.load(row))
        return result
    except Exception as e:
        raise Exception(str(e))
