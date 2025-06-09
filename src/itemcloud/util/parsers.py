import os.path
from typing import Dict, Any, List, Callable

def parse_to_int(s:str) -> int:
    if s == None or not(s.isdigit()):
        raise ValueError('Invalid value {0} must be a number'.fomat(s))
    return int(s)

def parse_to_float(s:str) -> float:
    if s == None or not(s.replace('.','',1).isdigit()):
        raise ValueError('Invalid value {0} must be a number'.fomat(s))
    return float(s)
    
def parse_to_existing_path(pathtype: str, value: str) -> str:
    if not os.path.exists(value):
        raise ValueError('The {0} {1} does not exist!'.format(pathtype, value))
    else:
        return value
    
def to_unused_filepath(directory: str, name: str, suffix: str) -> str:
    filepath_prefix = os.path.join(directory, name)
    result = '{0}.{1}'.format(filepath_prefix, suffix)
    version: int = 0
    while os.path.isfile(result):
        version += 1
        result = '{0}.{1}.{2}'.format(filepath_prefix, version, suffix)
    return result

def filepath_to_name(filepath: str) -> str:
    return os.path.splitext(os.path.basename(filepath))[0]

def is_empty(value: str | None) -> bool:
    return value in ['', None]

def to_existing_filepath(original_filepath: str, possible_dirnames: list[str] | str) -> str:
    basename = os.path.basename(original_filepath)
    possible_dirnames = [os.path.dirname(original_filepath), *possible_dirnames]
    tried_filepaths: list[str] = list()
    for dirname in possible_dirnames:
        filepath = os.path.join(dirname, basename)
        if os.path.exists(filepath):
            return filepath
        tried_filepaths.append(filepath)
    
    raise ValueError('The file {0} does not exist! (Tried [{1}])'.format(original_filepath, ', '.join(tried_filepaths)))

def field_exists(field_name: str, row: Dict[str, Any]) -> bool:
    return field_name in row and not(is_empty(row[field_name]))

def get_value_or_default(field_name: str, row: Dict[str, Any], default: Any, value_f: Callable[[Any], Any] | None = None) -> Any:
    if field_exists(field_name, row):
        return value_f(row[field_name]) if value_f is not None else row[field_name] 
    return default

def get_complex_value_or_default(field_names: List[str], row: Dict[str, Any], default: Any, value_f: Callable[[List[Any]], Any]) -> Any:
    if all([field_exists(name, row) for name in field_names]):
        return value_f([row[name] for name in field_names])
    return default


def validate_row(row: Dict[str, Any], field_names: List[str]) -> None:
    for field in field_names:
        if not(field_exists(field, row)):
            raise ValueError('{0} missing from data.'.format(field))