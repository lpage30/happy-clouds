from __future__ import annotations
from typing import Dict, Any, List
from itemcloud.containers.named_text import (
    NamedText
)
from itemcloud.containers.base.text_item import (
    TEXT_TEXT,
    TEXT_FONT_NAME_PATH,
    TEXT_MIN_FONT_SIZE,
    TEXT_MAX_FONT_SIZE,
    TEXT_FOREGROUND_COLOR,
    TEXT_BACKGROUND_COLOR,
    TEXT_LAYOUT,
    TEXT_STROKE_WIDTH,
    TEXT_ANCHOR,
    TEXT_ALIGN,
)
from itemcloud.containers.base.named_item import ITEM_NAME
from itemcloud.containers.base.weighted_item import WeightedItem, ITEM_WEIGHT
from itemcloud.size import Size
from itemcloud.util.parsers import validate_row

class WeightedText(WeightedItem, NamedText):
    
    def __init__(
        self, 
        weight: float,
        namedText: NamedText
    ) -> None:
        NamedText.__init__(self, namedText.name, namedText.text, namedText.font, namedText.foreground_color, namedText.background_color)
        WeightedItem.__init__(self, weight, self.name, self.width, self.height)
        

WEIGHTED_TEXT_NAME = ITEM_NAME
WEIGHTED_TEXT_NAME_HELP = '<name>'
WEIGHTED_TEXT_WEIGHT = ITEM_WEIGHT
WEIGHTED_TEXT_WEIGHT_HELP = '<float>'
WEIGHTED_TEXT_TEXT = TEXT_TEXT
WEIGHTED_TEXT_TEXT_HELP = 'text|phrase|prose'
WEIGHTED_TEXT_FONT_NAME_PATH = TEXT_FONT_NAME_PATH
WEIGHTED_TEXT_FONT_NAME_PATH_HELP = '<path-to-your-font>|<name-of-font>|empty(random)'
WEIGHTED_TEXT_MIN_FONT_SIZE = TEXT_MIN_FONT_SIZE
WEIGHTED_TEXT_MIN_FONT_SIZE_HELP = '<float>|empty(random)'
WEIGHTED_TEXT_MAX_FONT_SIZE = TEXT_MAX_FONT_SIZE
WEIGHTED_TEXT_MAX_FONT_SIZE_HELP = '<float>|empty(random)'
WEIGHTED_TEXT_LAYOUT = TEXT_LAYOUT
WEIGHTED_TEXT_LAYOUT_HELP = 'empty(0)|0(BASIC)|1(RAQM)'
WEIGHTED_TEXT_STROKE_WIDTH = TEXT_STROKE_WIDTH
WEIGHTED_TEXT_STROKE_WIDTH_HELP = 'empty|<integer>'
WEIGHTED_TEXT_ANCHOR = TEXT_ANCHOR
# https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html
WEIGHTED_TEXT_ANCHOR_HELP = 'empty(ma)|<l|m|r><t|m|b|a>'
WEIGHTED_TEXT_ALIGN = TEXT_ALIGN
WEIGHTED_TEXT_ALIGN_HELP = 'empty(center)|center|right|left'
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
    WEIGHTED_TEXT_LAYOUT,
    WEIGHTED_TEXT_STROKE_WIDTH,
    WEIGHTED_TEXT_ANCHOR,
    WEIGHTED_TEXT_ALIGN,
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
    WEIGHTED_TEXT_LAYOUT_HELP,
    WEIGHTED_TEXT_STROKE_WIDTH_HELP,
    WEIGHTED_TEXT_ANCHOR_HELP,
    WEIGHTED_TEXT_ALIGN_HELP,
    WEIGHTED_TEXT_FOREGROUND_COLOR_HELP,
    WEIGHTED_TEXT_BACKGROUND_COLOR_HELP,
]
WEIGHTED_TEXT_CSV_FILE_HELP = '''csv file for weighted text with following format:
"{0}"
{1}
'''.format('","'.join(WEIGHTED_TEXT_HEADERS), ','.join(WEIGHTED_TEXT_HEADERS_HELP))

def load_weighted_texts(csv_filepath: str) -> list[WeightedText]:
    try:
        result: List[WeightedText] = list()
        with open(csv_filepath, 'r', encoding='utf-8-sig') as file:    
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                result.append(WeightedText.load(row))
        return result
    except Exception as e:
        raise Exception(str(e))
