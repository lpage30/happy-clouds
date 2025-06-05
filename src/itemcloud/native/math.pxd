# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False

cdef int randint(int lower, int upper) noexcept nogil

cdef inline int randindex(int array_length) noexcept nogil:
    return randint(0, array_length)

cdef double distance(int origin_x, int origin_y, int target_x, int target_y) noexcept nogil

cdef enum RotateDirection:
    COUNTERCLOCKWISE = -1
    CLOCKWISE = 1

ctypedef struct RotationProperties:
    RotateDirection direction
    int degrees
    double radians
    double cosine
    double sine


cdef RotationProperties create_rotation_properties(int degrees, RotateDirection direction) noexcept nogil

cdef int rotate_point_x(RotationProperties properties, int origin_x, int origin_y, int point_x, int point_y) noexcept nogil

cdef int rotate_point_y(RotationProperties properties, int origin_x, int origin_y, int point_x, int point_y) noexcept nogil

cdef int rounded_division(int numerator, int denominator) noexcept nogil

