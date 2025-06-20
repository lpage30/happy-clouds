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
    unsigned int target,
    unsigned int item_id
) noexcept nogil:
    if item == 0 or target == 0 or target == item_id:
        return 1
    return 0

cdef int can_fit_on_target(
    DISPLAY_MAP_TYPE item,
    DISPLAY_MAP_TYPE target,
    Box target_item_box,
    unsigned int item_id
) noexcept nogil:
    cdef int item_row = 0
    cdef int item_col = 0
    cdef int target_item_row = box_top_corner_row(target_item_box)
    cdef int target_item_col = box_top_corner_col(target_item_box)
    cdef int item_rows = item.shape[0]
    cdef int item_cols = item.shape[1]

    if is_outside_target(item, target, target_item_row, target_item_col):
        return 0
    for item_row in range(item_rows):
        for item_col in range(item_cols):
            if 0 == can_overlap(
                item[item_row, item_col], 
                target[target_item_row + item_row, target_item_col + item_col],
                item_id
            ):
                return 0

    return 1

cdef void write_to_target(
    DISPLAY_MAP_TYPE item,
    DISPLAY_MAP_TYPE target,
    int target_row,
    int target_col,
    unsigned int item_id
) noexcept nogil:
    cdef int item_row = 0
    cdef int item_col = 0
    cdef int item_rows = item.shape[0]
    cdef int item_cols = item.shape[1]
    cdef int row = 0
    cdef int col = 0
    cdef unsigned int value = item_id
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


def native_can_fit_on_target(
    DISPLAY_MAP_TYPE item,
    DISPLAY_MAP_TYPE target,
    Box target_item_box,
    unsigned int item_id,
):
    return can_fit_on_target(item, target, target_item_box, item_id)

def native_write_to_margined_item(DISPLAY_MAP_TYPE item, DISPLAY_MAP_TYPE margined_item): # return nothing
    write_to_margined_item(item, margined_item)

def native_write_to_target(DISPLAY_MAP_TYPE item, DISPLAY_MAP_TYPE target, int target_row, int target_col, unsigned int item_id):
    write_to_target(item, target, target_row, target_col, item_id)
