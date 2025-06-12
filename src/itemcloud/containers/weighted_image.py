from __future__ import annotations
from itemcloud.containers.base.item_types import (
    IMAGE_FILEPATH,
    ITEM_WEIGHT
)
from itemcloud.containers.base.weighted_item import WeightedItem
from itemcloud.containers.named_image import NamedImage

class WeightedImage(WeightedItem, NamedImage):
    
    def __init__(self, weight: float, namedImage: NamedImage) -> None:
        NamedImage.__init__(self, namedImage.item, namedImage.name)
        WeightedItem.__init__(self, weight, namedImage.name, namedImage.item)
        

WEIGHTED_IMAGE_WEIGHT = ITEM_WEIGHT
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

WEIGHTED_IMAGE_CSV_FILE_HELP = '''csv file for weighted images with following format:
"{0}"
{1}
'''.format('","'.join(WEIGHTED_IMAGE_HEADERS), ','.join(WEIGHTED_IMAGE_HEADERS_HELP))
