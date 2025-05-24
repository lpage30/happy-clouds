# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
cimport cython
cdef extern from "stdio.h":
    int snprintf(char *str, size_t size, const char *format, ...) noexcept nogil
from itemcloud.native.size cimport (
    Size,
    ResizeType,
    to_resize_type,
    size_area,
    adjust,
    sampled_resize_closest_to_area
)

ctypedef struct WeightedSize:
    float weight
    Size size

cdef WeightedSize create_weighted_size(float weight, Size size) noexcept nogil:
    cdef WeightedSize self
    self.weight = weight
    self.size = size
    return self

cdef const char* weighted_size_to_string(WeightedSize self) noexcept nogil:
    cdef char wbuf[64]
    snprintf(wbuf, 64, "WeightedSize(%.2f, Size(%d,%d))", self.weight, self.size.width, self.size.height)
    return wbuf

def native_create_weighted_size(
    weight: float,
    native_size
): # return native_weightedsize
    return create_weighted_size(weight, native_size)

def native_create_weighted_size_array(
    size: int
): # native_weighted_sizes
    cdef WeightedSize[::1] result = cython.view.array(shape=(size,), itemsize=sizeof(WeightedSize), format="f i i")
    return result

def native_resize_to_proportionally_fit(
    native_weighted_sizes,
    native_fit_size,
    resize_type: int,
    step_size: int,
    margin: int
): # return native_weighted_sizes
    """
    use weights to determine proportion of fit_size for each image
    fit each image to their proportion by iteratively changing the size until the closest fit is made
    return fitted images with their proportions
    """

    cdef ResizeType eresize_type = to_resize_type(resize_type)
    cdef WeightedSize[:] result = native_create_weighted_size_array(native_weighted_sizes.shape[0])

    cdef float total_weight = 0.0
    cdef float proportion_weight = 0.0
    cdef int fit_area = size_area(native_fit_size)
    cdef int fitted_images = 0
    cdef Size new_size
    cdef int resize_area = 0
    cdef Size sampled_resize
    cdef int index = 0
    cdef WeightedSize weighted_size

    for index in range(native_weighted_sizes.shape[0]):
        weighted_size = native_weighted_sizes[index]
        total_weight = total_weight + weighted_size.weight
    
    for index in range(native_weighted_sizes.shape[0]):
        weighted_size = native_weighted_sizes[index]
        proportion_weight = weighted_size.weight / total_weight
        resize_area = <int>round(proportion_weight * fit_area)
        new_size = adjust(weighted_size.size, margin, ResizeType.NO_RESIZE_TYPE)
        sampled_resize = sampled_resize_closest_to_area(new_size, resize_area, step_size, eresize_type)
        new_size = adjust(sampled_resize, -1 * margin, ResizeType.NO_RESIZE_TYPE)
        result[index] = create_weighted_size(weighted_size.weight, new_size)
    
    return result
