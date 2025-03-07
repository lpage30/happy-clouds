from enum import Enum
from itemcloud.size import Size
from itemcloud.native.box import native_create_box, native_rotate_box

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
        return self.size.width
    @property
    def height(self) -> int:
        return self.size.height
    # see definition of 'box': https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.paste

    @property
    def image_tuple(self) -> tuple[int, int, int, int]:
        return (self.left, self.upper, self.right, self.lower)
    
    @property
    def area(self) -> int:
        return self.size.area
    
    def scale(self, scale: float) -> "Box":
        return Box(
            int(round(self.left * scale)),
            int(round(self.upper * scale)),
            int(round(self.right * scale)),
            int(round(self.lower * scale))
        )
    def copy_box(self) -> "Box":
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
    
    def remove_margin(self, margin: int) -> "Box":
        padding = int(round(margin/2))
        return Box(
            self.left + padding,
            self.upper + padding,
            self.right - padding,
            self.lower - padding
        )
    
    def is_wedged(self, bounding: "Box") -> bool:
        # a box is wedged when it is twisted so it hits its bounding box
        return (
            self.upper <= bounding.upper or
            self.lower >= bounding.lower or
            self.left <= bounding.left or
            self.right >= bounding.right
        )

    def rotate(self, degrees: float, direction: RotateDirection = RotateDirection.CLOCKWISE) -> "Box":
        native_box = native_rotate_box(self.to_native(), degrees, direction.value)
        return Box.from_native(native_box)
    
    def rotate_until_wedged(self, bounding: "Box", direction: RotateDirection = RotateDirection.CLOCKWISE) -> float:
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
    def from_native(native_box) -> "Box":
        return Box(
            native_box['left'],
            native_box['upper'],
            native_box['right'],
            native_box['lower']
        )

def to_box(bbox: tuple[int, int, int, int]) -> Box:
    return Box(bbox[0], bbox[1], bbox[2], bbox[3])