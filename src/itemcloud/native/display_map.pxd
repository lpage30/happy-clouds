# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
from itemcloud.native.size cimport Size, create_size
from itemcloud.native.box cimport Box, create_box

ctypedef (int, int) DISPLAY_MAP_SIZE_TYPE
ctypedef unsigned int[:,:] DISPLAY_MAP_TYPE
ctypedef unsigned int[:] DISPLAY_BUFFER_TYPE

cdef inline Size from_displaymap_size(DISPLAY_MAP_TYPE display_map) noexcept nogil:
    return create_size(display_map.shape[1], display_map.shape[0]) # cols == width, rows == height

cdef inline DISPLAY_MAP_SIZE_TYPE to_displaymap_size(Size size) noexcept nogil:
    cdef DISPLAY_MAP_SIZE_TYPE result = (size.height, size.width) # height == rows, width == cols
    return result

cdef inline int box_top_corner_row(Box box) noexcept nogil:
    return box.upper

cdef inline int box_bottom_corner_row(Box box) noexcept nogil:
    return box.lower

cdef inline int box_top_corner_col(Box box) noexcept nogil:
    return box.left

cdef inline int box_bottom_corner_col(Box box) noexcept nogil:
    return box.right

cdef inline Box from_displaymap_box(DISPLAY_MAP_TYPE display_map) noexcept nogil:
    return create_box(0,0, display_map.shape[1], display_map.shape[0]) # cols == width, rows == height

cdef int is_outside_target(
    DISPLAY_MAP_TYPE item,
    DISPLAY_MAP_TYPE target,
    int target_row,
    int target_col
) noexcept nogil

cdef int can_overlap(
    unsigned int item,
    unsigned int target,
    unsigned int item_id
) noexcept nogil


cdef int can_fit_on_target(
    DISPLAY_MAP_TYPE item,
    DISPLAY_MAP_TYPE target,
    Box target_item_box,
    unsigned int item_id
) noexcept nogil

cdef void write_to_target(
    DISPLAY_MAP_TYPE item,
    DISPLAY_MAP_TYPE target,
    int target_row,
    int target_col,
    unsigned int item_id
) noexcept nogil

cdef void write_to_margined_item(
    DISPLAY_MAP_TYPE item,
    DISPLAY_MAP_TYPE margined_item
) noexcept nogil