from PIL import Image
import numpy as np
from enum import Enum
from itemcloud.native.mask import native_write_to_margined_mask
DISPLAY_NP_DATA_TYPE = np.uint32
DISPLAY_MAP_TYPE = np.ndarray[DISPLAY_NP_DATA_TYPE, DISPLAY_NP_DATA_TYPE]
DISPLAY_BUFFER_TYPE = np.ndarray[DISPLAY_NP_DATA_TYPE]

class MaskFillType(Enum):
    TRANSPARENT = 0
    OPAQUE = 1

def create_display_map(size: tuple[int, int], initial_value: int = 0) -> DISPLAY_MAP_TYPE:
    if 0 == initial_value:
        return np.zeros(size, dtype=DISPLAY_NP_DATA_TYPE)
    if 1 == initial_value:
        return np.ones(size, dtype=DISPLAY_NP_DATA_TYPE)
    return np.full(size, dtype=DISPLAY_NP_DATA_TYPE, fill_value=initial_value)

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

def img_to_display_mask(img: Image.Image, mask_fill_type: MaskFillType = MaskFillType.TRANSPARENT) -> DISPLAY_MAP_TYPE:
    result = create_display_map((img.width, img.height), 1)
    if mask_fill_type == MaskFillType.TRANSPARENT:
        if has_transparency(img):
            pixels = img.load()
            for x in range(img.width):
                for y in range(img.height):
                    if is_transparent(pixels[x, y]):
                        result[x,y] = 0
    return result

def size_to_display_mask(size: tuple[int, int]) -> DISPLAY_MAP_TYPE:
    return create_display_map(size, 1)

def add_margin_to_display_mask(mask: DISPLAY_MAP_TYPE, margin: int, mask_fill_type: MaskFillType) -> DISPLAY_MAP_TYPE:
    result = create_display_map((mask.shape[0] + margin, mask.shape[1] + margin), mask_fill_type.value)
    if mask_fill_type == MaskFillType.TRANSPARENT:
        native_write_to_margined_mask(mask, result)
    return result

def overlay_display_masks(mask1: DISPLAY_MAP_TYPE, mask2: DISPLAY_MAP_TYPE, return_size: tuple[int, int]) -> DISPLAY_MAP_TYPE:
    


