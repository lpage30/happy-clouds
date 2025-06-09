from __future__ import annotations
from enum import Enum
from typing import List
from itemcloud.size import Size
from itemcloud.native.box import (
    native_create_box,
    native_rotate_box,
    native_create_box_array,
    native_set_box_element,
    native_box_array_length,
    native_get_box_element
)

class RotateDirection(Enum):
    COUNTERCLOCKWISE = -1
    CLOCKWISE = 1

class Box:
    left: int
    upper: int
    right: int
    lower: int
    size: Size
    
    def __init__(self, left: int, upper: int, right: int, lower: int) -> None:
        self.left = left
        self.upper = upper
        self.right = right
        self.lower = lower
        self.size = Size(right - left, lower - upper)
    
    @property
    def width(self) -> int:
        return self.right - self.left
    @property
    def height(self) -> int:
        return self.lower - self.upper
    
    @property
    def size(self) -> Size:
        return Size(self.width, self.height)
    
    # see definition of 'box': https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.paste

    @property
    def image_tuple(self) -> tuple[int, int, int, int]:
        return (self.left, self.upper, self.right, self.lower)
    
    @property
    def area(self) -> int:
        return self.size.area
    
    def scale(self, scale: float) -> Box:
        return Box(
            int(round(self.left * scale)),
            int(round(self.upper * scale)),
            int(round(self.right * scale)),
            int(round(self.lower * scale))
        )
    def copy_box(self) -> Box:
        return Box(
            self.left,
            self.upper,
            self.right,
            self.lower
        )
    
    def equals(self, other) -> bool:
        return (
            self.left == other.left and
            self.upper == other.upper and
            self.right == other.right and
            self.lower == other.lower
        )
    def contains(self, other) -> bool:
        return (self.left <= other.left and self.upper <= other.upper and 
            self.right >= other.right and self.lower >= other.lower)

    def box_to_string(self) -> str:
        return f'Box({self.left}, {self.upper}, {self.right}, {self.lower})'
    
    def remove_margin(self, margin: int) -> Box:
        padding = int(round(margin/2))
        return Box(
            self.left + padding,
            self.upper + padding,
            self.right - padding,
            self.lower - padding
        )
    
    def is_wedged(self, bounding: Box) -> bool:
        # a box is wedged when it is twisted so it hits its bounding box
        return (
            self.upper <= bounding.upper or
            self.lower >= bounding.lower or
            self.left <= bounding.left or
            self.right >= bounding.right
        )

    def resize(self, size: tuple[int, int]) -> Box:
        return Box(
            self.left,
            self.upper,
            self.left + size[0],
            self.upper + size[1]
        )
    def rotate(self, degrees: float, direction: RotateDirection = RotateDirection.CLOCKWISE) -> Box:
        native_box = native_rotate_box(self.to_native(), degrees, direction.value)
        return Box.from_native(native_box)
    
    def rotate_until_wedged(self, bounding: Box, direction: RotateDirection = RotateDirection.CLOCKWISE) -> float:
        result = 0
        rotation_increment = 5
        box = self.copy_box()
        while not(box.is_wedged(bounding)):
            if 90 < (result + rotation_increment):
                break
            result = result + rotation_increment
            box = box.rotate(result, direction)
        return result
        

    
    def to_native(self):
        return native_create_box(
            self.left,
            self.upper,
            self.right,
            self.lower
        )
    
    @staticmethod
    def from_native(native_box) -> Box:
        return Box(
            native_box['left'],
            native_box['upper'],
            native_box['right'],
            native_box['lower']
        )

def to_box(bbox: tuple[int, int, int, int]) -> Box:
    return Box(bbox[0], bbox[1], bbox[2], bbox[3])

def to_native_box_array(boxes: List[Box]): # native_box_array
    native_box_array = native_create_box_array(len(boxes))
    for i in range(len(boxes)):
        native_set_box_element(native_box_array, i, boxes[i].to_native())
    return native_box_array

def from_native_box_array(native_box_array) -> List[Box]:
    result: List[Box] = list()
    for i in range(native_box_array_length(native_box_array)):
        result.append(Box.from_native(native_get_box_element(native_box_array, i)))
    return result