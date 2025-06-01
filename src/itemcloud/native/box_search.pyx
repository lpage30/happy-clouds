# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
cimport cython
from itemcloud.native.search_types cimport (
    RelativePosition,
    RelativeDistance,
    SearchPattern,
    randpos,
    randpattern
)
from itemcloud.native.math cimport randindex

cdef void set_search_positions(
    BoxSearchProperties* search,
    RelativePosition one=RelativePosition.NO_POSITION,
    RelativePosition two=RelativePosition.NO_POSITION,
    RelativePosition three=RelativePosition.NO_POSITION
) noexcept nogil:
    with gil:
        search[0].positions[0] = one
        search[0].positions[1] = two
        search[0].positions[2] = three

cdef int box_center_x(Box self) noexcept nogil:
    return self.left + <int>((self.right - self.left)/2)

cdef int box_center_y(Box self) noexcept nogil:
    return self.upper + <int>((self.lower - self.upper)/2)


cdef RelativePosition relative_position(int origin_x, int origin_y, int item_x, int item_y) noexcept nogil:
    if item_x < origin_x:
        if item_y < origin_y:
            return RelativePosition.TOP_LEFT_POSITION
        elif item_y > origin_y:
            return RelativePosition.BOTTOM_LEFT_POSITION
        return RelativePosition.LEFT_POSITION
    elif item_x > origin_x:
        if item_y < origin_y:
            return RelativePosition.TOP_RIGHT_POSITION
        elif item_y > origin_y:
            return RelativePosition.BOTTOM_RIGHT_POSITION
        return RelativePosition.RIGHT_POSITION
    if item_y < origin_y:
        return RelativePosition.TOP_POSITION
    elif item_y > origin_y:
        return RelativePosition.BOTTOM_POSITION
    return RelativePosition.RANDOM_POSITION

cdef BoxSearchProperties restart_search(BoxSearchProperties last_properties) noexcept nogil:
    cdef BoxSearchProperties result = start_search(last_properties.area, last_properties.pattern)
    result.loop = last_properties.loop
    return result

cdef BoxSearchProperties next_linear_search(Box last_found, BoxSearchProperties last_properties) noexcept nogil:
    # search patterns: https://i.ytimg.com/vi/8rXv-0gg-ZY/maxresdefault.jpg
    # pattern: bottom right -> top left by going up and down columns
    cdef RelativePosition position = box_relative_position(last_properties.origin_x, last_properties.origin_y, last_found)
    cdef RelativePosition where_are_we = box_relative_position_to_box(last_properties.area, last_found)
    cdef BoxSearchProperties result
    cdef int position_count = search_positions_len(&last_properties)
    
    result.pattern = last_properties.pattern
    result.area = last_properties.area
    result.loop = last_properties.loop + 1
    result.origin_x = box_center_x(last_found)
    result.origin_y = box_center_y(last_found)
    result.distance = RelativeDistance.CLOSEST_DISTANCE
    set_search_positions(&result)

    if RelativePosition.LEFT_POSITION == position: # top-left -> down(bottom), bottom-left -> up(top)
        if RelativePosition.TOP_POSITION == where_are_we or RelativePosition.TOP_LEFT_POSITION == where_are_we or RelativePosition.TOP_RIGHT_POSITION == where_are_we:
            result.positions[0] = RelativePosition.BOTTOM_POSITION
            if 1 < position_count:
                set_search_positions(&result, RelativePosition.BOTTOM_POSITION, RelativePosition.BOTTOM_LEFT_POSITION, RelativePosition.BOTTOM_RIGHT_POSITION)
        else:
            result.positions[0] = RelativePosition.TOP_POSITION
            if 1 < position_count:
                set_search_positions(&result, RelativePosition.TOP_POSITION, RelativePosition.TOP_LEFT_POSITION, RelativePosition.TOP_RIGHT_POSITION)

    if RelativePosition.TOP_POSITION == position: # up -> up(continue moving up), up -> left
        if last_properties.area.upper <= last_found.upper:
            result.positions[0] = RelativePosition.TOP_POSITION
            if 1 < position_count:
                set_search_positions(&result, RelativePosition.TOP_POSITION, RelativePosition.TOP_LEFT_POSITION, RelativePosition.TOP_RIGHT_POSITION)
        else:
            result.positions[0] = RelativePosition.LEFT_POSITION
            if 1 < position_count:
                set_search_positions(&result, RelativePosition.LEFT_POSITION, RelativePosition.TOP_LEFT_POSITION, RelativePosition.BOTTOM_LEFT_POSITION)
    
    if RelativePosition.BOTTOM_POSITION == position: # down -> down(continue moving down), down -> left
        if last_properties.area.lower >= last_found.lower:
            result.positions[0] = RelativePosition.BOTTOM_POSITION
            if 1 < position_count:
                set_search_positions(&result, RelativePosition.BOTTOM_POSITION, RelativePosition.BOTTOM_LEFT_POSITION, RelativePosition.BOTTOM_RIGHT_POSITION)
        else:
            result.positions[0] = RelativePosition.LEFT_POSITION
            if 1 < position_count:
                set_search_positions(&result, RelativePosition.LEFT_POSITION, RelativePosition.TOP_LEFT_POSITION, RelativePosition.BOTTOM_LEFT_POSITION)
    
    # we are moving left next, are we at the end of the search area ?
    # if end of search area then restart search again, and 'blur' the search area every other time we restart it
    if RelativePosition.LEFT_POSITION == result.positions[0] and last_properties.area.left >= last_found.left:
        # end of search pattern, restart search
        result = restart_search(result)

    return result

