import csv
from typing import Dict, Any
from itemcloud.containers.weighted_item import WeightedItem
from itemcloud.containers.named_image import (NamedImage, IMAGE_FILEPATH)
from itemcloud.layout.layout_item import LayoutItem
from itemcloud.box import Box
from itemcloud.size import Size
from imagecloud.layout.layout_image import LayoutImage
from itemcloud.util.parsers import (validate_row)

class WeightedImage(WeightedItem, NamedImage):
    
    def __init__(self, weight: float, namedImage: NamedImage) -> None:
        NamedImage.__init__(self, namedImage.image, namedImage.name, namedImage._original_image)
        WeightedItem.__init__(self, weight, self.name, self._image.width, self._image.height)

    def to_layout_item(
        self,
        placement_box: Box,
        rotated_degrees: int,
        reservation_box: Box,        
        reservation_no: int,
        latency_str: str
    ) -> LayoutItem:
        item =  LayoutImage(
            self.name,
            placement_box,
            rotated_degrees,
            reservation_box,
            reservation_no,
            latency_str
        )
        item._original_image = NamedImage(self.image, self.name, self._original_image)
        return item
        
    
    def to_fitted_weighted_item(
        self,
        weight: float, 
        width: int,
        height: int
    ) -> "WeightedItem":
        return WeightedImage(
            weight,
            self.resize(Size(width, height))
        )        
        
    @staticmethod
    def load(row: Dict[str, Any]) -> "WeightedImage":
        validate_row(row, [WEIGHTED_IMAGE_WEIGHT])
        return WeightedImage(
            float(row[WEIGHTED_IMAGE_WEIGHT]),
            NamedImage.load(row)
        )

WEIGHTED_IMAGE_WEIGHT = 'weight'
WEIGHTED_IMAGE_WEIGHT_HELP = '<float>'

WEIGHTED_IMAGE_IMAGE_FILEPATH = IMAGE_FILEPATH
WEIGHTED_IMAGE_IMAGE_FILEPATH_HELP = '<image-filepath>'

WEIGHTED_IMAGE_HEADERS = [
    WEIGHTED_IMAGE_WEIGHT,
    WEIGHTED_IMAGE_IMAGE_FILEPATH
]
WEIGHTED_IMAGE_HEADERS_HELP = [
    WEIGHTED_IMAGE_WEIGHT_HELP,
    WEIGHTED_IMAGE_IMAGE_FILEPATH_HELP
]

WEIGHTED_IMAGES_CSV_FILE_HELP = '''csv file for weighted images with following format:
"{0}"
{1}
'''.format('","'.join(WEIGHTED_IMAGE_HEADERS), ','.join(WEIGHTED_IMAGE_HEADERS_HELP))

def load_weighted_images(csv_filepath: str) -> list[WeightedImage]:
    try:
        result: list[WeightedImage] = list()
        with open(csv_filepath, 'r', encoding='utf-8-sig') as file:    
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                result.append(WeightedImage.load(row))
        return result
    except Exception as e:
        raise Exception(str(e))
