from PIL import Image
import numpy as np
from enum import Enum
from itemcloud.box import Box
from itemcloud.size import Size
from itemcloud.native.display_map import (
    native_write_to_margined_item,
    native_write_to_target,
    native_find_expanded_box
)
DISPLAY_MAP_SIZE_TYPE = tuple[int, int]
DISPLAY_NP_DATA_TYPE = np.uint32
DISPLAY_MAP_TYPE = np.ndarray[DISPLAY_NP_DATA_TYPE, DISPLAY_NP_DATA_TYPE]
DISPLAY_BUFFER_TYPE = np.ndarray[DISPLAY_NP_DATA_TYPE]

def from_displaymap_size(display_map: DISPLAY_MAP_TYPE) -> Size:
    return Size(display_map.shape[1], display_map.shape[0]) # columns == width, rows == height

def to_displaymap_size(size: Size) -> DISPLAY_MAP_SIZE_TYPE:
    return (size.height, size.width) # height == rows, width == cols

class MapFillType(Enum):
    TRANSPARENT = 0
    OPAQUE = 1

def create_display_map(size: Size, initial_value: int = 0) -> DISPLAY_MAP_TYPE:
    d_size: DISPLAY_MAP_SIZE_TYPE = to_displaymap_size(size)
    if 0 == initial_value:
        return np.zeros(d_size, dtype=DISPLAY_NP_DATA_TYPE)
    if 1 == initial_value:
        return np.ones(d_size, dtype=DISPLAY_NP_DATA_TYPE)
    return np.full(d_size, dtype=DISPLAY_NP_DATA_TYPE, fill_value=initial_value)

def create_display_buffer(length: int, initial_value: int = 0) -> DISPLAY_BUFFER_TYPE:
    if 0 == initial_value:
        return np.zeros((length), dtype=DISPLAY_NP_DATA_TYPE)
    if 1 == initial_value:
        return np.ones((length), dtype=DISPLAY_NP_DATA_TYPE)
    return np.full((length), dtype=DISPLAY_NP_DATA_TYPE, fill_value=initial_value)


def has_transparency(img: Image.Image) -> bool:
    h,w,c = np.array(img).shape
    return True if c == 4 else False

def is_transparent(img_pixel) -> bool:
    return len(img_pixel) == 4 and 0 == img_pixel[3]

def img_to_display_map(img: Image.Image, map_fill_type: MapFillType = MapFillType.TRANSPARENT) -> DISPLAY_MAP_TYPE:
    result = create_display_map(Size(img.width, img.height), 1)
    if map_fill_type == MapFillType.TRANSPARENT:
        if has_transparency(img):
            pixels = img.load()
            for x in range(img.width):
                for y in range(img.height):
                    if is_transparent(pixels[x, y]):
                        result[y,x] = 0 # y == rows, x == cols
    return result

def size_to_display_map(size: Size) -> DISPLAY_MAP_TYPE:
    return create_display_map(size, 1)

def add_margin_to_display_map(item: DISPLAY_MAP_TYPE, margin: int, map_fill_type: MapFillType = MapFillType.TRANSPARENT) -> DISPLAY_MAP_TYPE:
    result = create_display_map((item.shape[0] + (margin * 2), item.shape[1] + (margin * 2)), map_fill_type.value)
    if map_fill_type == MapFillType.TRANSPARENT:
        native_write_to_margined_item(item, result)
    return result

def write_display_map(item: DISPLAY_MAP_TYPE, target: DISPLAY_MAP_TYPE, target_location: Box, item_value: int):
    native_write_to_target(item, target, target_location.upper, target_location.left, item_value)
    
class Direction(Enum):
    LEFT = 0
    UP = 1
    RIGHT = 2
    DOWN = 3


def find_expanded_box(item: DISPLAY_MAP_TYPE, target: DISPLAY_MAP_TYPE, box: Box, direction: Direction) -> Box:
    return Box.from_native(native_find_expanded_box(item, target, box, direction))
