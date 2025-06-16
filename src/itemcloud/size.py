from __future__ import annotations
from itemcloud.native.size import (
    native_create_size,
    native_adjust
)
from itemcloud.util.parsers import parse_to_int
from enum import Enum

class ResizeType(Enum):
    NO_RESIZE_TYPE = -1
    MAINTAIN_ASPECT_RATIO = 1
    MAINTAIN_PERCENTAGE_CHANGE = 2

RESIZE_TYPES = [member.name for member in ResizeType]

def parse_to_resize_type(s: str) -> ResizeType:
    for member in ResizeType:
        if s.upper() == member.name:
            return member
    raise ValueError('{0} unsupported. Must be one of [{1}]'.format(s, '{0}'.format('|'.join(RESIZE_TYPES))))

class Size:

    def __init__(self, width: int, height: int) -> None:
        self._width = width
        self._height = height

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height
    
    @property
    def area(self) -> int:
        return int(round(self.width * self.height))
    
    def size_to_string(self) -> str:
        return f"Size({self.width}, {self.height})"

    def adjust(self, step: int, resize_type: ResizeType) -> Size:
        return Size.from_native(
            native_adjust(
                self.to_native_size(), 
                step,
                resize_type.value
            )
        )
    
    def scale(self, scale: float) -> Size:
        return Size(
            int(round(self.width * scale)),
            int(round(self.height * scale))
        )
    def is_equal(self, other) -> bool:
        return self.width == other.width and self.height == other.height
    
    def is_less_than(self, other) -> bool:
        return self.width < other.width or self.height < other.height
    
    def to_native_size(self):
        return native_create_size(self.width, self.height)
    
    @staticmethod
    def from_native(native_size) -> Size:
        return Size(native_size['width'], native_size['height'])
    
    @staticmethod
    def parse(s: str) -> Size:
        width, height = s.split(',')
        return Size(parse_to_int(width), parse_to_int(height))
    
