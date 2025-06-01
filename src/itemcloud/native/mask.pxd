# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False


cdef int is_outside_target(
    unsigned int[:,:] mask,
    unsigned int[:,:] target,
    int target_row,
    int target_col
) noexcept nogil

cdef int can_overlap(
    unsigned int mask,
    unsigned int target
) noexcept nogil

cdef int can_fit_on_target(
    unsigned int[:,:] mask,
    unsigned int[:,:] target,
    int target_row,
    int target_col
) noexcept nogil

cdef int write_to_target(
    unsigned int[:,:] mask,
    unsigned int[:,:] target,
    int target_row,
    int target_col,
    unsigned int mask_id
) noexcept

