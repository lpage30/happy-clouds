import csv
from itemcloud.containers.weighted_item import WeightedItem
from imagecloud.containers.weighted_image import (
    WEIGHTED_IMAGE_HEADERS,
    WEIGHTED_IMAGE_HEADERS_HELP,
    WEIGHTED_IMAGE_IMAGE_FILEPATH,
    WeightedImage
)
from textcloud.containers.weighted_text import (
    WEIGHTED_TEXT_HEADERS,
    WEIGHTED_TEXT_HEADERS_HELP,
    WEIGHTED_TEXT_TEXT,
    WeightedText
)
from textimagecloud.containers.weighted_textimage import (
    WEIGHTED_TEXT_IMAGE_HEADERS,
    WEIGHTED_TEXT_IMAGE_HEADERS_HELP,
    WeightedTextImage
)
from itemcloud.util.parsers import (field_exists)

def load_weighted_items(csv_filepath: str) -> list[WeightedItem]:
    try:
        result: list[WeightedItem] = list()
        with open(csv_filepath, 'r', encoding='utf-8-sig') as file:    
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                item: WeightedItem
                if field_exists(WEIGHTED_TEXT_TEXT, row) and field_exists(WEIGHTED_IMAGE_IMAGE_FILEPATH, row):
                    item = WeightedTextImage.load(row)
                elif field_exists(WEIGHTED_TEXT_TEXT, row):
                    item = WeightedText.load(row)
                elif field_exists(WEIGHTED_IMAGE_IMAGE_FILEPATH, row):
                    item = WeightedImage.load(row)
                else:
                    raise ValueError('Unable to resolve row to a Weighted Type {0}'.format(row.__str__()))
                result.append(item)
        return result
    except Exception as e:
        raise Exception(str(e))



ITEM_IMPORT_FIELD_HELP_MAP = dict(
    zip(
        [
            *WEIGHTED_IMAGE_HEADERS,
            *WEIGHTED_TEXT_HEADERS,
            *WEIGHTED_TEXT_IMAGE_HEADERS
        ],
        [
            *WEIGHTED_IMAGE_HEADERS_HELP,
            *WEIGHTED_TEXT_HEADERS_HELP,
            *WEIGHTED_TEXT_IMAGE_HEADERS_HELP
        ]
    )
)

WEIGHTED_ITEM_HEADERS = list(ITEM_IMPORT_FIELD_HELP_MAP.keys())
WEIGHTED_ITEM_HEADERS_HELP = list(ITEM_IMPORT_FIELD_HELP_MAP.values())
WEIGHTED_ITEM_CSV_FILE_HELP = '''csv file for weighted items: images/text/text-images with following format:
"{0}"
{1}
'''.format('","'.join(WEIGHTED_ITEM_HEADERS), ','.join(WEIGHTED_ITEM_HEADERS_HELP))