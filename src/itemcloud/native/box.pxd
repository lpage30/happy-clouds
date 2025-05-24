# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
from itemcloud.native.size cimport Size
from itemcloud.native.math cimport (randint, RotateDirection)

ctypedef struct Box:
    int left
    int upper
    int right
    int lower

cdef Box create_box(int left, int upper, int right, int lower) noexcept nogil

cdef const char* box_to_string(Box self) noexcept nogil
cdef int box_area(Box self) noexcept nogil
cdef Size size(Box self) noexcept nogil
cdef int box_equals(Box self, Box other) noexcept nogil

cdef Box empty_box() noexcept nogil
cdef int is_empty(Box self) noexcept nogil

cdef int contains(Box self, Box other) noexcept nogil
cdef Box add_margin(Box self, int margin) noexcept nogil
cdef Box remove_margin(Box self, int margin) noexcept nogil

cdef Box rotate(Box self, int degrees, RotateDirection direction) noexcept nogil

cdef Box[::1] create_box_array(int length) noexcept

cdef inline Box randomly_pick_one(Box[::1] boxes) noexcept nogil:
    return boxes[randint(boxes.shape[0], -1)]

