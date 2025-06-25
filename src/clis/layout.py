import argparse
import os
import sys
from clis.argument_cli_helpers import (
    existing_path, 
    in_array,
    is_float,
    create_name,
    to_unused_filepath
)
from itemcloud.containers.base.image_item import IMAGE_FORMATS, set_global_image_settings
from itemcloud.layout.base.layout_defaults import (
    LAYOUT_HEADERS,
    LAYOUT_CANVAS_HEADERS,
    LAYOUT_CONTOUR_HEADERS,
    LAYOUT_ITEM_HEADERS,
    LAYOUT_HEADERS_HELP,
    LAYOUT_CANVAS_HEADER_HELP,
    LAYOUT_CONTOUR_HEADER_HELP,
    LAYOUT_ITEM_HEADER_HELP,
)
from itemcloud.logger.base_logger import BaseLogger, set_logger_instance
from itemcloud.logger.file_logger import FileLogger
from itemcloud.layout.base.layout import Layout
from itemcloud.item_cloud import ItemCloud

def main() -> None:
    sys_args = sys.argv[1:]
    parser = getArgParser()
    args = parser.parse_args()
    if args.log_filepath:
        logger: BaseLogger = FileLogger.create(parser.prog, args.verbose, args.log_filepath)
    else:
        logger: BaseLogger = BaseLogger.create(parser.prog, args.verbose)
    set_logger_instance(logger)

    logger.info('{0} {1}'.format(args.name, ' '.join(sys_args)))
    logger.info('loading {0} ...'.format(args.input))
    layout: Layout = Layout.load(args.input, set_global_image_settings)
    logger.info('loaded layout with {0} items'.format(len(layout.items)))
    logger.info('laying-out and showing itemcloud layout with {0} scaling.'.format(args.scale))
    
    layout.set_names(
        create_name(args.input, args.output_image_format, args.output_directory, layout.name),
        create_name(args.input, args.output_image_format, args.output_directory, layout.canvas.name)
    )

    if args.maximize_empty_space:
        logger.info('Maximizing {0} images: expanding them to fit their surrounding empty space.'.format(len(layout.items)))
        cloud = ItemCloud(
            logger=logger,
            mask=layout.contour.mask,
            size=layout.canvas.size,
            background_color=layout.canvas.background_color,
            max_items=layout.max_items,
            max_item_size=None,
            min_item_size=layout.min_item_size,
            item_step=layout.item_step,
            item_rotation_increment=layout.item_rotation_increment,
            resize_type=layout.resize_type,
            maximize_type=layout.maximize_type,
            scale=layout.scale,
            contour_width=layout.contour.width,
            contour_color=layout.contour.color,
            margin=layout.margin,
            opacity=layout.opacity,
            resize_resampling=layout.resize_resampling,
            rotate_resampling=layout.rotate_resampling,
            mode=layout.canvas.mode,
            name=layout.canvas.name,
            total_threads=layout.total_threads,
            search_pattern=layout._search_pattern
        )
        cloud.layout_ = layout
        layout = cloud.maximize_empty_space(layout)

    collage = layout.to_image(logger, args.scale)
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
        prog='layout existing (image|text|image-text) cloud',
        description='''
        Layout and show an image cloud as defined by its previously generated layout csv file
        Containing all the reservations, sizes, and rotations of image|text|image-text generated
        to produce a single image cloud.
        '''
    )
    parser.add_argument(
        '-i', 
        '--input',
        metavar='<csv_filepath>',
        type=lambda fp: existing_path(parser, 'File', fp),
        required=True,
        help="csv file representing 1 Layout Contour, 1 Layout Canvas and N Layout Items:\n\"{0}\"\n{1}".format(
            '","'.join([
                *LAYOUT_HEADERS,
                *LAYOUT_CANVAS_HEADERS,
                *LAYOUT_CONTOUR_HEADERS,
                *LAYOUT_ITEM_HEADERS,
            ]),
            ','.join([
                *LAYOUT_HEADERS_HELP,
                *LAYOUT_CANVAS_HEADER_HELP,
                *LAYOUT_CONTOUR_HEADER_HELP,
                *LAYOUT_ITEM_HEADER_HELP,
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
    parser.add_argument(
        '-scale',
        default=1.0,
        metavar='<float>',
        type=lambda v: is_float(parser, v),
        help='Optional, (default %(default)s) scale up/down all images'
    )
    return parser

if __name__ == '__main__':
    main()