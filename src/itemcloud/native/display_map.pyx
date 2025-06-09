# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# distutils: language = c++
# distutils: extra_compile_args = -std=c++11
cimport cython
from itemcloud.native.box cimpot Box, size
from itemcloud.native.math cimport rounded_division
from itemcloud.native.size cimport Size, size_to_rows, size_to_cols

cdef int is_outside_target(
    DISPLAY_MAP_TYPE item,
    DISPLAY_MAP_TYPE target,
    int target_row,
    int target_col
) noexcept nogil:

    cdef int item_rows = display_map_rows(item)
    cdef int item_cols = display_map_cols(item)
    cdef int row = target_row + item_rows
    cdef int col = target_col + item_cols
    if display_map_rows(target) < row:
        return 1
    if display_map_cols(target) < col:
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
    cdef Size item_size = size(item_window)
    cdef int item_rows = item_size.height
    cdef int item_cols = item_size.width
    cdef int row = 0
    cdef int col = 0
    if is_outside_target(item, target, row, col):
        return 0
    for item_row in range(item_rows):
        for item_col in range(item_cols):
            row = target_item_row + item_row
            col = target_item_col = item_col
            if 0 != can_overlap(get_map_cell(item, item_window.upper + item_row, item_window.left + item_col), get_map_cell(target, row, col)):
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
    cdef int item_rows = display_map_rows(item)
    cdef int item_cols = display_map_cols(item)
    cdef int row = 0
    cdef int col = 0
    cdef unsigned int value = item_value
    for item_row in range(item_rows):
        for item_col in range(item_cols):
            if get_map_cell(item, item_row, item_col) != 0:
                row = target_row + item_row
                col = target_col = item_col
                set_map_cell(target, row, col, value)


cdef void write_to_margined_item(
    DISPLAY_MAP_TYPE item,
    DISPLAY_MAP_TYPE margined_item
) noexcept nogil:
    cdef int row = 0
    cdef int col = 0
    cdef int item_rows = display_map_rows(item)
    cdef int item_cols = display_map_cols(item)
    cdef int margined_rows = display_map_rows(margined_item)
    cdef int margined_cols = display_map_cols(margined_item)
    cdef int padding = rounded_division(margined_rows - item_rows, 2)
    cdef int break_rows = 0
    cdef int i = 0

    # set passed item into shape padding distance into shape
    for row in range(item_rows):
        for col in range(item_cols):
            set_map_cell(margined_item, padding + row, padding + col, get_map_cell(item, row,col))
    
    # ensure padding distance from 1st non transparent item is filled
    # left to right, top to bottom area of image
    break_rows = 0
    for row in range(margined_rows):
        for col in range(margined_cols):
            if get_map_cell(margined_item, row + padding, col) == 1:
                for i in range(padding):
                    set_map_cell(margined_item[row + i, col, 1);
                break_rows = 1
            if get_map_cell(margined_item, row, col + padding) == 1:
                for i in range(padding):
                    set_map_cell(margined_item, row, col + i, 1);
                break
        if 1 == break_rows:
            break
    # right to left, bottom to top area of image
    break_rows = 0
    for row in range(margined_rows - 1, 0, -1):
        for col in range(margined_cols - 1, 0, -1):
            if get_map_cell(margined_item[row - padding, col) == 1:
                for i in range(padding):
                    set_map_cell(margined_item[row - i, col, 1);
                break_rows = 1
            if get_map_cell(margined_item[row, col - padding) == 1:
                for i in range(padding):
                    set_map_cell(margined_item, row, col - i, 1);
                break
        if 1 == break_rows:
            break

cdef Box find_expanded_box(
    DISPLAY_MAP_TYPE item,
    DISPLAY_MAP_TYPE target,
    Box box,
    Direction direction
) noexcept nogil:
    cdef Box target_box = display_map_box(target)
    cdef Box item_window = display_map_box(item)
    cdef Box edge = create_box(box.left, box.upper, box.right, box.lower)
    cdef Box result = create_box(box.left, box.upper, box.right, box.lower)

    if Direction.LEFT == direction: # left
        item_window = display_map_box(item)
        edge = create_box(box.left, box.upper, box.left, box.lower)
        for col in range(edge.left - 1, -1, -1):
            edge.left = col
            if 0 == contains(target_box, edge):
                break
            elif 0 != can_fit_on_target(item, target, edge, item_window):
                result.left = edge.left
                break
    elif Direction.UP == direction: # UP
        item_window = display_map_box(item)
        edge = create_box(box.left, box.upper, box.right, box.upper)
        for row in range(edge.upper - 1, -1, -1):
            edge.upper = row
            if 0 == contains(self.map_box, edge):
                break
            elif 0 != can_fit_on_target(item, target, edge, item_window):
                result.upper = edge.upper
                break
    elif Direction.RIGHT == direction: # right
        edge = create_box(box.right, box.upper, box.right, box.lower)
        item_window = display_map_box(item)
        item_window.left = item.right - 1
        for col in range(edge.right + 1, self.map_size.width):
            edge.right = col
            if 0 == contains(self.map_box, edge):
                break
            elif 0 != can_fit_on_target(item, target, edge, item_window):
                result.right = edge.right
                break
    elif Direction.DOWN == direction: # Down
        edge = create_box(box.left, box.lower, box.right, box.lower)
        item_window = display_map_box(item)
        item_window.upper = item.lower - 1
        for row in range(edge.lower + 1, self.map_size.height):
            edge.lower = row
            if 0 == contains(self.map_box, edge):
                break
            elif 0 != can_fit_on_target(item, target, edge, item_window):
                result.lower = edge.lower
                break
    return result



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
