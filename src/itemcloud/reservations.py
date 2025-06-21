from typing import List
from itemcloud.size import (Size, ResizeType)
from itemcloud.box import (
    Box,
    Direction,
    from_native_box_array,
    RotateDirection
)
from itemcloud.native.reservations import (
    native_create_reservations,
    native_find_openings
)
from itemcloud.logger.base_logger import BaseLogger
from itemcloud.util.search import SearchProperties
from itemcloud.util.display_map import(
    create_display_buffer,
    create_display_map,
    DISPLAY_MAP_TYPE,
    add_margin_to_display_map,
    write_display_map,
    can_fit_on_target,
    from_displaymap_box
)
from itemcloud.util.time_measure import TimeMeasure
from itemcloud.containers.base.item import Item

class Reservation:
    def __init__(self, name: str, no: int, box: Box, item: Item):
        self.reservation_name = name
        self.reservation_no = no
        self.reservation_box = box
        self.reservation_party = item


class SampledUnreservedOpening(object):
    found: bool = False
    sampling_total: int = 0
    original_item: Item | None = None
    new_item: Item | None = None
    opening_box: Box | None = None
    actual_box: Box | None = None
    rotated_degrees: int | None = None
    measure: TimeMeasure = TimeMeasure()
    
    def log_sampling(self, logger: BaseLogger) -> None:
        if (1 == self.found or (0 == (self.sampling_total % 500))) and self.original_item is not None and self.new_item is not None:
            logger.debug(
                f"sample_to_find_unreserved_opening sampling[{self.sampling_total}]@({self.measure.latency_str()}) rotated({self.rotated_degrees}) {self.original_item.size_to_string()} -> {self.new_item.size_to_string()}\n"
            )

    def log_finding(self, logger: BaseLogger) -> None:
        if self.original_item is not None and self.new_item is not None:
            logger.debug(
                f"{'FOUND:' if 1 == self.found else 'NOT FOUND:'} sample_to_find_unreserved_opening sampling[{self.sampling_total}]@({self.measure.latency_str()}) rotated({self.rotated_degrees}) {self.original_item.size_to_string()} -> {self.new_item.size_to_string()}\n"
            )

# extrapolated from https://github.com/amueller/word_cloud/blob/main/wordcloud/wordcloud.py
class Reservations(object):
    def __init__(self,
                 logger: BaseLogger,
                 map_size: Size = Size(0,0),
                 total_threads: int = 1
        ):
        self.logger = logger
        self.num_threads = total_threads
        self._map_size = map_size
        self._map_box = Box(0, 0, self._map_size.width, self._map_size.height)
        self._buffer_length = self._map_size.area * 2 # x,y for eqch point in 2d area
        self._reservations: List[Reservation] = list()
