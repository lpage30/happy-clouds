# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False

cdef enum RelativePosition:
    NO_POSITION = -1
    RANDOM_POSITION = 0
    LEFT_POSITION = 1
    RIGHT_POSITION = 2
    TOP_POSITION = 3
    BOTTOM_POSITION = 4
    TOP_LEFT_POSITION = 5
    TOP_RIGHT_POSITION = 6
    BOTTOM_LEFT_POSITION = 7
    BOTTOM_RIGHT_POSITION = 8

cdef enum RelativeDistance:
    RANDOM_DISTANCE = 0
    CLOSEST_DISTANCE = 1
    FARTHEST_DISTANCE = 2

cdef enum SearchPattern:
    NO_PATTERN = 0
    RANDOM_PATTERN = 1
    LINEAR_PATTERN = 2
    RAY_PATTERN = 3
    SPIRAL_PATTERN = 4

cdef RelativePosition randpos() noexcept nogil
cdef SearchPattern randpattern() noexcept nogil