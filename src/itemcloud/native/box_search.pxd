# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
from itemcloud.native.box cimport Box
from itemcloud.native.math cimport distance
from itemcloud.native.search cimport RelativePosition, RelativeDistance, SearchPattern

cdef int box_center_x(Box self) noexcept nogil

cdef int box_center_y(Box self) noexcept nogil

cdef inline double origin_distance(int origin_x, int origin_y, Box target) noexcept nogil:
    return distance(origin_x, origin_y, box_center_x(target), box_center_y(target))

cdef RelativePosition relative_position(int origin_x, int origin_y, int item_x, int item_y) noexcept nogil

cdef inline RelativePosition box_relative_position(int origin_x, int origin_y, Box item) noexcept nogil:
    return relative_position(origin_x, origin_y, box_center_x(item), box_center_y(item))

cdef inline RelativePosition box_relative_position_to_box(Box origin, Box item) noexcept nogil:
    return relative_position(box_center_x(origin), box_center_y(item), box_center_x(item), box_center_y(item))

cdef struct BoxSearchProperties:
    Box area
    int origin_x
    int origin_y
    SearchPattern pattern
    int loop
    RelativePosition positions[3]
    RelativeDistance distance

cdef void set_search_positions(BoxSearchProperties* search, RelativePosition one=*, RelativePosition two=*, RelativePosition three=*) noexcept nogil
cdef inline int search_positions_len(BoxSearchProperties* search) noexcept nogil:
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

cdef inline int contains_search_position(BoxSearchProperties* search, RelativePosition position) noexcept nogil:
    if search[0].positions[0] == position:
        return 1
    if search[0].positions[1] == position:
        return 1
    if search[0].positions[2] == position:
        return 1
    return 0

    
cdef BoxSearchProperties start_search(
    Box area,
    SearchPattern pattern
) noexcept nogil

cdef Box search(Box[::1] boxes, BoxSearchProperties properties) noexcept nogil

cdef BoxSearchProperties next_search(Box last_found, BoxSearchProperties last_properties) noexcept nogil
