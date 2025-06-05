from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict
from enum import Enum
from itemcloud.util.display_map import DISPLAY_MAP_TYPE
from itemcloud.box import RotateDirection
from itemcloud.size import Size
from itemcloud.logger.base_logger import BaseLogger
from itemcloud.containers.base.image_item import ImageItem

class ItemType(Enum):
    IMAGE = 1
    TEXT = 2
    TEXTIMAGE = 3

class Item(ABC):

    @abstractmethod
    @property
    def type(self) -> ItemType:
        pass 

    @abstractmethod
    @property
    def display_mask(self) -> DISPLAY_MAP_TYPE:
        pass

    @abstractmethod
    @property
    def version_count(self) -> int:
        pass

    @abstractmethod
    @property
    def width(self) -> int:
        pass

    @abstractmethod
    @property
    def height(self) -> int:
        pass

    @abstractmethod
    @property
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
    ) -> ImageItem:
        pass

    @abstractmethod
    def copy_item(self) -> Item:
        pass

    @abstractmethod
    def to_csv_row(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def write_row(self, name: str, directory: str, row: Dict[str, Any]) -> str:
        pass
    
    @staticmethod
    @abstractmethod
    def load_item(row: Dict[str, Any]) -> Item:
        pass



