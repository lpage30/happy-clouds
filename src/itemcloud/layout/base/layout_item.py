from __future__ import annotations
import os
import matplotlib.patches as mpatches
from typing import Any, Dict
from itemcloud.box import Box 
from itemcloud.util.csv_utils import (
    load_rows,
    write_rows
)
from itemcloud.containers.base.item_factory import (
    create_layout_item,
    load_weighted_item_row
)
from itemcloud.util.colors import Color
from itemcloud.size import Size
from itemcloud.logger.base_logger import BaseLogger
from itemcloud.containers.base.image_item import ImageItem
from itemcloud.containers.base.item_types import ItemType
from itemcloud.containers.base.item import Item, PrimitiveItem
from itemcloud.util.display_map import DISPLAY_MAP_TYPE
from itemcloud.box import RotateDirection
from itemcloud.util.parsers import (
    filepath_to_name,
    to_existing_filepath
)
from itemcloud.reservations import Reservation
import itemcloud.layout.base.layout_defaults as layout_defaults

class LayoutItem(Item, Reservation):
    def __init__(
        self,
        name: str,
        placement_box: Box,
        rotated_degrees: int | None,
        reservation_box: Box,        
        reservation_no: int,
        latency_str: str,
        item: Item,

    ) -> None:
        Reservation.__init__(self, name, reservation_no, reservation_box, item)
        self._name = name
        self._placement_box = placement_box
        self._rotated_degrees = rotated_degrees if rotated_degrees is not None else 0
        self._reservation_color = None
        self._latency_str = latency_str

    @property
    def primitive_item(self) -> PrimitiveItem:
       return self.item.primitive_item

    @property
    def type(self) -> ItemType:
        return self.reservation_party.type

    @property
    def item(self) -> Item:
        return self.reservation_party

    @item.setter
    def item(self, value: item) -> None:
        self.reservation_party = value
    
    @property
    def display_map(self) -> DISPLAY_MAP_TYPE:
        return self.reservation_party.display_map

    @property
    def width(self) -> int:
        return self.reservation_party.width

    @property
    def height(self) -> int:
        return self.reservation_party.height

    @property
    def size(self) -> tuple[int, int]:
        return self.reservation_party.size
    
    @property
    def original_image(self) -> ImageItem:
        return self.primitive_item.original_item.to_image(
            self.rotated_degrees,
            self._placement_box.size
        )
    
    def resize_item(self, size: Size) -> Item:
        return create_layout_item(
            self.name,
            self.placement_box.resize(size),
            self.rotated_degrees,
            self.reservation_box.resize(size),
            self.reservation_no,
            self._latency_str,
            self.reservation_party.resize_item(size)
        )

    def rotate_item(self, angle: float, direction: RotateDirection = RotateDirection.CLOCKWISE) -> Item:
        return create_layout_item(
            self.name,
            self.placement_box.rotate(angle, direction),
            self.rotated_degrees + (angle if direction == RotateDirection.CLOCKWISE else -angle),
            self.reservation_box.rotate(angle, direction),
            self.reservation_no,
            self._latency_str,
            self.reservation_party.rotate_item(angle, direction)
        )

    def to_image(
        self,
        rotated_degrees: int | None = None,
        size: Size | None = None,
        logger: BaseLogger | None = None,
        as_watermark: bool = False
    ) -> ImageItem:
        return self.original_image.to_image(rotated_degrees, size, logger, as_watermark)
        
    def show(self, title: str | None = None) -> None:
        self.reservation_party.show(title)

    def copy_item(self) -> Item:
        return create_layout_item(
            self.name,
            self.placement_box,
            self.rotated_degrees,
            self.reservation_box,
            self.reservation_no,
            self._latency_str,
            self.reservation_party.copy_item()
        )

    def to_csv_row(self, directory: str = '.') -> Dict[str, Any]:
        return {
            layout_defaults.LAYOUT_ITEM_FILEPATH: self.to_write_item_filename(directory, self.item.name),
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
            layout_defaults.LAYOUT_ITEM_LATENCY: self._latency_str,
            layout_defaults.LAYOUT_ITEM_TYPE: self.reservation_party.type.name
        }

    def write_row(self, directory: str, name: str, row: Dict[str, Any]) -> str:
        row[layout_defaults.LAYOUT_ITEM_FILEPATH] = self.primitive_item.original_item.write_row(directory, self.reservation_party.name, self.reservation_party.to_csv_row(directory))
        return write_rows(self.to_write_item_filename(directory, name), [row])

    @staticmethod
    def load_row(row: Dict[str, Any]) -> Item:
        item_rows = load_rows(row[layout_defaults.LAYOUT_ITEM_FILEPATH])
        placement_box = Box(
            int(row[layout_defaults.LAYOUT_ITEM_POSITION_X]),
            int(row[layout_defaults.LAYOUT_ITEM_POSITION_Y]),
            int(row[layout_defaults.LAYOUT_ITEM_POSITION_X]) + int(row[layout_defaults.LAYOUT_ITEM_SIZE_WIDTH]),
            int(row[layout_defaults.LAYOUT_ITEM_POSITION_Y]) + int(row[layout_defaults.LAYOUT_ITEM_SIZE_HEIGHT])
        )
        rotated_degrees = int(row[layout_defaults.LAYOUT_ITEM_ROTATED_DEGREES]) if row[layout_defaults.LAYOUT_ITEM_ROTATED_DEGREES] is not None else None
        reservation_box = Box(
            int(row[layout_defaults.LAYOUT_ITEM_RESERVATION_POSITION_X]),
            int(row[layout_defaults.LAYOUT_ITEM_RESERVATION_POSITION_Y]),
            int(row[layout_defaults.LAYOUT_ITEM_RESERVATION_POSITION_X]) + int(row[layout_defaults.LAYOUT_ITEM_RESERVATION_SIZE_WIDTH]),
            int(row[layout_defaults.LAYOUT_ITEM_RESERVATION_POSITION_Y]) + int(row[layout_defaults.LAYOUT_ITEM_RESERVATION_SIZE_HEIGHT])
        )
        item = load_weighted_item_row(item_rows[0])
        item = item.resize_item(placement_box.size)
        if rotated_degrees is not None:
            item = item.rotate_item(rotated_degrees)
        return create_layout_item(
            filepath_to_name(row[layout_defaults.LAYOUT_ITEM_FILEPATH]),
            placement_box,
            rotated_degrees,
            reservation_box,
            int(row[layout_defaults.LAYOUT_ITEM_RESERVATION_NO]),
            row[layout_defaults.LAYOUT_ITEM_LATENCY],
            item
        )
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
    def reservation_color(self) -> Color | None:
        return self._reservation_color

    @reservation_color.setter 
    def reservation_color(self, color: Color) -> None:
        self._reservation_color = color

    
    def to_legend_handle(self) -> mpatches.Patch:
        return mpatches.Patch(
            color=self.reservation_color.hex_code,
            label=self.name
        )

    def write_item(self, directory: str, name: str) -> str:
        return self.write_row(directory, name, self.to_csv_row(directory))
        

    def load_item(self, filepath: str) -> None:
        item: LayoutItem = self.load_row(load_rows(filepath)[0])
        self._name = item.name
        self._placement_box = item.placement_box
        self._rotated_degrees = item.rotated_degrees
        self._reservation_box = item.reservation_box
        self._reservation_no = item.reservation_no
        self._reservation_color = None
        self._latency_str = item.latency_str
        self.reservation_party = item.item

    def to_reserved_item(self, placement_box: Box, rotated_degrees: int, reservation_box: Box, latency_str: str, item: Item | None = None) -> LayoutItem:
        return create_layout_item(
            self.name,
            placement_box,
            rotated_degrees,
            reservation_box,
            self.reservation_no,
            latency_str,
            self.reservation_party if item is None else item
        )

    def write(self, layout_directory: str) -> Dict[str,Any]:
        result = self.to_csv_row(layout_directory)
        self.write_row(layout_directory, self._name, result)
        return result
    
    @staticmethod
    def pluck_item_rows(row: Dict[str,Any], _row_no: int, layout_directory: str) -> Dict[str, Any]:
        return {
            layout_defaults.LAYOUT_ITEM_FILEPATH: to_existing_filepath(row[layout_defaults.LAYOUT_ITEM_FILEPATH], layout_directory),
            layout_defaults.LAYOUT_ITEM_POSITION_X: row[layout_defaults.LAYOUT_ITEM_POSITION_X],
            layout_defaults.LAYOUT_ITEM_POSITION_Y: row[layout_defaults.LAYOUT_ITEM_POSITION_Y],
            layout_defaults.LAYOUT_ITEM_SIZE_WIDTH: row[layout_defaults.LAYOUT_ITEM_SIZE_WIDTH],
            layout_defaults.LAYOUT_ITEM_SIZE_HEIGHT: row[layout_defaults.LAYOUT_ITEM_SIZE_HEIGHT],
            layout_defaults.LAYOUT_ITEM_ROTATED_DEGREES: row[layout_defaults.LAYOUT_ITEM_ROTATED_DEGREES],
            layout_defaults.LAYOUT_ITEM_RESERVATION_POSITION_X: row[layout_defaults.LAYOUT_ITEM_RESERVATION_POSITION_X],
            layout_defaults.LAYOUT_ITEM_RESERVATION_POSITION_Y: row[layout_defaults.LAYOUT_ITEM_RESERVATION_POSITION_Y],
            layout_defaults.LAYOUT_ITEM_RESERVATION_SIZE_WIDTH: row[layout_defaults.LAYOUT_ITEM_RESERVATION_SIZE_WIDTH],
            layout_defaults.LAYOUT_ITEM_RESERVATION_SIZE_HEIGHT: row[layout_defaults.LAYOUT_ITEM_RESERVATION_SIZE_HEIGHT],
            layout_defaults.LAYOUT_ITEM_RESERVATION_NO: row[layout_defaults.LAYOUT_ITEM_RESERVATION_NO],
            layout_defaults.LAYOUT_ITEM_LATENCY: row[layout_defaults.LAYOUT_ITEM_LATENCY],
            layout_defaults.LAYOUT_ITEM_TYPE: row[layout_defaults.LAYOUT_ITEM_TYPE]
        }
    
    