cdef BoxSearchProperties next_ray_search(Box last_found, BoxSearchProperties last_properties) noexcept nogil:
    # search patterns: https://i.ytimg.com/vi/8rXv-0gg-ZY/maxresdefault.jpg
    # pattern: center -> up, center -> down, center -> top-right, center -> bottom-left
    cdef RelativePosition position = box_relative_position(last_properties.origin_x, last_properties.origin_y, last_found)
    cdef RelativePosition where_are_we = box_relative_position_to_box(last_properties.area, last_found)
    cdef BoxSearchProperties result
    cdef int position_count = search_positions_len(&last_properties)
    
    result.pattern = last_properties.pattern
    result.area = last_properties.area
    result.loop = last_properties.loop + 1
    result.origin_x = box_center_x(last_found)
    result.origin_y = box_center_y(last_found)
    result.distance = RelativeDistance.CLOSEST_DISTANCE
    set_search_positions(&result)

    if RelativePosition.TOP_POSITION == position:
        # up -> (continue) up, up -> center -> top-right
        if last_properties.area.upper < last_found.upper:
            result.positions[0] = RelativePosition.TOP_POSITION
            if 1 < position_count:
                set_search_positions(&result, RelativePosition.TOP_LEFT_POSITION, RelativePosition.TOP_POSITION, RelativePosition.TOP_RIGHT_POSITION)
        else:
            result.origin_x = box_center_x(last_properties.area)
            result.origin_y = box_center_y(last_properties.area)
            result.positions[0] = RelativePosition.TOP_RIGHT_POSITION
            if 1 < position_count:
                set_search_positions(&result, RelativePosition.TOP_POSITION, RelativePosition.TOP_RIGHT_POSITION, RelativePosition.RIGHT_POSITION)

    if RelativePosition.TOP_RIGHT_POSITION == position:
        # top-right -> top-right (continue moving top-right), top-right -> center -> right
        if last_properties.area.upper < last_found.upper:
            result.positions[0] = RelativePosition.TOP_RIGHT_POSITION
            if 1 < position_count:
                set_search_positions(&result, RelativePosition.TOP_POSITION, RelativePosition.TOP_RIGHT_POSITION, RelativePosition.RIGHT_POSITION)
        else:
            result.origin_x = box_center_x(last_properties.area)
            result.origin_y = box_center_y(last_properties.area)
            result.positions[0] = RelativePosition.RIGHT_POSITION
            if 1 < position_count:
                set_search_positions(&result, RelativePosition.TOP_RIGHT_POSITION, RelativePosition.RIGHT_POSITION, RelativePosition.BOTTOM_RIGHT_POSITION)

    if RelativePosition.RIGHT_POSITION == position:
        # right -> right (continue moving right), right -> center -> bottom-right
        if last_properties.area.right < last_found.right:
            result.positions[0] = RelativePosition.RIGHT_POSITION
            if 1 < position_count:
                set_search_positions(&result, RelativePosition.TOP_RIGHT_POSITION, RelativePosition.RIGHT_POSITION, RelativePosition.BOTTOM_RIGHT_POSITION)
        else:
            result.origin_x = box_center_x(last_properties.area)
            result.origin_y = box_center_y(last_properties.area)
            result.positions[0] = RelativePosition.BOTTOM_RIGHT_POSITION
            if 1 < position_count:
                set_search_positions(&result, RelativePosition.RIGHT_POSITION, RelativePosition.BOTTOM_RIGHT_POSITION, RelativePosition.BOTTOM_POSITION)

    if RelativePosition.BOTTOM_RIGHT_POSITION == position:
        # bottom-right -> bottom-right (continue moving bottom right), bottom-right -> center -> Bottom
        if last_properties.area.lower > last_found.lower:
            result.positions[0] = RelativePosition.BOTTOM_RIGHT_POSITION
            if 1 < position_count:
                set_search_positions(&result, RelativePosition.RIGHT_POSITION, RelativePosition.BOTTOM_RIGHT_POSITION, RelativePosition.BOTTOM_POSITION)

        else:
            result.origin_x = box_center_x(last_properties.area)
            result.origin_y = box_center_y(last_properties.area)
            result.positions[0] = RelativePosition.BOTTOM_POSITION
            if 1 == position_count:
                set_search_positions(&result, RelativePosition.BOTTOM_RIGHT_POSITION, RelativePosition.BOTTOM_POSITION, RelativePosition.BOTTOM_LEFT_POSITION)

    if RelativePosition.BOTTOM_POSITION == position:
        # bottom -> bottom (continue moving bottom), bottom -> center -> bottom-left
        if last_properties.area.lower > last_found.lower:
            result.positions[0] = RelativePosition.BOTTOM_POSITION
            if 1 < position_count:
                set_search_positions(&result, RelativePosition.BOTTOM_RIGHT_POSITION, RelativePosition.BOTTOM_POSITION, RelativePosition.BOTTOM_LEFT_POSITION)
        else:
            result.origin_x = box_center_x(last_properties.area)
            result.origin_y = box_center_y(last_properties.area)
            result.positions[0] = RelativePosition.BOTTOM_LEFT_POSITION
            if 1 < position_count:
                set_search_positions(&result, RelativePosition.BOTTOM_POSITION, RelativePosition.BOTTOM_LEFT_POSITION, RelativePosition.LEFT_POSITION)

    if RelativePosition.BOTTOM_LEFT_POSITION == position:
        # bottom-left -> bottom-left (continue moving bottom-left), bottom-left -> center -> left
        if last_properties.area.lower > last_found.lower:
            result.positions[0] = RelativePosition.BOTTOM_LEFT_POSITION
            if 1 < position_count:
                set_search_positions(&result, RelativePosition.BOTTOM_POSITION, RelativePosition.BOTTOM_LEFT_POSITION, RelativePosition.LEFT_POSITION)
        else:
            result.origin_x = box_center_x(last_properties.area)
            result.origin_y = box_center_y(last_properties.area)
            result.positions[0] = RelativePosition.LEFT_POSITION
            if 1 < position_count:
                set_search_positions(&result, RelativePosition.BOTTOM_LEFT_POSITION, RelativePosition.LEFT_POSITION, RelativePosition.TOP_LEFT_POSITION)

    if RelativePosition.LEFT_POSITION == position:
        # left -> left (continue moving left), left -> center -> top-left
        if last_properties.area.left < last_found.left:
            result.positions[0] = RelativePosition.LEFT_POSITION
            if 1 < position_count:
                set_search_positions(&result, RelativePosition.BOTTOM_LEFT_POSITION, RelativePosition.LEFT_POSITION, RelativePosition.TOP_LEFT_POSITION)
        else:
            result.origin_x = box_center_x(last_properties.area)
            result.origin_y = box_center_y(last_properties.area)
            result.positions[0] = RelativePosition.TOP_LEFT_POSITION
            if 1 < position_count:
                set_search_positions(&result, RelativePosition.LEFT_POSITION, RelativePosition.TOP_LEFT_POSITION, RelativePosition.TOP_POSITION)


    if RelativePosition.TOP_LEFT_POSITION == position:
        # top-left -> top-left (continue moving top-left), top-left -> center -> top
        if last_properties.area.upper < last_found.upper:
            result.positions[0] = RelativePosition.TOP_LEFT_POSITION
            if 1 < position_count:
                set_search_positions(&result, RelativePosition.TOP_LEFT_POSITION, RelativePosition.LEFT_POSITION, RelativePosition.TOP_POSITION)
        else:
            result.origin_x = box_center_x(last_properties.area)
            result.origin_y = box_center_y(last_properties.area)
            result.positions[0] = RelativePosition.TOP_POSITION
            if 1 < position_count:
                set_search_positions(&result, RelativePosition.TOP_LEFT_POSITION, RelativePosition.TOP_POSITION, RelativePosition.TOP_RIGHT_POSITION)

    # we are moving top next, are we at the end of the search area ?
    # if end of search area then restart search again, and 'blur' the search area every other time we restart it
    if RelativePosition.TOP_POSITION == result.positions[0] and last_properties.area.upper >= last_found.upper:
        # end of search pattern, restart search
        result = restart_search(result)

    return result

