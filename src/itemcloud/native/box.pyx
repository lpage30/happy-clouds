# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
cimport cython
from libc.limits cimport INT_MAX
from libc.math cimport round, pi, sin, cos, abs
from cython.parallel cimport parallel, prange
cdef extern from "stdio.h":
    int snprintf(char *str, size_t size, const char *format, ...) noexcept nogil
from itemcloud.native.size cimport create_size
from itemcloud.native.base_logger cimport  (
    log_error,
    log_debug
)

cdef Box create_box(int left, int upper, int right, int lower) noexcept nogil:
    cdef Box self
    self.left = left
    self.upper = upper
    self.right = right
    self.lower = lower
    return self

cdef const char* box_to_string(Box self) noexcept nogil:
    cdef char bbuf[64]
    snprintf(bbuf, 64, "Box(%d,%d,%d,%d)", self.left, self.upper, self.right, self.lower)
    return bbuf

cdef int box_width(Box self) noexcept nogil:
    return self.right - self.left

cdef int box_height(Box self) noexcept nogil:
    return self.lower - self.upper

cdef int box_area(Box self) noexcept nogil:
    return box_width(self) * box_height(self)

cdef Size size(Box self) noexcept nogil:
    return create_size(
        box_width(self),
        box_height(self)
    )
cdef int box_equals(Box self, Box other) noexcept nogil:
    if other.left == self.left and other.upper == self.upper and other.right == self.right and other.lower == self.lower:
        return 1
    return 0

cdef Box g_empty_box = create_box(
    -1,
    -1,
    -1,
    -1
)
cdef Box empty_box() noexcept nogil:
    global g_empty_box
    return g_empty_box

cdef int is_empty(Box self) noexcept nogil:
    global g_empty_box
    return box_equals(self, g_empty_box)

cdef int contains(Box self, Box other) noexcept nogil:
    if (self.left <= other.left and self.upper <= other.upper and 
        self.right >= other.right and self.lower >= other.lower):
        return 1
    return 0

cdef Box add_margin(Box self, int margin) noexcept nogil:
    cdef int padding = <int>round(margin / 2)
    return create_box(
        self.left - padding,
        self.upper - padding,
        self.right + padding,
        self.lower + padding
    )

cdef Box remove_margin(Box self, int margin) noexcept nogil:
    cdef int padding = <int>round(margin / 2)
    return create_box(
        self.left + padding,
        self.upper + padding,
        self.right - padding,
        self.lower - padding
    )

cdef struct Point:
    int x
    int y
cdef Point create_point(int x, int y) noexcept nogil:
    cdef Point r
    r.x = x
    r.y = y
    return r

cdef Box rotate(Box self, int degrees, RotateDirection direction) noexcept nogil:
    cdef double radians
    cdef double cosine
    cdef double sine
    cdef int i
    cdef Point pts[4]
    cdef Point rotated_pts[4]
    cdef Point origin
    cdef Point adjust_to_positive = create_point(0,0)
    cdef Box rotated_box
    cdef int needs_adjustment_to_positive = 0

    if degrees <= 0:
        return self

    radians = degrees * (pi / 180) 
    cosine = cos(radians)
    sine = sin(radians)
    origin = create_point(<int>round((self.right - self.left) / 2), <int>round((self.lower - self.upper) / 2))
    pts[0] = create_point(self.left, self.upper)
    pts[1] = create_point(self.right, self.upper)
    pts[2] = create_point(self.right, self.lower)
    pts[3] = create_point(self.left, self.lower)

    rotated_box = create_box(INT_MAX,INT_MAX,0,0)
    if RotateDirection.CLOCKWISE == direction:
        for i in range(4):
            #    [ cos(degrees)   sin(degrees) ]
            #    [ -sin(degrees)  cos(degrees) ]
            rotated_pts[i].x = <int>round(origin.x + cosine * (pts[i].x - origin.x) + sine * (pts[i].y - origin.y))
            rotated_pts[i].y = <int>round(origin.y - sine *(pts[i].x - origin.x) + cosine * (pts[i].y - origin.y))
            if rotated_pts[i].x < 0:
                needs_adjustment_to_positive = 1
                if rotated_pts[i].x < adjust_to_positive.x:
                    adjust_to_positive.x = rotated_pts[i].x
            if rotated_pts[i].y < 0:
                needs_adjustment_to_positive = 1
                if rotated_pts[i].y < adjust_to_positive.y:
                    adjust_to_positive.y = rotated_pts[i].y
    else:
        for i in range(4):
            #    [ cos(degrees)  -sin(degrees) ]
            #    [ sin(degrees)   cos(degrees) ]
            rotated_pts[i].x = <int>round(origin.x + cosine * (pts[i].x - origin.x) - sine * (pts[i].y - origin.y))
            rotated_pts[i].y = <int>round(origin.y + sine *(pts[i].x - origin.x) + cosine * (pts[i].y - origin.y))
            if rotated_pts[i].x < 0:
                needs_adjustment_to_positive = 1
                if rotated_pts[i].x < adjust_to_positive.x:
                    adjust_to_positive.x = rotated_pts[i].x
            if rotated_pts[i].y < 0:
                needs_adjustment_to_positive = 1
                if rotated_pts[i].y < adjust_to_positive.y:
                    adjust_to_positive.y = rotated_pts[i].y
                
    
    if 1 == needs_adjustment_to_positive:
        # adjust points so they are in positive territory
        # basically we are sliding the box  into positive area after having rotated it
        adjust_to_positive.x = abs(adjust_to_positive.x)
        adjust_to_positive.y = abs(adjust_to_positive.y)
    for i in range(4):
        rotated_pts[i].x = rotated_pts[i].x + adjust_to_positive.x
        rotated_pts[i].y = rotated_pts[i].y + adjust_to_positive.y
        if rotated_pts[i].x < rotated_box.left:
            rotated_box.left = rotated_pts[i].x
        if rotated_pts[i].y < rotated_box.upper:
            rotated_box.upper = rotated_pts[i].y
        if rotated_box.right < rotated_pts[i].x:
            rotated_box.right = rotated_pts[i].x
        if rotated_box.lower < rotated_pts[i].y:
            rotated_box.lower = rotated_pts[i].y

    if rotated_box.left < 0 or rotated_box.upper < 0 or rotated_box.right < 0 or rotated_box.lower < 0 or rotated_box.left == rotated_box.right or rotated_box.upper == rotated_box.lower:
        log_error("BAD DIMENSIONS: rotate(Box(%d,%d,%d,%d),degrees(%d),direction(%d)) -> Box(%d,%d,%d,%d)\nrotated points: [(%d,%d), (%d,%d), (%d, %d), (%d, %d)]",
            self.left, self.upper, self.right, self.lower, degrees, direction,
            rotated_box.left, rotated_box.upper, rotated_box.right, rotated_box.lower,
            rotated_pts[0].x, rotated_pts[0].y,
            rotated_pts[1].x, rotated_pts[1].y,
            rotated_pts[2].x, rotated_pts[2].y,
            rotated_pts[3].x, rotated_pts[3].y
        )


    return rotated_box

def native_create_box(
    left: int,
    upper: int,
    right: int,
    lower: int
): # return native_box
    return create_box(left, upper, right, lower)