# NOTE: ND Array shape is of form: (height, width) https://numpy.org/doc/2.2/reference/generated/numpy.ndarray.shape.html
#       PIL Image shape is of form (width, height) https://pillow.readthedocs.io/en/stable/reference/Image.html

        self._reservation_map = create_display_map(self._map_size)
        self._position_buffer = create_display_buffer(self._buffer_length)
        self._native_reservations = native_create_reservations(
            self.num_threads,
            self._map_size.to_native_size(),
            self._map_box.to_native(),
            self._buffer_length,
        )

    @property
    def reservation_map(self) -> DISPLAY_MAP_TYPE:
        return self._reservation_map
    
    @property
    def reservation_area(self) -> Box:
        return self._map_box

    def reserve_opening(self, name: str, reservation_no: int, opening: Box, party: Item, margin: int) -> bool:
    
        if not(self._map_box.contains(opening)):
            self.logger.error("BAD OPENING: reserve_opening reservation_map{0} cannot contain opening{1}".format(
                self._map_box.box_to_string(), opening.box_to_string()
            ))
            return False
        self.logger.debug("RESERVED: reserve_opening reservation({0}) opening{1}".format(reservation_no, opening.box_to_string()))
        write_display_map(add_margin_to_display_map(party.display_map, margin), self._reservation_map, opening, reservation_no)
        self._reservations.append(Reservation(name, reservation_no, opening, party))
        return True

    def sample_to_find_unreserved_opening(
        self,
        item: Item,
        min_party_size: Size,
        margin: int,
        resize_type: ResizeType,
        step_size: int,
        rotation_increment: int,
        search_properties: SearchProperties
    ) -> SampledUnreservedOpening:
        result: SampledUnreservedOpening = SampledUnreservedOpening()
        shrink_step_size: int = -step_size
        rotate: bool = False
        result.original_item = item
        result.new_item = item
        unrotated_item: Item = item
        result.measure.start()
        while True:
            result.sampling_total += 1
            party = add_margin_to_display_map(result.new_item.display_map, margin)
            openings = self._find_unreserved_openings(party)            
            result.found = 0 < len(openings)

            if result.found:
                result.opening_box = search_properties.search(openings)
                result.actual_box = result.opening_box.remove_margin(margin)
                result.measure.stop()
                result.log_finding(self.logger)
                return result

            result.log_sampling(self.logger)

            # Cycle: search -> shrink -> (search -> rotate)[until found or rotated 360] -> do cycle again with new shrink
            # until found or shrank so small its below min size -> not found
            if rotate and 0 < rotation_increment:
                # cycle part: (search -> rotate)[until found or rotated 360]
                result.rotated_degrees += rotation_increment
                result.new_item = result.new_item.rotate_item(rotation_increment, RotateDirection.CLOCKWISE)
                if 360 <= result.rotated_degrees + rotation_increment:
                    rotate = False
            else:
                # cycle part search -> shrink
                result.new_item = unrotated_item
                result.rotated_degrees = 0
                new_size = result.new_item.adjust(shrink_step_size, resize_type)
                result.new_item = result.new_item.resize_item(new_size)
                if result.new_item.is_less_than(min_party_size):
                    result.measure.stop()
                    result.log_finding(self.logger)
                    return result

                unrotated_item = result.new_item
                rotate = True

    def maximize_existing_reservation(self, reservation: Reservation, margin: int) -> Reservation:
        reservations_map = self._reservation_map
        reservations_box = from_displaymap_box(reservations_map.shape)
        expanded_item = reservation.reservation_party
        expanded_reservation = reservation.reservation_box.copy_box()
        expand_step_distance = 1
        deadends = set()
        deadends.add(Direction.NO_DIRECTION)
        # iteratively expand once in each direction until we cannot anymore
        while True:
            expansions = 0
            for direction in Direction:
                if direction in deadends:
                    continue
                expanded_item_map = add_margin_to_display_map(expanded_item.display_map, margin)
                sliding_reservation_box: Box = expanded_reservation.slide(expand_step_distance, direction)
                if not(reservations_box.contains(sliding_reservation_box)):
                    deadends.add(direction)
                    continue
                if not(can_fit_on_target(
                    expanded_item_map,
                    reservations_map,
                    sliding_reservation_box,
                    reservation.reservation_no
                )):
                    deadends.add(direction)
                    continue

                expanded_reservation = expanded_reservation.expand(expand_step_distance, direction)
                expanded_item = expanded_item.resize_item(expanded_reservation.remove_margin(margin).size)
                expansions += 1

            if 0 == expansions:
                break

        return Reservation(
            reservation.name,
            reservation.reservation_no,
            expanded_reservation,
            expanded_item
        )

    

    def _find_unreserved_openings(
            self,
            item: DISPLAY_MAP_TYPE
    ) -> List[Box]:
        return from_native_box_array(
            native_find_openings(
                self._native_reservations,
                self._position_buffer,
                self._reservation_map,
                item
            )
        )

    @staticmethod
    def create_reservations(reservation_map: DISPLAY_MAP_TYPE, logger: BaseLogger):
        result = Reservations(logger)
        result._map_size = Size(reservation_map.shape[1], reservation_map.shape[0])
        result._map_box = Box(0, 0, result._map_size.width, result._map_size.height)
        result._buffer_length = result._map_size.area
        result._reservation_map = reservation_map
        result._position_buffer = create_display_buffer(result._buffer_length)
        result._native_reservations = native_create_reservations(
            result.num_threads,
            result._map_size.to_native_size(),
            result._map_box.to_native(),
            result._buffer_length
        )
        return result
                
    @staticmethod
    def create_reservation_map(logger: BaseLogger, map_size: Size, reservations: list[Reservation], margin: int) -> DISPLAY_MAP_TYPE:
        reserver = Reservations(logger, map_size)
        for r in reservations:
            reserver.reserve_opening(r.reservation_name, r.reservation_no, r.reservation_box, r.reservation_party, margin)
        return reserver._reservation_map
