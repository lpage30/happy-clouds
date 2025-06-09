from typing import List
from itemcloud.box import (
    Box,
    to_native_box_array
)
from itemcloud.util.search_types import (
    RelativeDistance,
    RelativePosition,
    SearchPattern
)
from itemcloud.native.search import (
    native_start_search,
    native_search,
    native_next_search
)

class SearchProperties:
    def __init__(
        self,
        area: Box,
        origin_x: int,
        origin_y: int,
        pattern: SearchPattern,
        loop: int,
        positions: List[RelativePosition],
        distance: RelativeDistance,
        native
    ) -> None:
        self.area = area
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.pattern = pattern
        self.loop = loop
        self.positions = positions
        self.distance = distance
        self.native = native

    def to_native(self):
        return self.native
    
    def search(self, boxes: List[Box]) -> Box:
        return Box.from_native(native_search(
            to_native_box_array(boxes),
            self.to_native()
        ))

    def next(self, last_found: Box) -> 'SearchProperties':
        return SearchProperties.from_native(native_next_search(
            last_found.to_native(),
            self.to_native()
        ))

    @staticmethod
    def start(area: Box, pattern: SearchPattern) -> 'SearchProperties':
        return SearchProperties.from_native(native_start_search(
            area.to_native(),
            pattern.name
        ))

    @staticmethod
    def from_native(native_box_search_properties) -> 'SearchProperties':
        pattern: SearchPattern
        positions: List[RelativePosition] = list()
        distance: RelativeDistance
        for pat in SearchPattern:
            if pat.value == int(native_box_search_properties['pattern']):
                pattern = pat
                break
        for dist in RelativeDistance:
            if dist.value == int(native_box_search_properties['distance']):
                distance = dist
                break
        for native_pos in native_box_search_properties['positions']:
            for pos in RelativePosition:
                if pos.value == native_pos:
                    positions.append(pos)
        
        return SearchProperties(
            Box.from_native(native_box_search_properties['area']),
            int(native_box_search_properties['origin_x']),
            int(native_box_search_properties['origin_y']),
            pattern,
            int(native_box_search_properties['loop']),
            positions,
            distance,
            native_box_search_properties
        )
