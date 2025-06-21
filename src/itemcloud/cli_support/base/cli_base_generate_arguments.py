import argparse
from typing import List
from itemcloud.size import (
    Size,
    RESIZE_TYPES
)
from itemcloud.item_cloud import ItemCloud

import itemcloud.item_cloud_defaults as item_cloud_defaults
import itemcloud.cli_support.base.cli_helpers as cli_helpers
from itemcloud.cli_support.base.cli_base_arguments import CLIBaseArguments
from itemcloud.util.search_types import (
    SEARCH_PATTERNS,
    SearchPattern,
    is_search_pattern
)

DEFAULT_CLOUD_EXPAND_STEP_SIZE = '0'
DEFAULT_CLOUD_EXPAND_STEP_SIZE_HELP = '''Step size for expanding cloud to fit more images
images will be proportionally fit to the original cloud size but may still not get placed to fit in cloud.
step > 0 the cloud will expand by this amount in a loop until all images fit into it.
step > 1 might speed up computation but give a worse fit.
'''

class CLIBaseGenerateArguments(CLIBaseArguments):
    def __init__ (
        self, 
        name: str,
        parser: argparse.ArgumentParser,
        sys_args: List[str],
    ) -> None:
        super().__init__(name, parser, sys_args)

    def load(self) -> None:
        super().load()
        self.max_item_size: Size | None = self.parsed_args.max_item_size
        self.min_item_size: Size = self.parsed_args.min_item_size
        self.cloud_size: Size = self.parsed_args.cloud_size
        self.placement_search_pattern: SearchPattern = self.parsed_args.placement_search_pattern
        self.background_color = self.parsed_args.background_color
        self.contour_width: int = self.parsed_args.contour_width
        self.contour_color: str = self.parsed_args.contour_color
        self.mask: str | None = self.parsed_args.mask
        self.step_size: int = self.parsed_args.step_size
        self.rotation_increment: int = self.parsed_args.rotation_increment
        self.resize_type: bool = self.parsed_args.resize_type
        self.margin: int = self.parsed_args.margin
        self.opacity_pct: int = self.parsed_args.opacity_pct
        self.mode: str = self.parsed_args.mode
        self.cloud_expansion_step_size: int = self.parsed_args.cloud_expansion_step_size
        self.total_threads: int = self.parsed_args.total_threads

    @staticmethod 
    def add_parser_arguments(
        parser: argparse.ArgumentParser,
        inputHelp: str,
        showDefault: bool,
        verboseDefault: bool
    ) -> None:
        CLIBaseArguments.add_parser_arguments(
            parser,
            inputHelp,
            showDefault,
            verboseDefault
        )

        parser.add_argument(
            '-cloud_size',
            default=item_cloud_defaults.DEFAULT_CLOUD_SIZE,
            metavar='"<width>,<height>"',
            type= lambda v: cli_helpers.is_size(parser, v),
            help='Optional, (default %(default)s) {0}'.format(item_cloud_defaults.CLOUD_SIZE_HELP)
        )

        parser.add_argument(
            '-placement_search_pattern',
            default=item_cloud_defaults.DEFAULT_SEARCH_PATTERN,
            metavar='{0}'.format('|'.join(SEARCH_PATTERNS)),
            type=lambda v: is_search_pattern(v),
            help='Optional,(default %(default)s) {0}'.format(item_cloud_defaults.SEARCH_PATTERN_HELP)
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
            '-opacity_pct',
            default=item_cloud_defaults.DEFAULT_OPACITY,
            metavar='<0-100>',
            type=lambda v: cli_helpers.is_integer(parser, v),
            help='Optional, (default %(default)s) {0}'.format(item_cloud_defaults.OPACITY_HELP)
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


def create_item_cloud(args: CLIBaseGenerateArguments, item_cloud_type: ItemCloud) -> ItemCloud:
    return item_cloud_type(
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
        opacity=args.opacity_pct,
        mode=args.mode,
        name=args.get_output_name(),
        total_threads=args.total_threads,
        search_pattern=args.placement_search_pattern
    )
