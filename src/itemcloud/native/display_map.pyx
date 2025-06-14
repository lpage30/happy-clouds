# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# distutils: language = c++
# distutils: extra_compile_args = -std=c++11
cimport cython
from itemcloud.native.box cimport Box, size, contains
from itemcloud.native.math cimport rounded_division
from itemcloud.native.size cimport Size

cdef int is_outside_target(
    DISPLAY_MAP_TYPE item,
    DISPLAY_MAP_TYPE target,
    int target_row,
    int target_col
) noexcept nogil:
    if target.shape[0] < (target_col + item.shape[0]):
        return 1
    if target.shape[1] < (target_row + item.shape[1]):
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
    cdef int target_item_row = target_item_box.upper
    cdef int target_item_col = target_item_box.left
    cdef int item_rows = item_window.lower - item_window.upper
    cdef int item_cols = item_window.right - item_window.left
    if is_outside_target(item, target, target_item_row, target_item_col):
        return 0
    for item_row in range(item_rows):
        for item_col in range(item_cols):
            if 0 == can_overlap(item[item_window.left + item_col, item_window.upper + item_row], target[target_item_col + item_col, target_item_row + item_row]):
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
    cdef int item_rows = item.shape[1]
    cdef int item_cols = item.shape[0]
    cdef int row = 0
    cdef int col = 0
    cdef unsigned int value = item_value
    for item_row in range(item_rows):
        for item_col in range(item_cols):
            if item[item_col,item_row] != 0:
                row = target_row + item_row
                col = target_col = item_col
                target[col, row] = value


cdef void write_to_margined_item(
    DISPLAY_MAP_TYPE item,
    DISPLAY_MAP_TYPE margined_item
) noexcept nogil:
    cdef int row = 0
    cdef int prow = 0
    cdef int col = 0
    cdef int pcol = 0
    cdef int item_rows = item.shape[1]
    cdef int item_cols = item.shape[0]
    cdef int margined_rows = margined_item.shape[1]
    cdef int margined_cols = margined_item.shape[0]
    cdef int padding = rounded_division(margined_rows - item_rows, 2)
    cdef int i = 0

    # set passed item into shape padding distance into shape
    for row in range(item_rows):
        for col in range(item_cols):
            margined_item[col + padding, row + padding] = item[col, row]
    
    if margined_rows == item_rows and margined_cols == item_cols:
        return
    
    # left -> right for each row
    for row in range(margined_rows):
        for col in range(margined_cols):
            if margined_item[col, row] == 1:
                pcol = col - padding
                for i in range(padding):
                    margined_item[pcol + i, row] = 1
                break

    # right -> left for each row
    for row in range(margined_rows, 0, -1):
        for col in range(margined_cols, 0, -1):
            if margined_item[col, row] == 1:
                for i in range(padding):
                    margined_item[col + i, row] = 1
                break

    # upper -> lower for each row
    for col in range(margined_cols):
        for row in range(margined_rows):
            if margined_item[col, row] == 1:
                prow = row - padding
                for i in range(padding):
                    margined_item[col, prow + i] = 1
                break

    # lower -> upper for each row
    for col in range(margined_cols - 1, 0, -1):
        for row in range(margined_rows - 1, 0, -1):
            if margined_item[col, row] == 1:
                for i in range(padding):
                    margined_item[col, row + i] = 1
                break

cdef Box find_expanded_box(
    DISPLAY_MAP_TYPE item,
    DISPLAY_MAP_TYPE target,
    Box box,
    Direction direction
) noexcept nogil:
    cdef Box target_box = display_map_box(target)
    cdef Size target_size = size(target_box)
    cdef Box item_window = display_map_box(item)
    cdef Box edge = create_box(box.left, box.upper, box.right, box.lower)
    cdef Box margined_item = create_box(box.left, box.upper, box.right, box.lower)

    if Direction.LEFT == direction: # left
        item_window = display_map_box(item)
        edge = create_box(box.left, box.upper, box.left, box.lower)
        for col in range(edge.left - 1, -1, -1):
            edge.left = col
            if 0 == contains(target_box, edge):
                break
            elif 0 != can_fit_on_target(item, target, edge, item_window):
                margined_item.left = edge.left
                break
    elif Direction.UP == direction: # UP
        item_window = display_map_box(item)
        edge = create_box(box.left, box.upper, box.right, box.upper)
        for row in range(edge.upper - 1, -1, -1):
            edge.upper = row
            if 0 == contains(target_box, edge):
                break
            elif 0 != can_fit_on_target(item, target, edge, item_window):
                margined_item.upper = edge.upper
                break
    elif Direction.RIGHT == direction: # right
        edge = create_box(box.right, box.upper, box.right, box.lower)
        item_window = display_map_box(item)
        item_window.left = item_window.right - 1
        for col in range(edge.right + 1, target_size.width):
            edge.right = col
            if 0 == contains(target_box, edge):
                break
            elif 0 != can_fit_on_target(item, target, edge, item_window):
                margined_item.right = edge.right
                break
    elif Direction.DOWN == direction: # Down
        edge = create_box(box.left, box.lower, box.right, box.lower)
        item_window = display_map_box(item)
        item_window.upper = item_window.lower - 1
        for row in range(edge.lower + 1, target_size.height):
            edge.lower = row
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
