# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
from itemcloud.native.size cimport Size, create_size
from itemcloud.native.box cimport Box, create_box

ctypedef unsigned int[:,:] DISPLAY_MAP_TYPE
ctypedef unsigned int[:] DISPLAY_BUFFER_TYPE

cdef inline int display_map_rows(DISPLAY_MAP_TYPE display_map) noexcept nogil:
    return display_map.shape[0]

cdef inline int display_map_cols(DISPLAY_MAP_TYPE display_map) noexcept nogil:
    return display_map.shape[1]

cdef inline int display_map_height(DISPLAY_MAP_TYPE display_map) noexcept nogil:
    return display_map.shape[0]

cdef inline int display_map_width(DISPLAY_MAP_TYPE display_map) noexcept nogil:
    return display_map.shape[1]

cdef inline Box display_map_box(DISPLAY_MAP_TYPE display_map) noexcept nogil:
    return create_box(0, 0, display_map_cols(display_map), display_map_rows(display_map))

cdef inline Size display_map_size(
    DISPLAY_MAP_TYPE display_map
) noexcept nogil:
    return create_size(
        display_map_width(display_map),
        display_map_height(display_map)
    )

cdef inline int size_rows(Size self) noexcept nogil:
    return self.height

cdef inline int size_cols(Size self) noexcept nogil:
    return self.width

cdef inline unsigned int get_map_cell(
    DISPLAY_MAP_TYPE map,
    int row,
    int col
) noexcept nogil:
    return map[row, col]

cdef inline void set_map_cell(
    DISPLAY_MAP_TYPE map,
    int row,
    int col,
    unsigned int value
) noexcept nogil:
    map[row, col] = value

cdef inline unsigned int get_map_pt(
    DISPLAY_MAP_TYPE map,
    int x,
    int y
) noexcept nogil:
    return map[y, x]

cdef inline void set_map_pt(
    DISPLAY_MAP_TYPE map,
    int x,
    int y,
    unsigned int value
) noexcept nogil:
    map[y, x] = value

cdef int is_outside_target(
    DISPLAY_MAP_TYPE item,
    DISPLAY_MAP_TYPE target,
    int target_row,
    int target_col
) noexcept nogil

cdef int can_overlap(
    unsigned int item,
    unsigned int target
) noexcept nogil


cdef int can_fit_on_target(
    DISPLAY_MAP_TYPE item,
    DISPLAY_MAP_TYPE target,
    Box target_item_box,
    Box item_window
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

cdef enum Direction:
    LEFT = 0
    UP = 1
    RIGHT = 2
    DOWN = 3

cdef Box find_expanded_box(
    DISPLAY_MAP_TYPE item,
    DISPLAY_MAP_TYPE target,
    Box box,
    Direction direction
) noexcept nogil