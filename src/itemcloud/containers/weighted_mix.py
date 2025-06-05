from itemcloud.containers.weighted_image import (
    WEIGHTED_IMAGE_HEADERS,
    WEIGHTED_IMAGE_HEADERS_HELP
)
from itemcloud.containers.weighted_text import (
    WEIGHTED_TEXT_HEADERS,
    WEIGHTED_TEXT_HEADERS_HELP,
)
from itemcloud.containers.weighted_textimage import (
    WEIGHTED_TEXT_IMAGE_HEADERS,
    WEIGHTED_TEXT_IMAGE_HEADERS_HELP,
)

MIX_IMPORT_FIELD_HELP_MAP = dict(
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

WEIGHTED_MIX_HEADERS = list(MIX_IMPORT_FIELD_HELP_MAP.keys())
WEIGHTED_MIX_HEADERS_HELP = list(MIX_IMPORT_FIELD_HELP_MAP.values())
WEIGHTED_MIX_CSV_FILE_HELP = '''csv file for weighted mix of images/text/text-images with following format:
"{0}"
{1}
'''.format('","'.join(WEIGHTED_MIX_HEADERS), ','.join(WEIGHTED_MIX_HEADERS_HELP))