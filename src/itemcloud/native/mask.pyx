# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# distutils: language = c++
# distutils: extra_compile_args = -std=c++11
cimport cython
from itemcloud.native.math cimport rounded_division

cdef int is_outside_target(
    unsigned int[:,:] mask,
    unsigned int[:,:] target,
    int target_row,
    int target_col
) noexcept nogil:
    cdef int mask_rows = mask.shape[0]
    cdef int mask_cols = mask.shape[1]
    cdef int row = target_row + mask_rows
    cdef int col = target_col + mask_cols
    if target.shape[0] < row:
        return 1
    if target.shape[1] < col:
        return 1
    return 0

cdef int can_overlap(
    unsigned int mask,
    unsigned int target
) noexcept nogil:
    if mask == 0 or target == 0:
        return 1
    return 0

cdef int can_fit_on_target(
    unsigned int[:,:] mask,
    unsigned int[:,:] target,
    int target_row,
    int target_col
) noexcept nogil:
    cdef int mask_row = 0
    cdef int mask_col = 0
    cdef int mask_rows = mask.shape[0]
    cdef int mask_cols = mask.shape[1]
    cdef int row = 0
    cdef int col = 0
    if is_outside_target(mask, target, row, col):
        return 0
    for mask_row in range(mask_rows):
        for mask_col in range(mask_cols):
            row = target_row + mask_row
            col = target_col = mask_col
            if 0 != can_overlap(mask[mask_row, mask_col], target[row, col]):
                return 0
    return 1



cdef int write_to_target(
    unsigned int[:,:] mask,
    unsigned int[:,:] target,
    int target_row,
    int target_col,
    unsigned int mask_id
) noexcept nogil:
    cdef int mask_row = 0
    cdef int mask_col = 0
    cdef int mask_rows = mask.shape[0]
    cdef int mask_cols = mask.shape[1]
    cdef int row = 0
    cdef int col = 0
    cdef unsigned int value = mask_id
    for mask_row in range(mask_rows):
        for mask_col in range(mask_cols):
            if mask[mask_row, mask_col] != 0:
                row = target_row + mask_row
                col = target_col = mask_col
                target[row, col] = value

cdef void write_to_margined_mask(
    unsigned int[:,:] mask,
    unsigned int[:,:] margined_mask
) noexcept nogil:
    cdef int row = 0
    cdef int col = 0
    cdef int mask_rows = mask.shape[0]
    cdef int mask_cols = mask.shape[1]
    cdef int margined_rows = margined_mask.shape[0]
    cdef int margined_cols = margined_mask.shape[1]
    cdef int padding = rounded_division(margined_rows - mask_rows, 2)
    cdef int break_rows = 0
    cdef int i = 0

    # set passed mask into shape padding distance into shape
    for row in range(mask_rows):
        for col in range(mask_cols):
            margined_mask[padding + row, padding + col] = mask[row,col]
    
    # ensure padding distance from 1st non transparent item is filled
    # left to right, top to bottom area of image
    break_rows = 0
    for row in range(margined_rows):
        for col in range(margined_cols):
            if margined_mask[row + padding, col] == 1:
                for i in range(padding):
                    margined_mask[row + i, col] = 1;
                break_rows = 1
            if margined_mask[row, col + padding] == 1:
                for i in range(padding):
                    margined_mask[row, col + i] = 1;
                break
        if 1 == break_rows:
            break
    # right to left, bottom to top area of image
    break_rows = 0
    for row in range(margined_rows - 1, 0, -1):
        for col in range(margined_cols - 1, 0, -1):
            if margined_mask[row - padding, col] == 1:
                for i in range(padding):
                    margined_mask[row - i, col] = 1;
                break_rows = 1
            if margined_mask[row, col - padding] == 1:
                for i in range(padding):
                    margined_mask[row, col - i] = 1;
                break
        if 1 == break_rows:
            break

def native_write_to_margined_mask(unsigned int[:,:] mask, unsigned int[:,:] margined_mask): # return nothing
    write_to_margined_mask(mask, margined_mask)