cdef BoxSearchProperties next_spiral_search(Box last_found, BoxSearchProperties last_properties) noexcept nogil:
    # search patterns: https://i.ytimg.com/vi/8rXv-0gg-ZY/maxresdefault.jpg
    # pattern: center -> left, left -> up, up -> right, right -> down
    cdef RelativePosition position = box_relative_position(last_properties.origin_x, last_properties.origin_y, last_found)
    cdef RelativePosition where_are_we = box_relative_position_to_box(last_properties.area, last_found)
    cdef BoxSearchProperties result
    cdef int i = 0
    cdef int position_count = search_positions_len(&last_properties)
    
    result.pattern = last_properties.pattern
    result.area = last_properties.area
    result.loop = last_properties.loop + 1
    result.origin_x = box_center_x(last_found)
    result.origin_y = box_center_y(last_found)
    result.distance = RelativeDistance.CLOSEST_DISTANCE
    set_search_positions(&result)
    if RelativePosition.LEFT_POSITION == position:
        if last_properties.area.upper >= last_found.upper:
            return restart_search(result)
        set_search_positions(&result, RelativePosition.TOP_LEFT_POSITION, RelativePosition.TOP_POSITION, RelativePosition.TOP_RIGHT_POSITION)
    if RelativePosition.TOP_POSITION == position:
        if last_properties.area.right <= last_found.right:
            return restart_search(result)
        set_search_positions(&result, RelativePosition.TOP_RIGHT_POSITION, RelativePosition.RIGHT_POSITION, RelativePosition.BOTTOM_RIGHT_POSITION)
    if RelativePosition.RIGHT_POSITION == position:
        if last_properties.area.lower <= last_found.lower:
            return restart_search(result)
        set_search_positions(&result, RelativePosition.BOTTOM_RIGHT_POSITION, RelativePosition.BOTTOM_POSITION, RelativePosition.BOTTOM_LEFT_POSITION)
    if RelativePosition.BOTTOM_POSITION == position:
        if last_properties.area.left >= last_found.left:
            return restart_search(result)
        set_search_positions(&result, RelativePosition.BOTTOM_LEFT_POSITION, RelativePosition.LEFT_POSITION, RelativePosition.TOP_LEFT_POSITION)
    
    return result



