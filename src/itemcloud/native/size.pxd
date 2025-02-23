# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
from itemcloud.native.box cimport RotateDirection

cdef enum ResizeType:
    NO_RESIZE_TYPE = -1
    MAINTAIN_ASPECT_RATIO = 1
    MAINTAIN_PERCENTAGE_CHANGE = 2

cdef ResizeType to_resize_type(int t) noexcept nogil

cdef struct Size:
    int width
    int height

cdef Size create_size(int width, int height) noexcept nogil

cdef const char* size_to_string(Size self) noexcept nogil

cdef int size_area(Size self) noexcept nogil

cdef int size_less_than(Size self, Size other) noexcept nogil

cdef Size adjust(Size self, int step, ResizeType resize_type) noexcept nogil

cdef Size sampled_resize_closest_to_area(Size self, int area, int step_size, ResizeType resize_type) noexcept nogil

cdef Size rotate_size(Size self, int degrees, RotateDirection direction) noexcept nogil
    
    