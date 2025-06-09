# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
from itemcloud.native.display_map cimport DISPLAY_MAP_TYPE
from itemcloud.native.size cimport Size, ResizeType
from itemcloud.native.box cimport Box

ctypedef struct Reservations:
    int num_threads
    Size map_size
    Box map_box
    int buffer_length

cdef Reservations create_reservations(
    int num_threads,
    Size map_size,
    Box map_box,
    int buffer_length,
) noexcept nogil


cdef Box[::1] find_openings(
    Reservations self, 
    DISPLAY_MAP_TYPE self_reservation_map,
    DISPLAY_MAP_TYPE party
) noexcept nogil