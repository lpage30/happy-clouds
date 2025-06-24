import argparse
from typing import List
from itemcloud.cli_support.base.cli_base_arguments import CLIBaseArguments
import itemcloud.cli_support.base.cli_helpers as cli_helpers
from itemcloud.layout.base.layout import Layout
from itemcloud.logger.base_logger import BaseLogger
from itemcloud.item_cloud import ItemCloud

DEFAULT_SCALE = '1.0'

class CLIBaseLayoutArguments(CLIBaseArguments):
    def __init__ (
        self, 
        name: str,
        parser: argparse.ArgumentParser,
        sys_args: List[str],
    ) -> None:
        super().__init__(name, parser, sys_args)

    def load(self) -> None:
        super().load()
        self.scale: float = self.parsed_args.scale

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
            '-scale',
            default=DEFAULT_SCALE,
            metavar='<float>',
            type=lambda v: cli_helpers.is_float(parser, v),
            help='Optional, (default %(default)s) scale up/down all images'
        )


def create_item_cloud(
        layout: Layout,
        logger: BaseLogger,
        item_cloud_type: ItemCloud
) -> ItemCloud:
    result = item_cloud_type(
        logger,
        layout.contour.mask,
        layout.canvas.size,
        layout.canvas.background_color,
        layout.max_items,
        None,
        layout.min_item_size,
        layout.item_step,
        layout.item_rotation_increment,
        layout.resize_type,
        layout.maximize_type,
        layout.scale,
        layout.contour.width,
        layout.contour.color,
        layout.margin,
        layout.opacity,
        layout.resize_resampling,
        layout.rotate_resampling,
        layout.canvas.mode,
        layout.canvas.name
    )
    result.layout_ = layout
    return result
