from __future__ import annotations
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
from itemcloud.containers.base.item import Item
from itemcloud.util.display_map import DISPLAY_MAP_TYPE
from itemcloud.box import RotateDirection
from itemcloud.util.parsers import (
    filepath_to_name
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
        Reservation.__init__(self, name, reservation_no, reservation_box, item.display_map)
        self._name = name
        self._placement_box = placement_box
        self._rotated_degrees = rotated_degrees if rotated_degrees is not None else 0
        self._reservation_color = None
        self._latency_str = latency_str
        self._item = item


    @property
    def type(self) -> ItemType:
        return self._item.type

    @property
    def item(self) -> Item:
        return self._item

    @item.setter
    def item(self, value: item) -> None:
        self._item = value
    
    @property
    def display_map(self) -> DISPLAY_MAP_TYPE:
        return self._item.display_map

    @property
    def version_count(self) -> int:
        return self._item.version_count

    @property
    def width(self) -> int:
        return self._item.width

    @property
    def height(self) -> int:
        return self._item.height

    @property
    def size(self) -> tuple[int, int]:
        return self._item.size
    
    def reset_to_original_version(self) -> bool:
        return self._item.reset_to_original_version()

    def resize_item(self, size: Size) -> Item:
        return create_layout_item(
            self.name,
            self.placement_box.resize(size),
            self.rotated_degrees,
            self.reservation_box.resize(size),
            self.reservation_no,
            self._latency_str,
            self._item.resize_item(size)
        )

    def rotate_item(self, angle: float, direction: RotateDirection = RotateDirection.CLOCKWISE) -> Item:
        return create_layout_item(
            self.name,
            self.placement_box.rotate(angle, direction),
            self.rotated_degrees + (angle if direction == RotateDirection.CLOCKWISE else -angle),
            self.reservation_box.rotate(angle, direction),
            self.reservation_no,
            self._latency_str,
            self._item.rotate_item(angle, direction)
        )

    def to_image(
        self,
        rotated_degrees: int | None = None,
        size: Size | None = None,
        logger: BaseLogger | None = None,
        as_watermark: bool = False
    ) -> ImageItem:
        return self._item.to_image(rotated_degrees, size, logger, as_watermark)
        
    def show(self, title: str | None = None) -> None:
        self._item.show(title)

    def copy_item(self) -> Item:
        return create_layout_item(
            self.name,
            self.placement_box,
            self.rotated_degrees,
            self.reservation_box,
            self.reservation_no,
            self._latency_str,
            self._item.copy_item()
        )

    def to_csv_row(self) -> Dict[str, Any]:
        return {
            layout_defaults.LAYOUT_ITEM_FILEPATH: self.to_write_item_filename(self._name, ),
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
            layout_defaults.LAYOUT_ITEM_TYPE: self._item.type.name
        }

    def write_row(self, name: str, directory: str, row: Dict[str, Any]) -> str:
        row[layout_defaults.LAYOUT_ITEM_FILEPATH] = self._item.write_row(name, directory, self._item.to_csv_row())
        return write_rows(self.to_write_item_filename(self._name, directory), [row])

    @staticmethod
    def load_row(row: Dict[str, Any]) -> Item:
        item = load_weighted_item_row(load_rows(row[layout_defaults.LAYOUT_ITEM_FILEPATH])[0])
        return create_layout_item(
            filepath_to_name(row[layout_defaults.LAYOUT_ITEM_FILEPATH]),
            Box(
                row[layout_defaults.LAYOUT_ITEM_POSITION_X],
                row[layout_defaults.LAYOUT_ITEM_POSITION_Y],
                row[layout_defaults.LAYOUT_ITEM_POSITION_X] + row[layout_defaults.LAYOUT_ITEM_SIZE_WIDTH],
                row[layout_defaults.LAYOUT_ITEM_POSITION_Y] + row[layout_defaults.LAYOUT_ITEM_SIZE_HEIGHT]
            ),
            row[layout_defaults.LAYOUT_ITEM_ROTATED_DEGREES],
            Box(
                row[layout_defaults.LAYOUT_ITEM_RESERVATION_POSITION_X],
                row[layout_defaults.LAYOUT_ITEM_RESERVATION_POSITION_Y],
                row[layout_defaults.LAYOUT_ITEM_RESERVATION_POSITION_X] + row[layout_defaults.LAYOUT_ITEM_RESERVATION_SIZE_WIDTH],
                row[layout_defaults.LAYOUT_ITEM_RESERVATION_POSITION_Y] + row[layout_defaults.LAYOUT_ITEM_RESERVATION_SIZE_HEIGHT]
            ),
            row[layout_defaults.LAYOUT_ITEM_RESERVATION_NO],
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

    def write_item(self, name: str, directory: str) -> str:
        return self.write_row(name, directory, self.to_csv_row())
        

    def load_item(self, filepath: str) -> None:
        item: LayoutItem = self.load_row(load_rows(filepath)[0])
        self._name = item.name
        self._placement_box = item.placement_box
        self._rotated_degrees = item.rotated_degrees
        self._reservation_box = item.reservation_box
        self._reservation_no = item.reservation_no
        self._reservation_color = None
        self._latency_str = item.latency_str
        self._item = item.item

    def to_reserved_item(self, placement_box: Box, rotated_degrees: int, reservation_box: Box, latency_str: str, item: Item | None = None) -> LayoutItem:
        return create_layout_item(
            self.name,
            placement_box,
            rotated_degrees,
            reservation_box,
            self.reservation_no,
            latency_str,
            self._item if item is None else item
        )

    def write(self, layout_directory: str) -> Dict[str,Any]:
        item_filepath = self.write_row(self._name, layout_directory, self.to_csv_row())
        result = self.to_csv_row()
        result.update({
            layout_defaults.LAYOUT_ITEM_FILEPATH: item_filepath
        })
        return result
    