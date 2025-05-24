# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
cimport cython
from libc.limits cimport INT_MAX
from libc.math cimport round, pi, sin, cos, abs, sqrt
from libc.stdlib cimport rand, srand, RAND_MAX
from libc.time cimport time

srand(time(NULL))

cdef int randint(int lower, int upper) noexcept nogil:
    return (rand() % (upper - lower))

cdef double distance(int origin_x, int origin_y, int target_x, int target_y) noexcept nogil:
    cdef double x1 = origin_x
    cdef double y1 = origin_y
    cdef double x2 = target_x
    cdef double y2 = target_y
    return sqrt((x2 - x1)**2 + (y2 - y1)**2)

cdef RotationProperties create_rotation_properties(int degrees, RotateDirection direction) noexcept nogil:
    cdef RotationProperties result
    result.direction = direction
    result.degrees = degrees
    result.radians = degrees * (pi / 180)
    result.cosine = cos(result.radians)
    result.sine = sin(result.radians)

    return result

cdef int rotate_point_x(RotationProperties properties, int origin_x, int origin_y, int point_x, int point_y) noexcept nogil:
    if RotateDirection.CLOCKWISE == properties.direction:
        #    [ cos(degrees)   sin(degrees) ]
        return <int>round(origin_x + properties.cosine * (point_x - origin_x) + properties.sine * (point_y - origin_y))
    else:
        #    [ cos(degrees)  -sin(degrees) ]
        return <int>round(origin_x + properties.cosine * (point_x - origin_x) - properties.sine * (point_y - origin_y))

cdef int rotate_point_y(RotationProperties properties, int origin_x, int origin_y, int point_x, int point_y) noexcept nogil:
    if RotateDirection.CLOCKWISE == properties.direction:
        #    [ -sin(degrees)  cos(degrees) ]
        return <int>round(origin_y - properties.sine *(point_x - origin_x) + properties.cosine * (point_y - origin_y))
    else:
        #    [ sin(degrees)   cos(degrees) ]
        return <int>round(origin_y + properties.sine *(point_x - origin_x) + properties.cosine * (point_y - origin_y))






