# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# distutils: language = c++
# distutils: extra_compile_args = -std=c++11
cimport cython
from itemcloud.native.box cimport Box, size_from_box, contains, box_height, box_width
from itemcloud.native.math cimport rounded_division
from itemcloud.native.size cimport Size

#
# row == width == y
# col == height == x
#
# DISPLAY_MAP_TYPE[<row>,<col>]
#   shape = (<rows>, <cols>)
#  size = (<cols>, <rows>)
#

cdef int is_outside_target(
    DISPLAY_MAP_TYPE item,
    DISPLAY_MAP_TYPE target,
    int target_row,
    int target_col
) noexcept nogil:
    if target.shape[0] < (target_row + item.shape[0]):
        return 1
    if target.shape[1] < (target_col + item.shape[1]):
        return 1
    return 0

cdef int can_overlap(
    unsigned int item,
    unsigned int target
) noexcept nogil:
    if item == 0 or target == 0:
        return 1
    return 0

cdef int can_fit_on_target(
    DISPLAY_MAP_TYPE item,
    DISPLAY_MAP_TYPE target,
    Box target_item_box,
    Box item_window
) noexcept nogil:
    cdef int item_row = 0
    cdef int item_col = 0
    cdef int target_item_row = box_top_corner_row(target_item_box)
    cdef int target_item_col = box_top_corner_col(target_item_box)
    cdef int item_rows = box_height(item_window)
    cdef int item_cols = box_width(item_window)

    if is_outside_target(item, target, target_item_row, target_item_col):
        return 0
    for item_row in range(item_rows):
        for item_col in range(item_cols):
            if 0 == can_overlap(
                item[box_top_corner_row(item_window) + item_row, box_top_corner_col(item_window) + item_col], 
                target[target_item_row + item_row, target_item_col + item_col]
            ):
                return 0

    return 1

cdef void write_to_target(
    DISPLAY_MAP_TYPE item,
    DISPLAY_MAP_TYPE target,
    int target_row,
    int target_col,
    unsigned int item_value
) noexcept nogil:
    cdef int item_row = 0
    cdef int item_col = 0
    cdef int item_rows = item.shape[0]
    cdef int item_cols = item.shape[1]
    cdef int row = 0
    cdef int col = 0
    cdef unsigned int value = item_value
    for item_row in range(item_rows):
        for item_col in range(item_cols):
            if item[item_row, item_col] != 0:
                target[target_row + item_row, target_col + item_col] = value


cdef void write_to_margined_item(
    DISPLAY_MAP_TYPE item,
    DISPLAY_MAP_TYPE margined_item
) noexcept nogil:
    cdef int row = 0
    cdef int prow = 0
    cdef int col = 0
    cdef int pcol = 0
    cdef int item_rows = item.shape[0]
    cdef int item_cols = item.shape[1]
    cdef int margined_rows = margined_item.shape[0]
    cdef int margined_cols = margined_item.shape[1]
    cdef int padding = rounded_division(margined_rows - item_rows, 2)
    cdef int i = 0

    # set passed item into shape padding distance into shape
    for row in range(item_rows):
        for col in range(item_cols):
            margined_item[row + padding, col + padding] = item[row, col]
    
    if margined_rows == item_rows and margined_cols == item_cols:
        return
    
    # left -> right for each row
    for row in range(margined_rows):
        for col in range(margined_cols):
            if margined_item[row, col] == 1:
                pcol = col - padding
                for i in range(padding):
                    margined_item[row, pcol + i] = 1
                break

    # right -> left for each row
    for row in range(margined_rows, 0, -1):
        for col in range(margined_cols, 0, -1):
            if margined_item[row, col] == 1:
                for i in range(padding):
                    margined_item[row, col + i] = 1
                break

    # upper -> lower for each row
    for col in range(margined_cols):
        for row in range(margined_rows):
            if margined_item[row, col] == 1:
                prow = row - padding
                for i in range(padding):
                    margined_item[prow + i, col] = 1
                break

    # lower -> upper for each row
    for col in range(margined_cols - 1, 0, -1):
        for row in range(margined_rows - 1, 0, -1):
            if margined_item[row, col] == 1:
                for i in range(padding):
                    margined_item[row + i, col] = 1
                break

cdef Box find_expanded_box(
    DISPLAY_MAP_TYPE item,
    DISPLAY_MAP_TYPE target,
    Box box,
    Direction direction
) noexcept nogil:
    cdef Box target_box = from_displaymap_box(target)
    cdef Size target_size = size_from_box(target_box)
    cdef Box item_window = from_displaymap_box(item)
    cdef Box edge = create_box(box.left, box.upper, box.right, box.lower)
    cdef Box margined_item = create_box(box.left, box.upper, box.right, box.lower)
    cdef int left = 0
    cdef int right = 0
    cdef int upper = 0
    cdef int lower = 0

    if Direction.LEFT == direction: # widen more to LEFT
        edge = create_box(box.left, box.upper, box.left, box.lower)
        for left in range(edge.left - 1, -1, -1):
            edge.left = left
            if 0 == contains(target_box, edge):
                break
            elif 0 != can_fit_on_target(item, target, edge, item_window):
                margined_item.left = edge.left
                break

    elif Direction.UP == direction: # lengthen more UPward
        edge = create_box(box.left, box.upper, box.right, box.upper)
        for upper in range(edge.upper - 1, -1, -1):
            edge.upper = upper
            if 0 == contains(target_box, edge):
                break
            elif 0 != can_fit_on_target(item, target, edge, item_window):
                margined_item.upper = edge.upper
                break

    elif Direction.RIGHT == direction: # widen more to RIGHT
        edge = create_box(box.right, box.upper, box.right, box.lower)
        item_window.left = item_window.right - 1
        for right in range(edge.right + 1, target_size.width):
            edge.right = right
            if 0 == contains(target_box, edge):
                break
            elif 0 != can_fit_on_target(item, target, edge, item_window):
                margined_item.right = edge.right
                break

    elif Direction.DOWN == direction: # lengthen more DOWNward
        edge = create_box(box.left, box.lower, box.right, box.lower)
        item_window.upper = item_window.lower - 1
        for lower in range(edge.lower + 1, target_size.height):
            edge.lower = lower
            if 0 == contains(target_box, edge):
                break
            elif 0 != can_fit_on_target(item, target, edge, item_window):
                margined_item.lower = edge.lower
                break

    return margined_item



def native_write_to_margined_item(DISPLAY_MAP_TYPE item, DISPLAY_MAP_TYPE margined_item): # return nothing
    write_to_margined_item(item, margined_item)

def native_write_to_target(DISPLAY_MAP_TYPE item, DISPLAY_MAP_TYPE target, int target_row, int target_col, unsigned int item_value):
    write_to_target(item, target, target_row, target_col, item_value)

def native_find_expanded_box(
    DISPLAY_MAP_TYPE item,
    DISPLAY_MAP_TYPE target,
    Box box,
    int direction_value
) -> Box:
    cdef Direction direction = Direction.LEFT
    if direction_value == Direction.LEFT:
        direction =  Direction.LEFT
    elif direction_value == Direction.UP:
        direction =  Direction.UP
    elif direction_value == Direction.RIGHT:
        direction = Direction.RIGHT
    else:
        direction = Direction.DOWN

    return find_expanded_box(
        item,
        target,
        box,
        direction
    )
