import argparse
import sys
import numpy as np
from itemcloud.size import (
    Size,
    RESIZE_TYPES
)
from textcloud.containers.weighted_text import (
    WEIGHTED_TEXTS_CSV_FILE_HELP
)
import itemcloud.item_cloud_defaults as item_cloud_defaults
import itemcloud.clis.cli_helpers as cli_helpers
from itemcloud.clis.cli_base_arguments import CLIBaseArguments
from textcloud.text_cloud import TextCloud
from textcloud.containers.weighted_text import ( WeightedText, load_weighted_texts)


DEFAULT_SHOW = True
DEFAULT_VERBOSE = False
DEFAULT_CLOUD_EXPAND_STEP_SIZE = '0'
DEFAULT_CLOUD_EXPAND_STEP_SIZE_HELP = '''Step size for expanding cloud to fit more images
images will be proportionally fit to the original cloud size but may still not get placed to fit in cloud.
step > 0 the cloud will expand by this amount in a loop until all images fit into it.
step > 1 might speed up computation but give a worse fit.
'''

class GenerateCLIArguments(CLIBaseArguments):
    name = 'generate_textcloud'
    def __init__ (
        self, 
        parsedArgs
    ) -> None:
        super().__init__(self.name, parsedArgs)
        self.max_item_size: Size | None = parsedArgs.max_item_size
        self.min_item_size: Size = parsedArgs.min_item_size
        self.cloud_size: Size = parsedArgs.cloud_size
        self.background_color = parsedArgs.background_color
        self.contour_width: int = parsedArgs.contour_width
        self.contour_color: str = parsedArgs.contour_color
        self.mask: str | None = parsedArgs.mask
        self.step_size: int = parsedArgs.step_size
        self.rotation_increment: int = parsedArgs.rotation_increment
        self.resize_type: bool = parsedArgs.resize_type
        self.margin: int = parsedArgs.margin
        self.mode: str = parsedArgs.mode
        self.cloud_expansion_step_size: int = parsedArgs.cloud_expansion_step_size
        self.total_threads: int = parsedArgs.total_threads
    
    @staticmethod
    def parse(arguments: list[str]):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            prog=GenerateCLIArguments.name,
            description='''
            Generate an \'ImageCloud\' from a csv file indicating image filepath and weight for image.
            '''
        )
        CLIBaseArguments.add_parser_arguments(
            parser,
            WEIGHTED_TEXTS_CSV_FILE_HELP,
            DEFAULT_SHOW,
            DEFAULT_VERBOSE
        )

        parser.add_argument(
            '-cloud_size',
            default=item_cloud_defaults.DEFAULT_CLOUD_SIZE,
            metavar='"<width>,<height>"',
            type= lambda v: cli_helpers.is_size(parser, v),
            help='Optional, (default %(default)s) {0}'.format(item_cloud_defaults.CLOUD_SIZE_HELP)
        )

        parser.add_argument(
            '-cloud_expansion_step_size',
            default=DEFAULT_CLOUD_EXPAND_STEP_SIZE,
            metavar='<int>',
            type=lambda v: cli_helpers.is_integer(parser, v),
            help='Optional, (default %(default)s) {0}'.format(DEFAULT_CLOUD_EXPAND_STEP_SIZE_HELP)
        )
        parser.add_argument(
            '-margin',
            default=item_cloud_defaults.DEFAULT_MARGIN,
            metavar='<number>',
            type=lambda v: cli_helpers.is_integer(parser, v),
            help='Optional, (default %(default)s) {0}'.format(item_cloud_defaults.MARGIN_HELP)
        )

        parser.add_argument(
            '-min_item_size',
            default=item_cloud_defaults.DEFAULT_MIN_ITEM_SIZE,
            metavar='"<width>,<height>"',
            type=lambda v: cli_helpers.is_size(parser, v),
            help='Optional, (default %(default)s) {0}'.format(item_cloud_defaults.MIN_ITEM_SIZE_HELP)
        )

        parser.add_argument(
            '-step_size',
            default=item_cloud_defaults.DEFAULT_STEP_SIZE,
            metavar='<int>',
            type=lambda v: cli_helpers.is_integer(parser, v),
            help='Optional, (default %(default)s) {0}'.format(item_cloud_defaults.STEP_SIZE_HELP)
        )

        parser.add_argument(
            '-rotation_increment',
            default=item_cloud_defaults.DEFAULT_ROTATION_INCREMENT,
            metavar='<int>',
            type=lambda v: cli_helpers.is_integer(parser, v),
            help='Optional, (default %(default)s) {0}'.format(item_cloud_defaults.ROTATION_INCREMENT_HELP)
        )


        parser.add_argument(
            '-resize_type',
            default=item_cloud_defaults.DEFAULT_RESIZE_TYPE,
            metavar='{0}'.format('|'.join(RESIZE_TYPES)),
            type=lambda v: cli_helpers.is_resize_type(parser, v),
            help='Optional, (default %(default)s) {0}'.format(item_cloud_defaults.RESIZE_TYPE_HELP)
        )

        parser.add_argument(
            '-max_item_size',
            default=item_cloud_defaults.DEFAULT_MAX_ITEM_SIZE,
            metavar='"<width>,<height>"',
            type=lambda v: cli_helpers.is_size(parser, v),
            help='Optional, (default %(default)s) {0}'.format(item_cloud_defaults.MAX_ITEM_SIZE_HELP)
        )

        parser.add_argument(
            '-mode',
            default=item_cloud_defaults.DEFAULT_MODE,
            metavar='{0}'.format('|'.join(item_cloud_defaults.MODE_TYPES)),
            type=lambda v: cli_helpers.is_one_of_array(parser, v, item_cloud_defaults.MODE_TYPES),
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
            type=lambda fp: cli_helpers.existing_filepath(parser, fp),
            help='Optional, (default %(default)s) {0}'.format(item_cloud_defaults.MASK_HELP)
        )
        parser.add_argument(
            '-contour_width',
            default=item_cloud_defaults.DEFAULT_CONTOUR_WIDTH,
            metavar='<float>',
            type=lambda v: cli_helpers.is_float(parser, v),
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
            type=lambda v: cli_helpers.is_integer(parser, v),
            help='Optional, (default $(default)s) {0}'.format(item_cloud_defaults.TOTAL_THREADS_HELP)
        )

        args = parser.parse_args(arguments if 0 < len(arguments) else ['-h'])
        return GenerateCLIArguments(args)


