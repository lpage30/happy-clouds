import argparse
from typing import List
from itemcloud.logger.base_logger import BaseLogger, set_logger_instance
from itemcloud.logger.file_logger import FileLogger
import itemcloud.cli_support.base.cli_helpers as cli_helpers
from itemcloud.util.parsers import to_unused_filepath
from itemcloud.containers.named_image import NamedImage
from itemcloud.layout.base.layout import Layout

DEFAULT_MAXIMIZE_EMPTY_SPACE = False
DEFAULT_IMAGE_FORMAT = 'png'

IMAGE_FORMATS = [
    'blp',
    'bmp',
    'dds',
    'dib',
    'eps',
    'gif',
    'icns',
    'ico',
    'im',
    'jpeg',
    'mpo',
    'msp',
    'pcx',
    'pfm',
    'png',
    'ppm',
    'sgi',
    'webp',
    'xbm'
]
IMAGE_FORMAT_HELP = 'image format: [{0}]'.format(','.join(IMAGE_FORMATS))

class CLIBaseArguments:
    def __init__ (
        self,
        name: str,
        parser: argparse.ArgumentParser,
        sys_args: List[str],
    ):
        self.sys_args = sys_args
        self.name = name
        self.parser = parser
        self.parsed_args = None

    def load(self) -> None:
        if self.parsed_args is None:
            self.parsed_args = self.parser.parse_args(self.sys_args)

        self.input: str = self.parsed_args.input
        self.output_directory: str | None = self.parsed_args.output_directory
        self.output_image_format: str = self.parsed_args.output_image_format
        self.maximize_empty_space: bool = self.parsed_args.maximize_empty_space
        self.show_itemcloud: bool = self.parsed_args.show_itemcloud
        self.show_itemcloud_reservation_chart: bool = self.parsed_args.show_itemcloud_reservation_chart
        if self.parsed_args.log_filepath:
            self.logger: BaseLogger = FileLogger.create(self.name, self.parsed_args.verbose, self.parsed_args.log_filepath)
        else:
            self.logger: BaseLogger = BaseLogger.create(self.name, self.parsed_args.verbose)
        set_logger_instance(self.logger)
    
    def help(self) -> str:
        return self.parser.format_help()
    
    def get_output_name(self, existing_name: str | None = None) -> str:
        return cli_helpers.to_name(self.input, self.output_image_format, existing_name, self.output_directory)

    def try_save_output(
        self, 
        collage: NamedImage | None = None,
        reservation_chart: NamedImage | None = None,
        layout: Layout | None = None
    ) -> bool:
        result: bool = False
        if self.output_directory is None:
            return result

        if collage:
            result = True
            filepath = to_unused_filepath(self.output_directory, collage.name, self.output_image_format)
            print('saving itemcloud to {0}'.format(filepath))
            collage.image.save(filepath, self.output_image_format)
            print('completed! {0}'.format(filepath))

        if reservation_chart:
            result = True
            filepath = to_unused_filepath(self.output_directory, reservation_chart.name, self.output_image_format)
            print('saving itemcloud reservation chart to {0}'.format(filepath))
            reservation_chart.image.save(filepath, self.output_image_format)
            print('completed! {0}'.format(filepath))
        
        if layout:
            result = True
            filepath = to_unused_filepath(self.output_directory, layout.name, 'csv')
            print('saving itemcloud Layout to {0}'.format(filepath))
            layout.write(filepath)
            print('completed! {0}'.format(filepath))
        
        return result

    @staticmethod
    def add_parser_arguments(
        parser: argparse.ArgumentParser,
        inputHelp: str,
        showDefault: bool,
        verboseDefault: bool
    ) -> None:
        parser.add_argument(
            '-i', 
            '--input',
            metavar='<csv_filepath>',
            type=lambda fp: cli_helpers.existing_filepath(parser, fp),
            required=True,
            help='Required, {0}'.format(inputHelp)
        )
        parser.add_argument(
            '-output_directory',
            metavar='<output-directory-path>',
            type=lambda d: cli_helpers.existing_dirpath(parser, d),
            help='Optional, output directory for all output'
        )
        parser.add_argument(
            '-output_image_format',
            default=DEFAULT_IMAGE_FORMAT,
            metavar='{0}'.format('|'.join(IMAGE_FORMATS)),
            type=lambda v: cli_helpers.is_one_of_array(parser, v, IMAGE_FORMATS),
            help='Optional,(default %(default)s) {0}'.format(IMAGE_FORMAT_HELP)
        )
        parser.add_argument(
            '-show_itemcloud',
            action='store_true',
            help='Optional, {0}show itemcloud.'.format('(default) ' if showDefault else '')
        )
        parser.add_argument(
            '-no-show_itemcloud',
            action='store_false',
            dest='show_itemcloud',
            help='Optional, {0}do not show mage itemcloud.'.format('' if showDefault else '(default) ')
        )
        parser.set_defaults(show_itemcloud=showDefault)

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
            help='Optional {0}maximize items, after generation, to fill surrounding empty space.'.format('(default) ' if DEFAULT_MAXIMIZE_EMPTY_SPACE else '')
        )
        parser.add_argument(
            '-no-maximize_empty_space',
            action='store_false',
            dest='maximize_empty_space',
            help='Optional {0}maximize items, after generation, to fill surrounding empty space.'.format('' if DEFAULT_MAXIMIZE_EMPTY_SPACE else '(default) ')
        )
        parser.set_defaults(maximize_empty_space=DEFAULT_MAXIMIZE_EMPTY_SPACE)
        parser.add_argument(
            '-verbose',
            action='store_true',
            help='Optional, {0}report progress as constructing itemcloud'.format('(default) ' if verboseDefault else '')
        )
        parser.add_argument(
            '-no-verbose',
            action='store_false',
            dest='verbose',
            help='Optional, {0}report progress as constructing itemcloud'.format('' if verboseDefault else '(default) ')
        )
        parser.set_defaults(verbose=verboseDefault)
        
        parser.add_argument(
            '-log_filepath',
            metavar='<log-filepath>',
            type=lambda fp: cli_helpers.existing_dirpath_of_filepath(parser, fp),
            help='Optional, all output logging will also be written to this logfile'
        )