cdef BoxSearchProperties start_search(Box area, SearchPattern pattern) noexcept nogil:
    cdef BoxSearchProperties result

    result.pattern = pattern if pattern != SearchPattern.RANDOM_PATTERN else randpattern()
    result.area = area
    result.loop = -1
    set_search_positions(&result)
    result.distance = RelativeDistance.CLOSEST_DISTANCE
    
    if SearchPattern.LINEAR_PATTERN == result.pattern:
        result.origin_x = result.area.right
        result.origin_y = result.area.lower
        result.positions[0] = RelativePosition.TOP_POSITION
        result.distance = RelativeDistance.CLOSEST_DISTANCE
    if SearchPattern.RAY_PATTERN == result.pattern:
        result.origin_x = box_center_x(result.area)
        result.origin_y = box_center_y(result.area)
        result.positions[0] = RelativePosition.TOP_POSITION
        result.distance = RelativeDistance.CLOSEST_DISTANCE
    if SearchPattern.SPIRAL_PATTERN == result.pattern:
        result.origin_x = box_center_x(result.area)
        result.origin_y = box_center_y(result.area)
        set_search_positions(&result, RelativePosition.BOTTOM_LEFT_POSITION, RelativePosition.LEFT_POSITION, RelativePosition.TOP_LEFT_POSITION)
        result.distance = RelativeDistance.CLOSEST_DISTANCE
    return result


