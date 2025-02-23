# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
from libc.math cimport round, abs, fmod, fmin, fmax
cimport cython
cdef extern from "stdio.h":
    int snprintf(char *str, size_t size, const char *format, ...) noexcept nogil
from itemcloud.native.box cimport Box, RotateDirection, create_box, size, rotate
from itemcloud.native.base_logger cimport (  
    log_debug,
    log_error,
)
cdef struct SizeDistance:
    Size size
    int distance

cdef SizeDistance resize_closest_to_area(Size self, int area, int step_size, ResizeType resize_type) noexcept nogil:
    cdef Size grow_size = adjust(self, step_size, resize_type)
    cdef Size shrink_size = adjust(self, -1 * step_size, resize_type)
    cdef int grow_distance = abs(area - (grow_size.width * grow_size.height))
    cdef int shrink_distance = abs(area - (shrink_size.width * shrink_size.height))

    cdef SizeDistance result
    if grow_distance <= shrink_distance:
        result.size = grow_size
        result.distance = grow_distance
    else:
        result.size = shrink_size
        result.distance = shrink_distance
    return result

cdef ResizeType to_resize_type(int t) noexcept nogil:
    if 1 == t:
        return ResizeType.MAINTAIN_ASPECT_RATIO
    if 2 == t:
        return ResizeType.MAINTAIN_PERCENTAGE_CHANGE
    return ResizeType.NO_RESIZE_TYPE



cdef Size create_size(int width, int height) noexcept nogil:
    cdef Size self
    self.width = width
    self.height = height
    return self

cdef const char* size_to_string(Size self) noexcept nogil:
    cdef char sbuf[32]
    snprintf(sbuf, 32, "Size(%d,%d)", self.width, self.height)
    return sbuf

cdef int size_area(Size self) noexcept nogil:
    return self.width * self.height

cdef int size_less_than(Size self, Size other) noexcept nogil:
    if self.width < other.width or self.height < other.height:
        return 1
    return 0

cdef Size adjust(Size self, int step, ResizeType resize_type) noexcept nogil:
    cdef float pct_change 
    cdef float aspect_ratio
    if 0 == self.width:
        log_error("DIVIDE BY ZERO - Width(%d): adjust Size(%d,%d) step(%d) resize_type(%d)", 
            self.width, self.width, self.height, step, resize_type
        )
        return self
    if 0 == self.height:
        log_error("DIVIDE BY ZERO - Height(%d): adjust Size(%d,%d) step(%d) resize_type(%d)", 
            self.height, self.width, self.height, step, resize_type
        )
        return self
    pct_change = abs(step) / self.width
    aspect_ratio = self.width / self.height
    if ResizeType.MAINTAIN_ASPECT_RATIO == resize_type:
        if 0.0 == aspect_ratio:
            log_error("DIVIDE BY ZERO - aspect_ratio(%f): adjust Size(%d,%d) step(%d) resize_type(%d)", 
                aspect_ratio, self.width, self.height, step, resize_type
            )
            return self
        return Size(
            self.width + step,
            <int>round((self.width + step) / aspect_ratio)
        )
    elif ResizeType.MAINTAIN_PERCENTAGE_CHANGE == resize_type:
        if 0 <= step:
            return Size(
                self.width + <int>round(pct_change * self.width),
                self.height + <int>round(pct_change * self.height)
            )
        else:
            return Size(
                self.width - <int>round(pct_change * self.width),
                self.height - <int>round(pct_change * self.height)
            )
    return Size(
        self.width + step,
        self.height + step
    )

cdef Size sampled_resize_closest_to_area(Size self, int area, int step_size, ResizeType resize_type) noexcept nogil:
    cdef int sampling_count = 0
    cdef Size last_size = self
    cdef SizeDistance best_size_distance
    cdef SizeDistance last_size_distance
    cdef int last_distances_len = 6
    cdef int last_distances[6]
    cdef int found_best = 0

    while found_best == 0:
        sampling_count += 1
        best_size_distance = resize_closest_to_area(last_size, area, step_size, resize_type)
        
        if sampling_count == 1:
            last_size_distance = best_size_distance
            last_distances[<int>fmod((sampling_count - 1), last_distances_len)] = last_size_distance.distance
            continue
        
        if last_size_distance.distance < best_size_distance.distance:
            found_best = 1
            continue
        else:
            found_best = 1
            for i in range(sampling_count-1, <int>fmax(0, sampling_count - last_distances_len),-1):
                if last_distances[<int>fmod(i, last_distances_len)] != best_size_distance.distance:
                    found_best = 0
                    break
            if found_best != 1:
                last_distances[<int>fmod((sampling_count - 1), last_distances_len)] = best_size_distance.distance
                last_size_distance = best_size_distance

    return last_size_distance.size

def native_create_size(
    width: int, 
    height: int
): # return native_size
    return create_size(width, height)

def native_adjust(
    native_size,
    step: int,
    resize_type: int
): # return native_size
    return adjust(native_size, step, to_resize_type(resize_type))

cdef Size rotate_size(Size self, int degrees, RotateDirection direction) noexcept nogil:
    cdef Box result_box = rotate(create_box(0,0, self.width, self.height), degrees, direction)
    cdef Size result = size(result_box)
    if result.width <= 0 or result.height <= 0:
        log_error("BAD DIMENSIONS: rotate_size(Size(%d,%d),degrees(%d),direction(%d)) -> Size(%d,%d) (Box(%d,%d,%d,%d))",
            self.width, self.height, degrees, direction,
            result.width, result.height,
            result_box.left, result_box.upper, result_box.right, result_box.lower

        )
    return result
