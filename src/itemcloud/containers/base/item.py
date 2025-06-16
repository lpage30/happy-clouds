from __future__ import annotations
from abc import abstractmethod
from typing import Any, Dict
from itemcloud.containers.base.item_types import ItemType
from itemcloud.util.display_map import DISPLAY_MAP_TYPE
from itemcloud.box import RotateDirection
from itemcloud.size import Size
from itemcloud.logger.base_logger import BaseLogger
from itemcloud.util.parsers import to_unused_filepath


class Item(Size):

    @property
    @abstractmethod
    def type(self) -> ItemType:
        pass 

    @property
    @abstractmethod
    def display_map(self) -> DISPLAY_MAP_TYPE:
        pass

    @property
    @abstractmethod
    def version_count(self) -> int:
        pass

    @property
    @abstractmethod
    def width(self) -> int:
        pass

    @property
    @abstractmethod
    def height(self) -> int:
        pass

    @property
    def item_size(self) -> Size:
        return Size(self.width, self.height)

    @abstractmethod
    def reset_to_original_version(self) -> bool:
        pass

    @abstractmethod
    def resize_item(self, size: Size) -> Item:
        pass

    @abstractmethod
    def rotate_item(self, angle: float, direction: RotateDirection = RotateDirection.CLOCKWISE) -> Item:
        pass

    def scale_item(self, scale: float) -> Item:
        if 1.0 == scale:
            return self
        return self.resize_item(self.item_size.scale(scale))
    
    @abstractmethod
    def to_image(
        self,
        rotated_degrees: int | None = None,
        size: Size | None = None,
        logger: BaseLogger | None = None,
        as_watermark: bool = False
    ) -> "ImageItem":
        pass

    @abstractmethod
    def show(self, title: str | None = None) -> None:
        pass

    @abstractmethod
    def copy_item(self) -> Item:
        pass

    @abstractmethod
    def to_csv_row(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def to_write_item_filename(self, name: str, directory: str) -> str:
        return to_unused_filepath(directory, name, 'csv')
    
    @abstractmethod
    def write_row(self, name: str, directory: str, row: Dict[str, Any]) -> str:
        pass
    
    @staticmethod
    @abstractmethod
    def load_row(row: Dict[str, Any]) -> Item:
        pass