cdef Box search(Box[::1] boxes, BoxSearchProperties properties) noexcept nogil:
    cdef int index = -1
    cdef int total_at_position = 0
    cdef int randomly_selected_position = 0
    cdef int i
    if SearchPattern.NO_PATTERN == properties.pattern:
        return boxes[randindex(boxes.shape[0])]

    if RelativeDistance.RANDOM_DISTANCE == properties.distance:
        for i in range(boxes.shape[0]):
            if 0 < contains_search_position(&properties, box_relative_position(properties.origin_x, properties.origin_y, boxes[i])):
                total_at_position = total_at_position + 1
        if 0 < total_at_position:
            randomly_selected_position = randindex(total_at_position)
            total_at_position = 0
            for i in range(boxes.shape[0]):
                if 0 < contains_search_position(&properties, box_relative_position(properties.origin_x, properties.origin_y, boxes[i])):
                    if randomly_selected_position == total_at_position:
                        index = i
                        break
                    total_at_position = total_at_position + 1

    if RelativeDistance.CLOSEST_DISTANCE == properties.distance:
        for i in range(boxes.shape[0]):
            if 0 < contains_search_position(&properties, box_relative_position(properties.origin_x, properties.origin_y, boxes[i])):
                if 0 == total_at_position or origin_distance(properties.origin_x, properties.origin_y, boxes[i]) < origin_distance(properties.origin_x, properties.origin_y, boxes[index]):
                    index = i
                total_at_position = total_at_position + 1

    if RelativeDistance.FARTHEST_DISTANCE == properties.distance:
        for i in range(boxes.shape[0]):
            if 0 < contains_search_position(&properties, box_relative_position(properties.origin_x, properties.origin_y, boxes[i])):
                if 0 == total_at_position or origin_distance(properties.origin_x, properties.origin_y, boxes[i]) > origin_distance(properties.origin_x, properties.origin_y, boxes[index]):
                    index = i
                total_at_position = total_at_position + 1

    if -1 == index:
        index = randindex(boxes.shape[0])
    return boxes[index]

cdef BoxSearchProperties next_search(Box last_found, BoxSearchProperties last_properties) noexcept nogil:
    if SearchPattern.LINEAR_PATTERN == last_properties.pattern:
        return next_linear_search(last_found, last_properties)
    if SearchPattern.RAY_PATTERN == last_properties.pattern:
        return next_ray_search(last_found, last_properties)
    if SearchPattern.SPIRAL_PATTERN == last_properties.pattern:
        return next_spiral_search(last_found, last_properties)
    return start_search(last_properties.area, last_properties.pattern)

cdef SearchPattern str_to_pattern(str pattern):
    if pattern == 'RANDOM_PATTERN':
        return SearchPattern.RANDOM_PATTERN
    if pattern == 'LINEAR_PATTERN':
        return SearchPattern.LINEAR_PATTERN
    if pattern == 'RAY_PATTERN':
        return SearchPattern.RAY_PATTERN
    if pattern == 'SPIRAL_PATTERN':
        return SearchPattern.SPIRAL_PATTERN
    return SearchPattern.NO_PATTERN

def native_start_search(
    area: Box,
    pattern: str_to_pattern
): # return native_search_properties
    return start_search(
        area,
        str_to_pattern(pattern)
    )

def native_search(boxes: Box[::1], properties: BoxSearchProperties): # return native_box
    return search(boxes, properties)

def native_next_search(
    last_found: Box,
    last_properties: BoxSearchProperties
): # return native_search_properties
    return next_search(last_found, last_properties)
