from PIL import Image
import numpy as np
from enum import Enum
from itemcloud.box import Box
from itemcloud.size import Size
from itemcloud.native.display_map import (
    native_write_to_margined_item,
    native_write_to_target,
    native_find_expanded_box,
    native_can_fit_on_target
)
DISPLAY_MAP_SIZE_TYPE = tuple[int, int]
DISPLAY_NP_DATA_TYPE = np.uint32
DISPLAY_MAP_TYPE = np.ndarray[DISPLAY_NP_DATA_TYPE, DISPLAY_NP_DATA_TYPE]
DISPLAY_BUFFER_TYPE = np.ndarray[DISPLAY_NP_DATA_TYPE]

def from_displaymap_size(display_map_shape: DISPLAY_MAP_SIZE_TYPE) -> Size:
    return Size(display_map_shape[1], display_map_shape[0]) # columns == width, rows == height

def to_displaymap_size(size: Size) -> DISPLAY_MAP_SIZE_TYPE:
    return (size.height, size.width) # height == rows, width == cols

def from_displaymap_box(display_map_shape: DISPLAY_MAP_SIZE_TYPE) -> Box:
    return Box(0, 0, display_map_shape[1], display_map_shape[0])

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
    result = create_display_map(from_displaymap_size((item.shape[0] + (margin * 2), item.shape[1] + (margin * 2))), map_fill_type.value)
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
    return _find_expanded_box(item, target, box, direction)
    #return Box.from_native(native_find_expanded_box(item, target, box, direction))

def can_fit_on_target(item: DISPLAY_MAP_TYPE, target: DISPLAY_MAP_TYPE, target_item_box: Box, item_window: Box) -> bool:
    return 0 != native_can_fit_on_target(item, target, target_item_box.to_native(), item_window.to_native())

def _find_expanded_box(item: DISPLAY_MAP_TYPE, target: DISPLAY_MAP_TYPE, box: Box, direction: Direction) -> Box:
    target_box: Box = from_displaymap_box(target.shape)
    target_size: Size = target_box.size
    item_window: Box = from_displaymap_box(item.shape)
    edge: Box = Box(box.left, box.upper, box.right, box.lower)
    margined_item: Box = Box(box.left, box.upper, box.right, box.lower)

    if Direction.LEFT == direction: # widen more to LEFT
        edge = Box(box.left, box.upper, box.left, box.lower)
        for left in range(edge.left - 1, -1, -1):
            edge.left = left
            if target_box.contains(edge):
                break
            elif can_fit_on_target(item, target, edge, item_window):
                margined_item.left = edge.left
                break

    elif Direction.UP == direction: # lengthen more UPward
        edge = Box(box.left, box.upper, box.right, box.upper)
        for upper in range(edge.upper - 1, -1, -1):
            edge.upper = upper
            if target_box.contains(edge):
                break
            elif can_fit_on_target(item, target, edge, item_window):
                margined_item.upper = edge.upper
                break

    elif Direction.RIGHT == direction: # widen more to RIGHT
        edge = Box(box.right, box.upper, box.right, box.lower)
        item_window.left = item_window.right - 1
        for right in range(edge.right + 1, target_size.width):
            edge.right = right
            if target_box.contains(edge):
                break
            elif can_fit_on_target(item, target, edge, item_window):
                margined_item.right = edge.right
                break

    elif Direction.DOWN == direction: # lengthen more DOWNward
        edge = Box(box.left, box.lower, box.right, box.lower)
        item_window.upper = item_window.lower - 1
        for lower in range(edge.lower + 1, target_size.height):
            edge.lower = lower
            if target_box.contains(edge):
                break
            elif can_fit_on_target(item, target, edge, item_window):
                margined_item.lower = edge.lower
                break

    return margined_item


def _can_fit_on_target(item: DISPLAY_MAP_TYPE, target: DISPLAY_MAP_TYPE, target_item_box: Box, item_window: Box) -> bool:
    target_item_row: int = target_item_box.upper
    target_item_col: int = target_item_box.left
    item_rows: int = item_window.height
    item_cols: int = item_window.width

    # is_outside_target
    if target.shape[0] < (target_item_row + item.shape[0]) or target.shape[1] < (target_item_col + item.shape[1]):
        return 0

    for item_row in range(item_rows):
        for item_col in range(item_cols):
            # can_overlap
            if item[item_window.upper + item_row, item_window.left + item_col] == 0 or target[target_item_row + item_row, target_item_col + item_col] == 0:
                return 0

    return 1