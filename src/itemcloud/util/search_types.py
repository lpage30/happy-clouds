from enum import Enum

class RelativePosition(Enum):
    NO_POSITION = -1
    RANDOM = 0
    LEFT = 1
    RIGHT = 2
    TOP = 3
    BOTTOM = 4
    TOP_LEFT = 5
    TOP_RIGHT = 6
    BOTTOM_LEFT = 7
    BOTTOM_RIGHT = 8

class RelativeDistance(Enum):
    RANDOM = 0
    CLOSEST = 1
    FARTHEST = 2

class SearchPattern(Enum):
    NONE = 0
    RANDOM = 1
    LINEAR = 2
    RAY = 3
    SPIRAL = 4


SEARCH_PATTERNS = [p.name for p in SearchPattern]
