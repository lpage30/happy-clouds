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

class Direction(Enum):
    NO_DIRECTION = 0
    LEFT = 1
    UP = 2
    RIGHT = 3
    DOWN = 4

class Box:
    left: int
    upper: int
    right: int
    lower: int
    
    def __init__(self, left: int, upper: int, right: int, lower: int) -> None:
        self.left = left
        self.upper = upper
        self.right = right
        self.lower = lower
    
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
        return Box(
            self.left + margin,
            self.upper + margin,
            self.right - margin,
            self.lower - margin
        )
    def get_margin(self, larger: Box) -> int:
        width_margin = self.left - larger.left
        height_margin = self.upper - larger.upper
        if width_margin != height_margin:
            raise ValueError(f"Unexpected margin difference: width-margin({width_margin}) <> height-margin({height_margin})")
        return width_margin
    
    def is_wedged(self, bounding: Box) -> bool:
        # a box is wedged when it is twisted so it hits its bounding box
        return (
            self.upper <= bounding.upper or
            self.lower >= bounding.lower or
            self.left <= bounding.left or
            self.right >= bounding.right
        )

    def resize(self, size: Size) -> Box:
        return Box(
            self.left,
            self.upper,
            self.left + size.width,
            self.upper + size.height
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
    
    def expand(self, distance: int, direction: Direction) -> Box:
        if Direction.LEFT == direction:
            return Box(
                self.left - distance,
                self.upper,
                self.right,
                self.lower
            )
        elif Direction.UP == direction:
            return Box(
                self.left,
                self.upper - distance,
                self.right,
                self.lower
            )
        elif Direction.RIGHT == direction:
            return Box(
                self.left,
                self.upper,
                self.right + distance,
                self.lower
            )
        elif Direction.DOWN == direction:
            return Box(
                self.left,
                self.upper,
                self.right,
                self.lower + distance
            )
        return self

    def slide(self, distance: int, direction: Direction) -> Box:
        if Direction.LEFT == direction:
            return Box(
                self.left - distance,
                self.upper,
                self.right - distance,
                self.lower
            )
        elif Direction.UP == direction:
            return Box(
                self.left,
                self.upper - distance,
                self.right,
                self.lower - distance
            )
        elif Direction.RIGHT == direction:
            return Box(
                self.left + distance,
                self.upper,
                self.right + distance,
                self.lower
            )
        elif Direction.DOWN == direction:
            return Box(
                self.left,
                self.upper + distance,
                self.right,
                self.lower + distance
            )
        return self
    
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