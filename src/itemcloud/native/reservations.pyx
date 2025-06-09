# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# distutils: language = c++
# distutils: extra_compile_args = -std=c++11
cimport cython
from libcpp.atomic cimport atomic
from cython.parallel cimport parallel, prange
from libc.math cimport fmod
from libc.time cimport time
cdef extern from "stdio.h":
    int snprintf(char *str, unsigned int size, const char *format, ...) noexcept nogil
from itemcloud.native.display_map cimport (
    can_fit_on_target,
    display_map_box,
    display_map_size
)

cdef int _is_unreserved(
    Reservations self,
    DISPLAY_MAP_TYPE self_reservation_map,
    DISPLAY_MAP_TYPE party,
    Box test_area
) noexcept nogil:
    return can_fit_on_target(
        party,
        self_reservation_map,
        test_area,
        display_map_box(party)
    )

cdef Box[::1] find_openings(
    Reservations self, 
    DISPLAY_MAP_TYPE self_reservation_map,
    DISPLAY_MAP_TYPE party,    
) noexcept nogil:
    cdef atomic[int] pos_count
    cdef Size size = display_map_size(party)
    cdef Size sub_map_size = create_size(self.map_size.width - size.width, self.map_size.height - size.height)
    cdef int total_positions = size_area(sub_map_size)
    cdef int p
    cdef Box possible_opening
    cdef int row
    cdef int col
    cdef Box[::1] result
    pos_count.store(0)
    with nogil, parallel(num_threads=self.num_threads):
        for p in prange(total_positions):
            row = <int>(p / self.map_size.width)
            col = <int>(p - (row * self.map_size.width))
            possible_opening = create_box(col, row, col + size.width, row + size.height)
            if self.map_box.lower < possible_opening.lower:
                break
            if self.map_box.right < possible_opening.right:
                continue
            if 0 != _is_unreserved(
                self,
                self_reservation_map,
                party,
                possible_opening
            ):
                self_position_buffer[pos_count.fetch_add(1)] = p

    with gil:
        result = create_box_array(pos_count.load())
        for i in range(pos_count.load()):
            p = self_position_buffer[i]
            row = <int>(p / self.map_size.width)
            col = <int>(p - (row * self.map_size.width))
            result[i] = create_box(col, row, col + size.width, row + size.height)

    return result


#NOTE: PIL Image shape is of form (width, height) https://pillow.readthedocs.io/en/stable/reference/Image.html

# NOTE: ND Array shape is of form: (height, width) https://numpy.org/doc/2.2/reference/generated/numpy.ndarray.shape.html
# so for ND Array (memory view) we process rows (height or y axis) followed by columns (width or x axis)
# which is opposite of Image.
# memoryview[y,x] for ND Array and Image[x,y] <eye roll>
# a 'flattened out' memory view length is the area (height*width)
# 1 index value in that flattened out view addresses row = <int>(index_value/width), col = index_value - (width * row)

cdef Reservations create_reservations(
    int num_threads,
    Size map_size,
    Box map_box,
    int buffer_length,
) noexcept nogil:
    cdef Reservations self
    self.num_threads = num_threads
    self.map_size = map_size
    self.map_box = map_box
    self.buffer_length = buffer_length
    return self


def native_create_reservations(
    int num_threads,
    native_map_size,
    native_map_box,
    int buffer_length,
    DISPLAY_MAP_TYPE reservation_map,
    unsigned int[:] position_buffer
):
    cdef Reservations native_reservations = create_reservations(
        num_threads,
        native_map_size,
        native_map_box,
        buffer_length,
    )
    return native_reservations

def native_maximize_existing_reservation(
    native_reservations,
    DISPLAY_MAP_TYPE reservation_map,
    native_existing_reservation
): # return native_box
    return maximize_existing_reservation(native_reservations, reservation_map, native_existing_reservation)


def native_find_openings(
    Reservations self, 
    DISPLAY_MAP_TYPE self_reservation_map,
    DISPLAY_MAP_TYPE party
):
    return find_openings(
        self,
        self_reservation_map,
        party,
    )
