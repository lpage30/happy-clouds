import argparse
import os
import sys
from typing import List
import numpy as np
from clis.argument_cli_helpers import (
    existing_path, 
    in_array,
    is_integer,
    is_float,
    is_size,
    is_enum,
    create_name,
    to_unused_filepath
)
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
from itemcloud.containers.base.image_item import IMAGE_FORMATS
import itemcloud.item_cloud_defaults as item_cloud_defaults
from itemcloud.size import (
    RESIZE_TYPES,
    ResizeType
)
from itemcloud.util.search_types import (
    SEARCH_PATTERNS,
    SearchPattern
)
from itemcloud.logger.base_logger import BaseLogger, set_logger_instance
from itemcloud.logger.file_logger import FileLogger
from itemcloud.containers.base.item_factory import load_weighted_items
from itemcloud.containers.base.weighted_item import WeightedItem
from itemcloud.item_cloud import ItemCloud
from itemcloud.containers.base.image_item import ImageItem

def main() -> None:
    sys_args = sys.argv[1:]
    parser = getArgParser()
    args = parser.parse_args()
    name = create_name(args.input, args.output_image_format, args.output_directory)
    if args.log_filepath:
        logger: BaseLogger = FileLogger.create(parser.prog, False, args.log_filepath)
    else:
        logger: BaseLogger = BaseLogger.create(parser.prog, False)
    set_logger_instance(logger)

    logger.info('{0} {1} {2}'.format(parser.prog, name, ' '.join(sys_args)))
    logger.info('loading {0} ...'.format(args.input))
    weighted_items: List[WeightedItem] = load_weighted_items(args.input)
    total_items = len(weighted_items)
    logger.info('loaded {0} weights and items'.format(total_items))
    mask_image = None
    if args.mask is not None:
        mask_image = ImageItem.open(args.mask)

    cloud = ItemCloud(
        logger=logger,
        mask=mask_image,
        size=args.cloud_size,
        background_color=args.background_color,
        max_item_size=args.max_item_size,
        min_item_size=args.min_item_size,
        item_step=args.step_size,
        item_rotation_increment=args.rotation_increment,
        resize_type=args.resize_type,
        contour_width=args.contour_width,
        contour_color=args.contour_color,
        margin=args.margin,
        mode=args.mode,
        name=name,
        total_threads=args.total_threads,
        search_pattern=args.placement_search_pattern
    )
    logger.info('generating cloud from {0} weighted and normalized items.{1}'.format(
        total_items,
        ' Cloud will be expanded iteratively by cloud_expansion_step_size until all items are positioned.' if 0 != args.cloud_expansion_step_size else ''
    ))
    ## Generate
    layout = cloud.generate(weighted_items, cloud_expansion_step_size=args.cloud_expansion_step_size)
    process_layout(args, logger, layout)

    ## Optionally Maximize images
    if args.maximize_empty_space:
        logger.info('Maximizing {0} items: expanding them to fit their surrounding empty space.'.format(len(layout.items)))
        layout = cloud.maximize_empty_space(layout)
        process_layout(args, logger, layout)


def process_layout(args, logger, layout) -> None:
    reconstructed_reservation_map = layout.reconstruct_reservation_map(logger)
    if not(np.array_equal(layout.canvas.reservation_map, reconstructed_reservation_map)):
        logger.info('Warning reservations map from generation not same as reconstructed from items.')
    
    collage = layout.to_image(args.logger)
    reservation_chart = layout.to_reservation_chart_image()

    if args.output_directory is not None:
        filepath = to_unused_filepath(args.output_directory, collage.name, args.output_image_format)
        logger.info('saving itemcloud to {0}'.format(filepath))
        collage.image.save(filepath, args.output_image_format)
        logger.info('completed! {0}'.format(filepath))

        filepath = to_unused_filepath(args.output_directory, reservation_chart.name, args.output_image_format)
        logger.info('saving itemcloud reservation chart to {0}'.format(filepath))
        reservation_chart.image.save(filepath, args.output_image_format)
        logger.info('completed! {0}'.format(filepath))
    
        filepath = to_unused_filepath(args.output_directory, layout.name, 'csv')
        logger.info('saving itemcloud Layout to {0}'.format(filepath))
        layout.write(filepath)
        logger.info('completed! {0}'.format(filepath))

    if args.show_itemcloud_reservation_chart:
        reservation_chart.show()

    if args.show_itemcloud:
        collage.show()

def getArgParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        prog='generate (image|text|image-text) cloud',
        description='''
        Generate an image cloud from a csv file whose rows contain:
        weight, and either image or text or image-text (image with text watermark)
        The weight is used to indicate importance of the image|text|image-text item relative
        to other image|text|image-text in the file.
        '''
    )
    parser.add_argument(
        '-i', 
        '--input',
        metavar='<csv_filepath>',
        type=lambda fp: existing_path(parser, 'File', fp),
        required=True,
        help="csv file of weights and image|text|image-text:\n\"{0}\"\n{1}".format(
            '","'.join([
                *WEIGHTED_IMAGE_HEADERS,
                *WEIGHTED_TEXT_HEADERS,
                *WEIGHTED_TEXT_IMAGE_HEADERS
            ]),
            ','.join([
                *WEIGHTED_IMAGE_HEADERS_HELP,
                *WEIGHTED_TEXT_HEADERS_HELP,
                *WEIGHTED_TEXT_IMAGE_HEADERS_HELP
            ])
        )
    )
    parser.add_argument(
        '-output_directory',
        metavar='<output-directory-path>',
        type=lambda d: existing_path(parser, 'Directory', d),
        help='Optional, output directory for all output'
    )
    parser.add_argument(
        '-output_image_format',
        default='png',
        metavar='{0}'.format('|'.join(IMAGE_FORMATS)),
        type=lambda v: in_array(parser, IMAGE_FORMATS, v),
        help='Optional,(default %(default)s) image format: [{0}]'.format(','.join(IMAGE_FORMATS))
    )
    parser.add_argument(
        '-show_itemcloud',
        action='store_true',
        help='Optional, (default)show itemcloud.'
    )
    parser.add_argument(
        '-no-show_itemcloud',
        action='store_false',
        dest='show_itemcloud',
        help='Optional, do not show mage itemcloud.'
    )
    parser.set_defaults(show_itemcloud=True)

    parser.add_argument(
        '-show_itemcloud_reservation_chart',
        action='store_true',
        help='Optional, show reservation_chart for itemcloud.'
    )
    parser.add_argument(
        '-no-show_itemcloud_reservation_chart',
        action='store_false',
        dest='show_itemcloud_reservation_chart',
        help='Optional, (default) do not show reservation_chart for itemcloud.'
    )
    parser.set_defaults(show_itemcloud_reservation_chart=False)

    parser.add_argument(
        '-maximize_empty_space',
        action='store_true',
        help='Optional (default)maximize items, after generation, to fill surrounding empty space.'
    )
    parser.add_argument(
        '-no-maximize_empty_space',
        action='store_false',
        dest='maximize_empty_space',
        help='Optional do not maximize items, after generation, to fill surrounding empty space.'
    )
    parser.set_defaults(maximize_empty_space=True)
    parser.add_argument(
        '-verbose',
        action='store_true',
        help='Optional, (default)report progress as constructing itemcloud'
    )
    parser.add_argument(
        '-no-verbose',
        action='store_false',
        dest='verbose',
        help='Optional, do not report progress as constructing itemcloud'
    )
    parser.set_defaults(verbose=True)
    
    parser.add_argument(
        '-log_filepath',
        metavar='<log-filepath>',
        type=lambda fp: existing_path(parser, 'Directory', os.path.dirname(fp), fp),
        help='Optional, all output logging will also be written to this logfile'
    )
    ### generate-specific arguments ###
    parser.add_argument(
        '-cloud_size',
        default=item_cloud_defaults.DEFAULT_CLOUD_SIZE,
        metavar='"<width>,<height>"',
        type= lambda v: is_size(parser, v),
        help='Optional, (default %(default)s) {0}'.format(item_cloud_defaults.CLOUD_SIZE_HELP)
    )
    parser.add_argument(
        '-placement_search_pattern',
        default=item_cloud_defaults.DEFAULT_SEARCH_PATTERN,
        metavar='{0}'.format('|'.join(SEARCH_PATTERNS)),
        type=lambda v: is_enum(parser, SearchPattern, v),
        help='Optional,(default %(default)s) {0}'.format(item_cloud_defaults.SEARCH_PATTERN_HELP)
    )

    parser.add_argument(
        '-cloud_expansion_step_size',
        default=0,
        metavar='<int>',
        type=lambda v: is_integer(parser, v),
        help='Optional, (default %(default)s) {0}'.format('''Step size for expanding cloud to fit more images
images will be proportionally fit to the original cloud size but may still not get placed to fit in cloud.
step > 0 the cloud will expand by this amount in a loop until all images fit into it.
step > 1 might speed up computation but give a worse fit.
''')
    )
    parser.add_argument(
        '-margin',
        default=item_cloud_defaults.DEFAULT_MARGIN,
        metavar='<number>',
        type=lambda v: is_integer(parser, v),
        help='Optional, (default %(default)s) {0}'.format(item_cloud_defaults.MARGIN_HELP)
    )

    parser.add_argument(
        '-min_item_size',
        default=item_cloud_defaults.DEFAULT_MIN_ITEM_SIZE,
        metavar='"<width>,<height>"',
        type=lambda v: is_size(parser, v),
        help='Optional, (default %(default)s) {0}'.format(item_cloud_defaults.MIN_ITEM_SIZE_HELP)
    )

    parser.add_argument(
        '-step_size',
        default=item_cloud_defaults.DEFAULT_STEP_SIZE,
        metavar='<int>',
        type=lambda v: is_integer(parser, v),
        help='Optional, (default %(default)s) {0}'.format(item_cloud_defaults.STEP_SIZE_HELP)
    )

    parser.add_argument(
        '-rotation_increment',
        default=item_cloud_defaults.DEFAULT_ROTATION_INCREMENT,
        metavar='<int>',
        type=lambda v: is_integer(parser, v),
        help='Optional, (default %(default)s) {0}'.format(item_cloud_defaults.ROTATION_INCREMENT_HELP)
    )


    parser.add_argument(
        '-resize_type',
        default=item_cloud_defaults.DEFAULT_RESIZE_TYPE,
        metavar='{0}'.format('|'.join(RESIZE_TYPES)),
        type=lambda v: is_enum(parser, ResizeType, v),
        help='Optional, (default %(default)s) {0}'.format(item_cloud_defaults.RESIZE_TYPE_HELP)
    )

    parser.add_argument(
        '-max_item_size',
        default=item_cloud_defaults.DEFAULT_MAX_ITEM_SIZE,
        metavar='"<width>,<height>"',
        type=lambda v: is_size(parser, v),
        help='Optional, (default %(default)s) {0}'.format(item_cloud_defaults.MAX_ITEM_SIZE_HELP)
    )

    parser.add_argument(
        '-mode',
        default=item_cloud_defaults.DEFAULT_MODE,
        metavar='{0}'.format('|'.join(item_cloud_defaults.MODE_TYPES)),
        type=lambda v: in_array(parser, item_cloud_defaults.MODE_TYPES, v),
        help='Optional, (default %(default)s) {0}'.format(item_cloud_defaults.MODE_HELP)
    )
    parser.add_argument(
        '-background_color',
        default=item_cloud_defaults.DEFAULT_BACKGROUND_COLOR,
        metavar='<color-name>',
        help='Optional, (default %(default)s) {0}'.format(item_cloud_defaults.BACKGROUND_COLOR_HELP)
    )

    parser.add_argument(
        '-mask',
        metavar='<image_file_path>',
        default=None,
        type=lambda fp: existing_path(parser, 'File', fp),
        help='Optional, (default %(default)s) {0}'.format(item_cloud_defaults.MASK_HELP)
    )
    parser.add_argument(
        '-contour_width',
        default=item_cloud_defaults.DEFAULT_CONTOUR_WIDTH,
        metavar='<float>',
        type=lambda v: is_float(parser, v),
        help='Optional, (default %(default)s) {0}'.format(item_cloud_defaults.CONTOUR_WIDTH_HELP)
    )
    parser.add_argument(
        '-contour_color',
        default=item_cloud_defaults.DEFAULT_CONTOUR_COLOR,
        metavar='<color-name>',
        help='Optional, (default %(default)s) {0}'.format(item_cloud_defaults.CONTOUR_COLOR_HELP)
    )
    parser.add_argument(
        '-total_threads',
        default=item_cloud_defaults.DEFAULT_TOTAL_THREADS,
        metavar='<int>',
        type=lambda v: is_integer(parser, v),
        help='Optional, (default $(default)s) {0}'.format(item_cloud_defaults.TOTAL_THREADS_HELP)
    )
    return parser

if __name__ == '__main__':
    main()