# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
cimport cython
from itemcloud.native.math cimport randindex

cdef RelativePosition randpos() noexcept nogil:
    cdef int pos = randindex(8) + 1
    if 1 == pos:
        return RelativePosition.LEFT_POSITION
    if 2 == pos:
        return RelativePosition.RIGHT_POSITION
    if 3 == pos:
        return RelativePosition.TOP_POSITION
    if 4 == pos:
        return RelativePosition.BOTTOM_POSITION
    if 5 == pos:
        return RelativePosition.TOP_LEFT_POSITION
    if 6 == pos:
        return RelativePosition.TOP_RIGHT_POSITION
    if 7 == pos:
        return RelativePosition.BOTTOM_LEFT_POSITION
    return RelativePosition.BOTTOM_RIGHT_POSITION

cdef SearchPattern randpattern() noexcept nogil:
    cdef int pat = 2 + randindex(3)
    if 2 == pat:
        return SearchPattern.LINEAR_PATTERN
    if 3 == pat:
        return SearchPattern.RAY_PATTERN
    if 4 == pat:
        return SearchPattern.SPIRAL_PATTERN
    return SearchPattern.NO_PATTERN
