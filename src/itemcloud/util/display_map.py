import numpy as np
from enum import Enum
from itemcloud.box import Box
from itemcloud.size import Size
from itemcloud.native.display_map import (
    native_write_to_margined_item,
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

def size_to_display_map(size: Size) -> DISPLAY_MAP_TYPE:
    return create_display_map(size, 1)

def add_margin_to_display_map(item: DISPLAY_MAP_TYPE, margin: int, map_fill_type: MapFillType = MapFillType.TRANSPARENT) -> DISPLAY_MAP_TYPE:
    result = create_display_map(from_displaymap_size((item.shape[0] + (margin * 2), item.shape[1] + (margin * 2))), map_fill_type.value)
    if map_fill_type == MapFillType.TRANSPARENT:
        native_write_to_margined_item(item, result)
    return result

def write_display_map(item: DISPLAY_MAP_TYPE, target: DISPLAY_MAP_TYPE, target_location: Box, item_value: int):
    plots = _write_to_target(item, target, target_location, item_value)
    if plots == 0:
        raise ValueError('Nothin')

def can_fit_on_target(item: DISPLAY_MAP_TYPE, target: DISPLAY_MAP_TYPE, target_item_box: Box, item_id: int | None = None, ) -> bool:
    return 0 != native_can_fit_on_target(item, target, target_item_box.to_native(), item_id if item_id is not None else 0)

def _write_to_target(item: DISPLAY_MAP_TYPE, target: DISPLAY_MAP_TYPE, target_location: Box, item_id: int) -> int:
    target_row = target_location.upper
    target_col = target_location.left
    result = 0
    for item_row in range(item.shape[0]):
        for item_col in range(item.shape[1]):
            if item[item_row, item_col] != 0:
                result += 1
                target[target_row + item_row, target_col + item_col] = item_id
    return result
