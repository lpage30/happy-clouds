from abc import ABC, abstractmethod
import os
from PIL import Image
import matplotlib.patches as mpatches
from typing import Any, Dict, Callable
from itemcloud.box import Box
from itemcloud.util.colors import Color
from itemcloud.logger.base_logger import BaseLogger
from itemcloud.containers.named_image import NamedImage
from itemcloud.util.parsers import (is_empty, to_existing_filepath)
import itemcloud.layout.layout_defaults as layout_defaults

create_layout_item_f = Callable[
    [
        str, #name
        Box, #placement_box
        int, #rotated_degrees
        Box, #reservation_box
        int, #reservation_no
        str, #item_latency
    ],
    "LayoutItem"
]
class LayoutItem(ABC):
    def __init__(
        self,
        name: str,
        placement_box: Box,
        rotated_degrees: int | None,
        reservation_box: Box,        
        reservation_no: int,
        latency_str: str = ''
    ) -> None:
        
        self._name = name
        self._placement_box = placement_box
        self._rotated_degrees = rotated_degrees if rotated_degrees is not None else 0
        self._reservation_box = reservation_box
        self._reservation_no = reservation_no
        self._reservation_color = None
        self._latency_str = latency_str
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def placement_box(self) -> Box:
        return self._placement_box
        
    @property
    def rotated_degrees(self) -> int | None:
        return self._rotated_degrees

    @property    
    def reservation_box(self) -> Box:
        return self._reservation_box

    @property
    def reservation_no(self) -> int:
        return self._reservation_no
    
    @property
    def reservation_color(self) -> Color | None:
        return self._reservation_color

    @reservation_color.setter 
    def reservation_color(self, color: Color) -> None:
        self._reservation_color = color

    def to_image(
        self,
        logger: BaseLogger,
        scale: float = 1.0
    ) -> NamedImage:
        new_named_image = self.get_item_as_named_image()
        new_image = new_named_image.image

        if 0 < self.rotated_degrees:
            logger.info('Rotating {0} {1} degrees'.format(self.name, self.rotated_degrees))
            # always rotate clockwise (negative degrees)
            new_image = new_image.rotate(-self.rotated_degrees, expand=1)
        
        new_size = self.placement_box.size.scale(scale)
        if new_image.size != new_size.image_tuple:
            logger.info('Resizing {0} ({1},{2}) -> {3}'.format(
                new_named_image.name,
                new_image.size[0], new_image.size[1],
                new_size.size_to_string()
            ))
            new_image = new_image.resize(new_size.image_tuple)
        return NamedImage(new_image, new_named_image.name, new_named_image.image)

    def to_legend_handle(self) -> mpatches.Patch:
        return mpatches.Patch(
            color=self.reservation_color.hex_code,
            label=self.name
        )

    def write(self, layout_directory: str) -> Dict[str,Any]:
        item_filepath = self.write_item(self._name, layout_directory)
        
        return {
            layout_defaults.LAYOUT_ITEM_FILEPATH: item_filepath,
            layout_defaults.LAYOUT_ITEM_POSITION_X: self.placement_box.left,
            layout_defaults.LAYOUT_ITEM_POSITION_Y: self.placement_box.upper,
            layout_defaults.LAYOUT_ITEM_SIZE_WIDTH: self.placement_box.width,
            layout_defaults.LAYOUT_ITEM_SIZE_HEIGHT: self.placement_box.height,
            layout_defaults.LAYOUT_ITEM_ROTATED_DEGREES: self.rotated_degrees,
            layout_defaults.LAYOUT_ITEM_RESERVATION_POSITION_X: self.reservation_box.left,
            layout_defaults.LAYOUT_ITEM_RESERVATION_POSITION_Y: self.reservation_box.upper,
            layout_defaults.LAYOUT_ITEM_RESERVATION_SIZE_WIDTH: self.reservation_box.width,
            layout_defaults.LAYOUT_ITEM_RESERVATION_SIZE_HEIGHT: self.reservation_box.height,
            layout_defaults.LAYOUT_ITEM_RESERVATION_NO: self.reservation_no,
            layout_defaults.LAYOUT_ITEM_LATENCY: self._latency_str
        }

    @abstractmethod
    def get_item_as_named_image(self) -> NamedImage:
        pass

    @abstractmethod
    def write_item(self, item_name: str, layout_directory: str) -> str:
        pass

    @abstractmethod
    def load_item(self, item_filepath: str) -> None:
        pass

    @abstractmethod
    def to_reserved_item(self, placement_box: Box, rotated_degrees: int, reservation_box: Box, latency_str: str) -> "LayoutItem":
        pass

    @staticmethod
    def empty_csv_data() -> Dict[str,Any]:
        return { header:'' for header in layout_defaults.LAYOUT_ITEM_HEADERS }

    @staticmethod
    def load(
        row: Dict[str,Any],
        row_no: int,
        layout_directory: str,
        create_layout: create_layout_item_f
    ):
        if all([is_empty(row[header])  for header in layout_defaults.LAYOUT_ITEM_HEADERS]): 
            return None

        placement_box = Box(
            int(row[layout_defaults.LAYOUT_ITEM_POSITION_X]),
            int(row[layout_defaults.LAYOUT_ITEM_POSITION_Y]),
            int(row[layout_defaults.LAYOUT_ITEM_POSITION_X]) + int(row[layout_defaults.LAYOUT_ITEM_SIZE_WIDTH]), 
            int(row[layout_defaults.LAYOUT_ITEM_POSITION_Y]) + int(row[layout_defaults.LAYOUT_ITEM_SIZE_HEIGHT])
        )
        reservation_box = placement_box
        reservation_headers = [
            layout_defaults.LAYOUT_ITEM_RESERVATION_POSITION_X,
            layout_defaults.LAYOUT_ITEM_RESERVATION_POSITION_Y,
            layout_defaults.LAYOUT_ITEM_RESERVATION_SIZE_WIDTH,
            layout_defaults.LAYOUT_ITEM_RESERVATION_SIZE_HEIGHT
        ]

        if all([header in row and not(is_empty(row[header])) for header in reservation_headers]):
            reservation_box = Box(
                int(row[layout_defaults.LAYOUT_ITEM_RESERVATION_POSITION_X]),
                int(row[layout_defaults.LAYOUT_ITEM_RESERVATION_POSITION_Y]),
                int(row[layout_defaults.LAYOUT_ITEM_RESERVATION_POSITION_X]) + int(row[layout_defaults.LAYOUT_ITEM_RESERVATION_SIZE_WIDTH]), 
                int(row[layout_defaults.LAYOUT_ITEM_RESERVATION_POSITION_Y]) + int(row[layout_defaults.LAYOUT_ITEM_RESERVATION_SIZE_HEIGHT])
            )
        item_filepath = to_existing_filepath(row[layout_defaults.LAYOUT_ITEM_FILEPATH], layout_directory)
        item = create_layout(
            os.path.splitext(os.path.basename(item_filepath))[0],
            placement_box,
            int(row[layout_defaults.LAYOUT_ITEM_ROTATED_DEGREES]) if not(is_empty(row[layout_defaults.LAYOUT_ITEM_ROTATED_DEGREES])) else 0,
            reservation_box,
            int(row[layout_defaults.LAYOUT_ITEM_RESERVATION_NO]) if not(is_empty(row[layout_defaults.LAYOUT_ITEM_RESERVATION_NO])) else row_no,
            row[layout_defaults.LAYOUT_ITEM_LATENCY] if not(is_empty(row[layout_defaults.LAYOUT_ITEM_LATENCY])) else ''
        )
        item.load_item(item_filepath)
        return item
    