import argparse
from enum import Enum
from typing import Dict, List
from itemcloud.layout.base.layout_defaults import (
    LAYOUT_CSV_FILE_HELP,
)
from itemcloud.containers.weighted_image import (
    WEIGHTED_IMAGE_CSV_FILE_HELP,
    WEIGHTED_IMAGE_HEADERS,
    WEIGHTED_IMAGE_HEADERS_HELP
)
from itemcloud.containers.weighted_text import (
    WEIGHTED_TEXT_CSV_FILE_HELP,
    WEIGHTED_TEXT_HEADERS,
    WEIGHTED_TEXT_HEADERS_HELP,
)
from itemcloud.containers.weighted_textimage import (
    WEIGHTED_TEXT_IMAGE_CSV_FILE_HELP,
    WEIGHTED_TEXT_IMAGE_HEADERS,
    WEIGHTED_TEXT_IMAGE_HEADERS_HELP
)
from itemcloud.containers.weighted_mix import (
    WEIGHTED_MIX_CSV_FILE_HELP,
    WEIGHTED_MIX_HEADERS,
    WEIGHTED_MIX_HEADERS_HELP
)
from itemcloud.cli_support.base.cli_base_generate_arguments import CLIBaseGenerateArguments
from itemcloud.cli_support.base.cli_generate import cli_generate
from itemcloud.cli_support.base.cli_base_layout_arguments import CLIBaseLayoutArguments
from itemcloud.cli_support.base.cli_layout import cli_layout
class CloudType(Enum):
    IMAGE_CLOUD = 1
    TEXT_CLOUD = 2
    TEXT_IMAGE_CLOUD = 3
    MIXED_CLOUD = 4

class CloudTypeHelpers:

    def __init__(
        self,
        cloud_type: CloudType,
        name: str,
        item_types: List[str],
        weighted_csv_help: str,
        csv_fields: List[str],
        csv_value_type: List[str],
    ) -> None:
        self.cloud_type = cloud_type
        self.name = name
        self.item_types = item_types
        self.weighted_csv_help = weighted_csv_help
        self.csv_fields = csv_fields
        self.csv_value_type = csv_value_type

    def generate_args(self, args: List[str]) -> CLIBaseGenerateArguments:
        name = 'generate_{0}'.format(self.name)
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            prog=name,
            description='''
            Generate an \'{0}\' from a csv file indicating weight, and {1}
            '''.format(self.name, ', '.join(self.item_types))
        )
        CLIBaseGenerateArguments.add_parser_arguments(
            parser,
            self.weighted_csv_help,
            True,
            False
        )
        return CLIBaseGenerateArguments(name, parser, args)
    
    def generate(self, args: CLIBaseGenerateArguments) -> None:
        cli_generate(
            args.sys_args,
            args
        )
    def cli_generate(self, args: List[str]) -> None:
        self.generate(self.generate_args(args))

    def layout_args(self, args: List[str]) -> CLIBaseLayoutArguments:
        name = 'layout_{0}'.format(self.name)
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            prog=name,
            description='''
             Layout and show a generated \'{0}\' from its layout csv file
            '''.format(self.name)
        )
        CLIBaseLayoutArguments.add_parser_arguments(
            parser,
            LAYOUT_CSV_FILE_HELP,
            False,
            False
        )
        return CLIBaseLayoutArguments(name, parser, args)
    
    def layout(self, args: CLIBaseGenerateArguments) -> None:
        cli_layout(
            args.sys_args,
            args
        )
    def cli_layout(self, args: List[str]) -> None:
        self.layout(self.layout_args(args))

g_cloud_types: Dict[CloudType, CloudTypeHelpers] = {
    CloudType.IMAGE_CLOUD: CloudTypeHelpers(
        CloudType.IMAGE_CLOUD,
        'imagecloud',
        ['image'],
        WEIGHTED_IMAGE_CSV_FILE_HELP,
        WEIGHTED_IMAGE_HEADERS,
        WEIGHTED_IMAGE_HEADERS_HELP
    ),
    CloudType.TEXT_CLOUD: CloudTypeHelpers(
        CloudType.TEXT_CLOUD,
        'textcloud',
        ['text'],
        WEIGHTED_TEXT_CSV_FILE_HELP,
        WEIGHTED_TEXT_HEADERS,
        WEIGHTED_TEXT_HEADERS_HELP
    ),
    CloudType.TEXT_IMAGE_CLOUD: CloudTypeHelpers(
        CloudType.TEXT_IMAGE_CLOUD,
        'textimagecloud',
        ['text-on-image'],
        WEIGHTED_TEXT_IMAGE_CSV_FILE_HELP,
        WEIGHTED_TEXT_IMAGE_HEADERS,
        WEIGHTED_TEXT_IMAGE_HEADERS_HELP
    ),
    CloudType.MIXED_CLOUD: CloudTypeHelpers(
        CloudType.MIXED_CLOUD,
        'mixeditemcloud',
        ['image', 'text', 'text-on-image'],
        WEIGHTED_MIX_CSV_FILE_HELP,
        WEIGHTED_MIX_HEADERS,
        WEIGHTED_MIX_HEADERS_HELP
    )
}

def to_cloud_type_helper(name: str) -> CloudTypeHelpers:
    for h in g_cloud_types.values():
        if name.lower() == h.name:
            return h
    raise ValueError('cloud type: {0} does not exist'.format(name))