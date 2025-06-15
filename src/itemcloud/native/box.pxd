# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
from itemcloud.native.size cimport Size, create_size
from itemcloud.native.math cimport (randint, RotateDirection)

ctypedef struct Box:
    int left
    int upper
    int right
    int lower

cdef Box create_box(int left, int upper, int right, int lower) noexcept nogil

cdef inline int box_width(Box self) noexcept nogil:
    return self.right - self.left

cdef inline int box_height(Box self) noexcept nogil:
    return self.lower - self.upper

cdef inline int box_area(Box self) noexcept nogil:
    return box_width(self) * box_height(self)

cdef inline Box box_from_size(Size size) noexcept nogil:
    return create_box(0, 0, size.width, size.height)

cdef inline Size size_from_box(Box box) noexcept nogil:
    return create_size(
        box_width(box),
        box_height(box)
    )

cdef const char* box_to_string(Box self) noexcept nogil
cdef int box_area(Box self) noexcept nogil
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

