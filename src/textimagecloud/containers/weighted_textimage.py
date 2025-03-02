import csv
from typing import (Dict, Any)
from textimagecloud.containers.named_textimage import (NamedTextImage, TEXT_TRANSPARENCY_PERCENT)
from itemcloud.containers.weighted_item import WeightedItem
from itemcloud.layout.layout_item import LayoutItem
from itemcloud.box import Box
from itemcloud.size import Size
from textimagecloud.layout.layout_textimage import LayoutTextImage
from itemcloud.util.parsers import validate_row
from textcloud.containers.weighted_text import (WEIGHTED_TEXT_WEIGHT, WEIGHTED_TEXT_HEADERS, WEIGHTED_TEXT_HEADERS_HELP)
from imagecloud.containers.weighted_image import (WEIGHTED_IMAGE_IMAGE_FILEPATH, WEIGHTED_IMAGE_IMAGE_FILEPATH_HELP)


class WeightedTextImage(WeightedItem, NamedTextImage):

    def __init__(
        self,
        weight: float,
        namedTextImage: NamedTextImage
    ) -> None:
        NamedTextImage.__init__(self, namedTextImage.name, namedTextImage._text, namedTextImage._image, namedTextImage._watermark_transparency)
        WeightedItem.__init__(self, weight, self.name, self.width, self.height)

    def to_layout_item(
        self,
        placement_box: Box,
        rotated_degrees: int,
        reservation_box: Box,        
        reservation_no: int,
        latency_str: str
    ) -> LayoutItem:
        item =  LayoutTextImage(
            self.name,
            placement_box,
            rotated_degrees,
            reservation_box,
            reservation_no,
            latency_str
        )
        item._original_textimage = self.copy_named_textimage()
        return item

    def to_fitted_weighted_item(
        self,
        weight: float,
        width: int,
        height: int
    ) -> "WeightedItem":
        return WeightedTextImage(
            weight,
            self.resize(Size(width, height))
        )

    @staticmethod
    def load(row: Dict[str, Any]) -> "WeightedTextImage":
        validate_row(row, [WEIGHTED_TEXT_WEIGHT])
        return WeightedTextImage(
            float(row[WEIGHTED_TEXT_WEIGHT]),
            NamedTextImage.load(row)
        )

WEIGHTED_TEXT_IMAGE_HEADERS = [
    *WEIGHTED_TEXT_HEADERS,
    TEXT_TRANSPARENCY_PERCENT,
    WEIGHTED_IMAGE_IMAGE_FILEPATH
]

WEIGHTED_TEXT_IMAGE_HEADERS_HELP = [
    *WEIGHTED_TEXT_HEADERS_HELP,
    '<float>',
    WEIGHTED_IMAGE_IMAGE_FILEPATH_HELP
]

WEIGHTED_TEXT_IMAGE_CSV_FILE_HELP = '''csv file for weighted text-images with following format:
"{0}"
{1}
'''.format('","'.join(WEIGHTED_TEXT_IMAGE_HEADERS), ','.join(WEIGHTED_TEXT_IMAGE_HEADERS_HELP))

def load_weighted_text_images(csv_filepath: str) -> list[WeightedTextImage]:
    try:
        result: list[WeightedTextImage] = list()
        with open(csv_filepath, 'r', encoding='utf-8-sig') as file:    
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                result.append(WeightedTextImage.load(row))
        return result
    except Exception as e:
        raise Exception(str(e))
