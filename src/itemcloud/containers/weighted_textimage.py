from __future__ import annotations
from itemcloud.containers.base.textimage_item import TEXT_TRANSPARENCY_PERCENT
from itemcloud.containers.named_textimage import NamedTextImage
from itemcloud.containers.base.weighted_item import WeightedItem
from itemcloud.containers.weighted_text import (WEIGHTED_TEXT_HEADERS, WEIGHTED_TEXT_HEADERS_HELP)
from itemcloud.containers.weighted_image import (WEIGHTED_IMAGE_IMAGE_FILEPATH, WEIGHTED_IMAGE_IMAGE_FILEPATH_HELP)


class WeightedTextImage(WeightedItem, NamedTextImage):

    def __init__(
        self,
        weight: float,
        namedTextImage: NamedTextImage
    ) -> None:
        NamedTextImage.__init__(self, namedTextImage.name, namedTextImage.item)
        WeightedItem.__init__(self, weight, namedTextImage.name, namedTextImage.item)

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
