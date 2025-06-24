import argparse
from enum import Enum
import os
from typing import List
from itemcloud.size import Size

def existing_path(parser: argparse.ArgumentParser, path_type: str, value: str, return_value: str | None = None) -> str:
    if not os.path.exists(value):
        parser.error(f"{path_type} {value} does not exist!")
    return value if return_value is None else return_value

def in_array(parser: argparse.ArgumentParser, arr: List[str], value: str) -> str:
    if value in arr:
        return value
    else:
        parser.error('Invalid value {0} must be one of [{1}]'.format(value, ','.join(arr)))


def is_size(parser: argparse.ArgumentParser, value: str) -> Size:
    try:
        return Size.parse(value)
    except Exception as e:
        parser.error(str(e))


def is_integer(parser: argparse.ArgumentParser, value: str) -> int:
    if value is None or not(value.isdigit()):
        parser.error('Invalid value {0} must be a number'.format(value))
    return int(value)

def is_float(parser: argparse.ArgumentParser, value: str) -> float:
    if value is None or not(value.replace('.','',1).isdigit()):
        parser.error('Invalid value {0} must be a number'.format(value))
    return float(value)

def is_enum(parser: argparse.ArgumentParser, enum_type: Enum, value: str) -> Enum:
    for m in enum_type:
        if value.upper() == m.name:
            return m
    parser.error('{0} unsupported. Must be one of [{1}]'.format(value, '|'.join([m.name for m in enum_type])))
    
    
def create_name(
        input_filepath: str,
        output_image_format: str,
        output_directory: str | None,
        specific_name: str | None = None
) -> str:
    name = specific_name if specific_name is not None else os.path.splitext(os.path.basename(input_filepath))[0]
    if output_directory is not None:
        name = os.path.splitext(os.path.basename(
            to_unused_filepath(output_directory, name, output_image_format)
        ))[0]
    return name

def to_unused_filepath(directory: str, name: str, suffix: str) -> str:
    filepath_prefix = os.path.join(directory, name)
    result = '{0}.{1}'.format(filepath_prefix, suffix)
    version: int = 0
    while os.path.isfile(result):
        version += 1
        result = '{0}.{1}.{2}'.format(filepath_prefix, version, suffix)
    return result