from abc import ABC, abstractmethod
from typing import Callable, List
from itemcloud.size import (
    ResizeType,
    Size,
)
from itemcloud.containers.base.named_item import NamedItem
from itemcloud.layout.base.layout_item import LayoutItem
from itemcloud.box import Box
from itemcloud.native.weighted_size import (
    native_create_weighted_size,
    native_create_weighted_size_array,
    native_resize_to_proportionally_fit,  
)
class WeightedItem(NamedItem):
    weight: float
    def __init__(self, weight: float, name: str, width: int, height: int) -> None:
        NamedItem.__init__(self, name, width, height)
        self.weight = weight


    @abstractmethod
    def to_layout_item(
        self,
        placement_box: Box,
        rotated_degrees: int,
        reservation_box: Box,        
        reservation_no: int,
        latency_str: str
    ) -> LayoutItem:
        pass
    
    @abstractmethod
    def to_fitted_weighted_item(
        self, 
        weight: float,
        width: int,
        height: int
    ) -> "WeightedItem":
        pass
        
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
    resize_type: ResizeType,
    step_size: int,
    margin: int
) -> list[WeightedItem]:
    native_weighted_size_array = native_create_weighted_size_array(len(weighted_items))
    for i in range(len(weighted_items)):
        native_weighted_size_array[i] = to_native_weighted_size(weighted_items[i])
    
    native_weighted_size_array = native_resize_to_proportionally_fit(native_weighted_size_array, fit_size.to_native_size(), resize_type.value, step_size, margin)
    result: list[WeightedItem] = list()
    for i in range(len(weighted_items)):
        result.append(from_native_weighted_size(weighted_items[i], native_weighted_size_array[i]))
    return result
    

load_weighted_items_f = Callable[
    [
        str, #csv_filepath
    ],
    List[WeightedItem]
]