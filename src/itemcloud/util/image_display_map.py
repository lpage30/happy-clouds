from PIL import Image
import numpy as np
from typing import Any
from itemcloud.box import Box

def has_transparency(img: Image.Image) -> bool:
    h,w,c = np.array(img).shape
    return True if c == 4 else False

def is_transparent(img_pixel) -> bool:
    return len(img_pixel) == 4 and 0 == img_pixel[3]

def img_to_display_matrix(img: Image.Image) -> np.ndarray[Any]:
    result = np.ones((img.width, img.height))
    if has_transparency(img):
        pixels = img.load()
        for x in range(img.width):
            for y in range(img.height):
                if len(pixels[x, y]) == 4 and 0 == pixels[x, y][3]:
                    result[x,y] = 0
    return result

def box_to_display_matrix(box: Box) -> np.ndarray[Any]:
    return np.ones((box.width, box.height))

