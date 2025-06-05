from __future__ import annotations
from itemcloud.containers.base.weighted_item import WeightedItem, ITEM_WEIGHT
from itemcloud.containers.named_image import (NamedImage, IMAGE_FILEPATH)

class WeightedImage(WeightedItem, NamedImage):
    
    def __init__(self, weight: float, namedImage: NamedImage) -> None:
        NamedImage.__init__(self, namedImage.image, namedImage.name, namedImage._original_image)
        WeightedItem.__init__(self, weight, self.name, self._image.width, self._image.height)
        

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
