from __future__ import annotations
from itemcloud.containers.base.image_item import ImageItem
from itemcloud.containers.base.item import Item, ItemType
from itemcloud.item_factory import load_item, create_named_item
from itemcloud.size import Size
from itemcloud.logger.base_logger import BaseLogger
from typing import Any, Dict

class NamedItem:
    
    def __init__(self, name: str, item: Item) -> None:
        self._name = name if name is not None else ''
        self._item = item
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def item(self) -> Item:
        return self._item

    @property
    def type(self) -> ItemType:
        return self._item.type

    def copy(self) -> NamedItem:
        return create_named_item(
            self.name,
            self.item.copy_item()
        )

    def to_image(
        self,
        rotated_degrees: int | None = None,
        size: Size | None = None,
        logger: BaseLogger | None = None,
        as_watermark: bool = False
    ) -> ImageItem:
        return self.item.to_image(rotated_degrees, size, logger, as_watermark)

    def resize(self, size: Size) -> NamedItem:
        return  create_named_item(
            self.name,
            self.item.resize_item((size.width, size.height))
        )

    def to_csv_row(self) -> Dict[str, Any]:
        return {
            ITEM_NAME: self.name,
        }.update(self.item.to_csv_row())

    def write_row(self, name: str, directory: str, row: Dict[str, Any]) -> str:
        return self.item.write_row(name, directory, row)        

    @staticmethod
    def load(row: Dict[str, Any]) -> NamedItem:
        return create_named_item(row[ITEM_NAME], load_item(row))

ITEM_NAME = 'name'
    
