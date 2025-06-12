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
    @abstractmethod
    def size(self) -> tuple[int, int]:
        pass

    @abstractmethod
    def reset_to_original_version(self) -> bool:
        pass

    @abstractmethod
    def resize_item(self, size: tuple[int, int]) -> Item:
        pass

    @abstractmethod
    def rotate_item(self, angle: float, direction: RotateDirection = RotateDirection.CLOCKWISE) -> Item:
        pass

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