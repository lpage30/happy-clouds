# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
from itemcloud.native.box cimport Box
from itemcloud.native.math cimport distance

cdef int box_center_x(Box self) noexcept nogil

cdef int box_center_y(Box self) noexcept nogil

cdef inline double origin_distance(int origin_x, int origin_y, Box target) noexcept nogil:
    return distance(origin_x, origin_y, box_center_x(target), box_center_y(target))

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

cdef RelativePosition relative_position(int origin_x, int origin_y, int item_x, int item_y) noexcept nogil

cdef inline RelativePosition box_relative_position(int origin_x, int origin_y, Box item) noexcept nogil:
    return relative_position(origin_x, origin_y, box_center_x(item), box_center_y(item))

cdef inline RelativePosition box_relative_position_to_box(Box origin, Box item) noexcept nogil:
    return relative_position(box_center_x(origin), box_center_y(item), box_center_x(item), box_center_y(item))

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

cdef struct SearchProperties:
    Box area
    int origin_x
    int origin_y
    SearchPattern pattern
    int loop
    RelativePosition positions[3]
    RelativeDistance distance

cdef void set_search_positions(SearchProperties* search, RelativePosition one=*, RelativePosition two=*, RelativePosition three=*) noexcept nogil
cdef inline int search_positions_len(SearchProperties* search) noexcept nogil:
    cdef int result = 0
    if search[0].positions[0] == RelativePosition.NO_POSITION:
        return result
    result = result + 1
    if search[0].positions[1] == RelativePosition.NO_POSITION:
        return result
    result = result + 1
    if search[0].positions[2] == RelativePosition.NO_POSITION:
        return result
    result = result + 1
    return result

cdef inline int contains_search_position(SearchProperties* search, RelativePosition position) noexcept nogil:
    if search[0].positions[0] == position:
        return 1
    if search[0].positions[1] == position:
        return 1
    if search[0].positions[2] == position:
        return 1
    return 0

    
cdef SearchProperties start_search(
    Box area,
    SearchPattern pattern
) noexcept nogil

cdef Box search(Box[::1] boxes, SearchProperties properties) noexcept nogil

cdef SearchProperties next_search(Box last_found, SearchProperties last_properties) noexcept nogil