def generate(args: GenerateCLIArguments | None = None) -> None:
    sys_args = sys.argv[1:]
    if args == None:
        args = GenerateCLIArguments.parse(sys_args)

    print('{0} {1}'.format(GenerateCLIArguments.name, ' '.join(sys_args)))
    args.logger.info('{0} {1}'.format(GenerateCLIArguments.name, ' '.join(sys_args)))
    args.logger.info('loading {0} ...'.format(args.input))
    weighted_texts: list[WeightedText] = load_weighted_texts(args.input)
    total_texts = len(weighted_texts)
    args.logger.info('loaded {0} weights and texts'.format(total_texts))

    text_cloud = TextCloud(
        logger=args.logger,
        mask=args.mask,
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
        name=args.get_output_name(),
        total_threads=args.total_threads
    )
    args.logger.info('generating textcloud from {0} weighted and normalized texts.{1}'.format(
        total_texts,
        ' Cloud will be expanded iteratively by cloud_expansion_step_size until all texts are positioned.' if 0 != args.cloud_expansion_step_size else ''
    ))

    layout = text_cloud.generate(weighted_texts, cloud_expansion_step_size=args.cloud_expansion_step_size)
    if args.maximize_empty_space:
        args.logger.info('Maximizing {0} texts: expanding them to fit their surrounding empty space.'.format(len(layout.items)))
        layout = text_cloud.maximize_empty_space(layout)

    reconstructed_reservation_map = layout.reconstruct_reservation_map(args.logger)
    if not(np.array_equal(layout.canvas.reservation_map, reconstructed_reservation_map)):
        args.logger.info('Warning reservations map from generation not same as reconstructed from images.')
    

    collage = layout.to_image(args.logger)

    args.try_save_output(collage, None, layout)

    if args.show_itemcloud_reservation_chart:
        reservation_chart = layout.to_reservation_chart_image()
        args.try_save_output(None, reservation_chart, None)
        reservation_chart.show()

    if args.show_itemcloud:
        collage.show()

if __name__ == '__main__':
    generate()
