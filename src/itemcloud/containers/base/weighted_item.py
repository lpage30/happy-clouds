from __future__ import annotations
from typing import Any, Dict, List
from math import sqrt
from itemcloud.size import (
    ResizeType,
    Size,
)
from itemcloud.containers.base.item_factory import create_layout_item, create_weighted_item
from itemcloud.containers.base.item import Item
from itemcloud.containers.base.item_types import ITEM_WEIGHT
from itemcloud.containers.base.named_item import NamedItem
from itemcloud.layout.base.layout_item import LayoutItem
from itemcloud.box import Box
from itemcloud.box import RotateDirection
from itemcloud.util.csv_utils import load_rows
from itemcloud.containers.base.item_factory import create_weighted_item
from itemcloud.native.weighted_size import (
    native_create_weighted_size,
    native_create_weighted_size_array,
    native_resize_to_proportionally_fit,  
)
class WeightedItem(NamedItem):
    weight: float
    def __init__(self, weight: float, name: str, item: Item) -> None:
        NamedItem.__init__(self, name, item)
        self.weight = weight

    def resize_item(self, size: Size) -> Item:
        return create_weighted_item(self.weight, super().resize_item(size))

    def rotate_item(self, angle: float, direction: RotateDirection = RotateDirection.CLOCKWISE) -> Item:
        return create_weighted_item(self.weight, super().rotate_item(angle, direction))

    def copy_item(self) -> Item:
        return create_weighted_item(self.weight, super().copy_item())

    def to_csv_row(self, directory: str = '.') -> Dict[str, Any]:
        result = super().to_csv_row(directory)
        result.update({
            ITEM_WEIGHT: self.weight,
        })
        return result

    def to_layout_item(
        self,
        placement_box: Box,
        rotated_degrees: int,
        reservation_box: Box,        
        reservation_no: int,
        latency_str: str
    ) -> LayoutItem:
        return create_layout_item(
            self.name,
            placement_box,
            rotated_degrees,
            reservation_box,
            reservation_no,
            latency_str,
            self
        )
    
    def to_fitted_weighted_item(
        self, 
        weight: float,
        width: int,
        height: int
    ) -> WeightedItem:
        return create_weighted_item(
            weight,
            self.resize_item(Size(width, height))
        )

    @staticmethod
    def load_row(row: Dict[str, Any]) -> Item:
        return create_weighted_item(float(row[ITEM_WEIGHT]), NamedItem.load_row(row))

    @staticmethod
    def load_item(filepath: str) -> NamedItem:
        row = load_rows(filepath)[0]
        return WeightedItem.load_row(row)


def to_native_weighted_size(weighted_item: WeightedItem):
    return native_create_weighted_size(weighted_item.weight, weighted_item.to_native_size())

def from_native_weighted_size(weighted_item: WeightedItem, native_weighted_size) -> WeightedItem:
    size = Size.from_native(native_weighted_size['size'])
    return weighted_item.to_fitted_weighted_item(
        native_weighted_size['weight'],
        size.width,
        size.height
    )
def sort_by_weight(
    weighted_items: list[WeightedItem],
    reverse: bool
) -> list[WeightedItem]:
    return sorted(weighted_items, key=lambda i: i.weight, reverse=reverse)

def resize_items_to_proportionally_fit(
    weighted_items: list[WeightedItem],
    fit_size: Size,
    margin: int
) -> List[WeightedItem]:
    margin_area = (len(weighted_items) * (margin*4))
    margin_fit_area = fit_size.area - margin_area
    if margin_fit_area <= 0:
        raise ValueError(f"Unable to proportionally fit {len(weighted_items)} in {fit_size.size_to_string()} ({fit_size.area}) area due to margin {margin} taking up {margin_area} space.")
    total_weight = sum(item.weight for item in weighted_items)
    result: List[WeightedItem] = list()
    for witem in weighted_items:
        item_size = witem.item_size
        target_area = witem.weight / total_weight * margin_fit_area
        new_size = item_size.scale(sqrt(target_area/item_size.area))
        new_item = witem.item.resize_item(new_size)
        result.append(
            WeightedItem(witem.weight, witem.name, new_item)
        )
        margin_fit_area -= new_size.area
        total_weight -= witem.weight

    return result
    