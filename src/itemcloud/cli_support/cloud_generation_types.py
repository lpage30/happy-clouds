import argparse
from enum import Enum
from typing import Dict, List
from itemcloud.layout.base.layout_item import create_layout_item_f
from itemcloud.layout.base.layout_defaults import (
    LAYOUT_CSV_FILE_HELP,
)
from itemcloud.containers.base.weighted_item import load_weighted_items_f

from itemcloud.containers.weighted_image import (
    load_weighted_images,
    WEIGHTED_IMAGE_CSV_FILE_HELP,
    WEIGHTED_IMAGE_HEADERS,
    WEIGHTED_IMAGE_HEADERS_HELP
)
from itemcloud.layout.layout_image import (
    create_layout_image
)
from itemcloud.containers.weighted_text import (
    load_weighted_texts,
    WEIGHTED_TEXT_CSV_FILE_HELP,
    WEIGHTED_TEXT_HEADERS,
    WEIGHTED_TEXT_HEADERS_HELP,
)
from itemcloud.layout.layout_text import (
    create_layout_text
)
from itemcloud.containers.weighted_textimage import (
    load_weighted_text_images,
    WEIGHTED_TEXT_IMAGE_CSV_FILE_HELP,
    WEIGHTED_TEXT_IMAGE_HEADERS,
    WEIGHTED_TEXT_IMAGE_HEADERS_HELP
)
from itemcloud.layout.layout_textimage import (
    create_layout_text_image
)
from itemcloud.layout.layout_mix import (
    create_layout_mix
)
from itemcloud.containers.weighted_mix import (
    load_weighted_mix,
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
        create_layout: create_layout_item_f,
        load_weighted_items: load_weighted_items_f
    ) -> None:
        self.cloud_type = cloud_type
        self.name = name
        self.item_types = item_types
        self.weighted_csv_help = weighted_csv_help
        self.csv_fields = csv_fields
        self.csv_value_type = csv_value_type
        self.create_layout = create_layout
        self.load_weighted_items = load_weighted_items

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
            args,
            self.load_weighted_items
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
            args,
            self.create_layout
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
        WEIGHTED_IMAGE_HEADERS_HELP,
        create_layout_image,
        load_weighted_images, 
    ),
    CloudType.TEXT_CLOUD: CloudTypeHelpers(
        CloudType.TEXT_CLOUD,
        'textcloud',
        ['text'],
        WEIGHTED_TEXT_CSV_FILE_HELP,
        WEIGHTED_TEXT_HEADERS,
        WEIGHTED_TEXT_HEADERS_HELP,
        create_layout_text,
        load_weighted_texts,
    ),
    CloudType.TEXT_IMAGE_CLOUD: CloudTypeHelpers(
        CloudType.TEXT_IMAGE_CLOUD,
        'textimagecloud',
        ['text-on-image'],
        WEIGHTED_TEXT_IMAGE_CSV_FILE_HELP,
        WEIGHTED_TEXT_IMAGE_HEADERS,
        WEIGHTED_TEXT_IMAGE_HEADERS_HELP,
        create_layout_text_image,
        load_weighted_text_images,
    ),
    CloudType.MIXED_CLOUD: CloudTypeHelpers(
        CloudType.MIXED_CLOUD,
        'mixeditemcloud',
        ['image', 'text', 'text-on-image'],
        WEIGHTED_MIX_CSV_FILE_HELP,
        WEIGHTED_MIX_HEADERS,
        WEIGHTED_MIX_HEADERS_HELP,
        create_layout_mix,
        load_weighted_mix,
    )
}

def to_cloud_type_helper(name: str) -> CloudTypeHelpers:
    for h in g_cloud_types.values():
        if name.lower() == h.name:
            return h
    raise ValueError('cloud type: {0} does not exist'.format(name))