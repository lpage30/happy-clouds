# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
from itemcloud.native.size cimport Size, ResizeType
from itemcloud.native.box cimport Box
from itemcloud.native.box_search cimport BoxSearchProperties

ctypedef struct BoxReservations:
    int num_threads
    Size map_size
    Box map_box
    int buffer_length


cdef struct SampledUnreservedBoxOpening:
    int found
    int sampling_total
    Size new_size
    Box opening_box
    Box actual_box
    int rotated_degrees

cdef BoxReservations create_box_reservations(
    int num_threads,
    Size map_size,
    Box map_box,
    int buffer_length,
) noexcept nogil

cdef const char* reservations_to_string(
    BoxReservations self
) noexcept nogil

cdef int is_unreserved(
    BoxReservations self,
    unsigned int[:,:] self_reservation_map,
    Box party_sizes
) noexcept nogil

cdef SampledUnreservedBoxOpening sample_to_find_unreserved_opening(
    BoxReservations self,
    unsigned int[:,:] self_reservation_map,
    unsigned int[:] self_position_buffer,
    Size max_party_size,
    Size min_party_size,
    int margin,
    ResizeType resize_type,
    int step_size,
    int rotation_increment,
    BoxSearchProperties search_properties
)  noexcept nogil
