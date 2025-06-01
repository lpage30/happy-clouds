import numpy as np
from typing import List
from itemcloud.size import (Size, ResizeType)
from itemcloud.box import Box
from itemcloud.native.box_reservations import (
    native_create_box_reservations,
    native_sample_to_find_unreserved_opening,
    native_maximize_existing_reservation
)
from itemcloud.logger.base_logger import BaseLogger
from itemcloud.util.box_search import BoxSearchProperties
ReservationMapDataType = np.uint32
ReservationMapType = np.ndarray[ReservationMapDataType, ReservationMapDataType]
PositionBufferType = np.ndarray[ReservationMapDataType]


class BoxReservation:
    def __init__(self, name: str, no: int, box: Box):
        self.name = name
        self.no = no
        self.box = box


class SampledUnreservedBoxOpening(object):
    
    def __init__(
        self, 
        found: bool,
        sampling_total: int,
        new_size: Size,
        opening_box: Box | None = None,
        actual_box: Box | None = None,
        rotated_degrees: int | None = None
    ):
        self.found = found
        self.sampling_total = sampling_total
        self.new_size = new_size
        self.opening_box = opening_box
        self.actual_box = actual_box
        self.rotated_degrees = rotated_degrees
    
    @staticmethod
    def from_native(native_sampledunreservedboxopening):
        if 0 != native_sampledunreservedboxopening['found']:
            return SampledUnreservedBoxOpening(
                True,
                native_sampledunreservedboxopening['sampling_total'],
                Size.from_native(native_sampledunreservedboxopening['new_size']),
                Box.from_native(native_sampledunreservedboxopening['opening_box']),
                Box.from_native(native_sampledunreservedboxopening['actual_box']),
                native_sampledunreservedboxopening['rotated_degrees']
            )
        else:
            return  SampledUnreservedBoxOpening(
                False,
                native_sampledunreservedboxopening['sampling_total'],
                Size.from_native(native_sampledunreservedboxopening['new_size']),
            )


# extrapolated from https://github.com/amueller/word_cloud/blob/main/wordcloud/wordcloud.py
class BoxReservations(object):
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
        self._reservations: List[BoxReservation] = list()
# NOTE: ND Array shape is of form: (height, width) https://numpy.org/doc/2.2/reference/generated/numpy.ndarray.shape.html
#       PIL Image shape is of form (width, height) https://pillow.readthedocs.io/en/stable/reference/Image.html

        self._reservation_map: ReservationMapType = np.zeros(self._map_size.nd_shape, dtype=ReservationMapDataType)
        self._position_buffer: PositionBufferType = np.zeros((self._buffer_length), dtype=ReservationMapDataType)
        self._native_reservations = native_create_box_reservations(
            self.num_threads,
            self._map_size.to_native_size(),
            self._map_box.to_native(),
            self._buffer_length,
            self._reservation_map,
            self._position_buffer
        )

    @property
    def reservation_map(self) -> ReservationMapType:
        return self._reservation_map
    
    @property
    def reservation_area(self) -> Box:
        return self._map_box

    def reserve_opening(self, name: str, reservation_no: int, opening: Box) -> bool:
        if not(self._map_box.contains(opening)):
            self.logger.error("BAD OPENING: reserve_opening reservation_map{0} cannot contain opening{1}".format(
                self._map_box.box_to_string(), opening.box_to_string()
            ))
            return False
        self.logger.debug("RESERVED: reserve_opening reservation({0}) opening{1}".format(reservation_no, opening.box_to_string()))
        for row in range(opening.upper, opening.lower):
            for col in range(opening.left, opening.right):
                self._reservation_map[row, col] = reservation_no
        self._reservations.append(BoxReservation(name, reservation_no, opening))
        return True

    def sample_to_find_unreserved_opening(
        self,
        max_party_size: Size,
        min_party_size: Size,
        margin: int,
        resize_type: ResizeType,
        step_size: int,
        rotation_increment: int,
        search_properties: BoxSearchProperties
    ) -> SampledUnreservedBoxOpening:
        native_SampledUnreservedBoxOpening = native_sample_to_find_unreserved_opening(
            self._native_reservations,
            self._reservation_map,
            self._position_buffer,
            max_party_size.to_native_size(),
            min_party_size.to_native_size(),
            margin,
            resize_type.value,
            step_size,
            rotation_increment,
            search_properties.to_native()
        )
        return SampledUnreservedBoxOpening.from_native(native_SampledUnreservedBoxOpening)
    
    def maximize_existing_reservation(self, existing_reservation: Box) -> Box:
        native_box = native_maximize_existing_reservation(
            self._native_reservations,
            self._reservation_map,
            existing_reservation.to_native()
        )
        return Box.from_native(native_box)
    
    @staticmethod
    def create_reservations(reservation_map: ReservationMapType, logger: BaseLogger):
        result = BoxReservations(logger)
        result._map_size = Size(reservation_map.shape[1], reservation_map.shape[0])
        result._map_box = Box(0, 0, result._map_size.width, result._map_size.height)
        result._buffer_length = result._map_size.area
        result._reservation_map = reservation_map
        result._position_buffer = np.zeros((result._buffer_length), dtype=ReservationMapDataType)
        result._native_reservations = native_create_box_reservations(
            result.num_threads,
            result._map_size.to_native_size(),
            result._map_box.to_native(),
            result._buffer_length,
            result._reservation_map,
            result._position_buffer
        )
        return result
        
        
    @staticmethod
    def create_reservation_map(logger: BaseLogger, map_size: Size, reservations: list[Box]) -> ReservationMapType:
        reserver = BoxReservations(logger, map_size)
        for i in range(len(reservations)):
            reserver.reserve_opening('', i+1, reservations[i])
        return reserver._reservation_map

