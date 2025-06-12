from __future__ import annotations
from itemcloud.containers.base.item_factory import load_item_row
from itemcloud.containers.base.item import Item
from itemcloud.containers.base.item_types import ITEM_NAME
from itemcloud.containers.base.image_item import ImageItem
from itemcloud.containers.base.item_types import ItemType
from itemcloud.containers.base.item import Item
from itemcloud.util.display_map import DISPLAY_MAP_TYPE
from itemcloud.util.csv_utils import load_rows
from itemcloud.containers.base.item_factory import create_named_item
from itemcloud.box import RotateDirection

from itemcloud.size import Size
from itemcloud.logger.base_logger import BaseLogger
from typing import Any, Dict

class NamedItem(Item):
    
    def __init__(self, name: str, item: Item) -> None:
        self._name = name if name is not None else ''
        self._item = item
    
    @property
    def type(self) -> ItemType:
        return self._item.type

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

    def resize_item(self, size: tuple[int, int]) -> Item:
        return create_named_item(self._name, self._item.resize_item(size))

    def rotate_item(self, angle: float, direction: RotateDirection = RotateDirection.CLOCKWISE) -> Item:
        return create_named_item(self._name, self._item.rotate_item(angle, direction))

    def to_image(
        self,
        rotated_degrees: int | None = None,
        size: Size | None = None,
        logger: BaseLogger | None = None,
        as_watermark: bool = False
    ) -> ImageItem:
        return self._item.to_image(rotated_degrees, size, logger, as_watermark)

    def copy_item(self) -> Item:
        return create_named_item(
            self._name,
            self._item.copy_item()
        )

    def to_csv_row(self) -> Dict[str, Any]:
        return {
            ITEM_NAME: self.name,
        }.update(self.item.to_csv_row())

    def write_row(self, name: str, directory: str, row: Dict[str, Any]) -> str:
        return self.item.write_row(name, directory, row)        
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def item(self) -> Item:
        return self._item
    
    @item.setter
    def item(self, new_item) -> None:
        self._item = new_item
    

    def write_item(self, name: str, directory: str) -> str:
        row = self.to_csv_row()
        row[ITEM_NAME] = name
        return self.write_row(name, directory, row)
    
    @staticmethod
    def load_row(row: Dict[str, Any]) -> Item:
        return create_named_item(row[ITEM_NAME], load_item_row(row))

    @staticmethod
    def load_item(filepath: str) -> NamedItem:
        row = load_rows(filepath)[0]
        return NamedItem.load_row(row)    
