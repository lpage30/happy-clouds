from typing import Any, Dict, List
from itemcloud.box import Box
from itemcloud.util.csv_utils import load_rows
from itemcloud.containers.base.base_item_factory import (
    get_item_type,
    load_item_module,
    load_nameditem_module,
    load_weighteditem_module,
    load_layoutitem_module
)
from itemcloud.containers.base.item_types import (
    ItemType,
    ITEM_NAME,
    ITEM_WEIGHT
)
def load_item_row(row: Dict[str, Any]) -> "Item":
    type = get_item_type(row)
    module = load_item_module(type)
    match type:
        case ItemType.IMAGE:
            return module.ImageItem.load_row(row)
        case ItemType.TEXT:
            return module.TextItem.load_row_ex(row, True)
        case ItemType.TEXTIMAGE:
            return module.TextImageItem.load_row(row)
        case _:
            raise ValueError(f"unsupported ItemType {type.name}")


def create_named_item(name: str, item: "Item") -> "NamedItem":
    module = load_nameditem_module(item.type)
    match item.type:
        case ItemType.IMAGE:
            return module.NamedImage(item, name)
        case ItemType.TEXT:
            return module.NamedText(name, item)
        case ItemType.TEXTIMAGE:
            return module.NamedTextImage(name, item)
        case _:
            raise ValueError(f"unsupported ItemType {item.type.name}")


def create_weighted_item(weight: float, named_item: "NamedItem") -> "WeightedItem":
    module = load_weighteditem_module(named_item.type)
    match named_item.type:
        case ItemType.IMAGE:
            return module.WeightedImage(weight, named_item)
        case ItemType.TEXT:
            return module.WeightedText(weight, named_item)
        case ItemType.TEXTIMAGE:
            return module.WeightedTextImage(weight, named_item)
        case _:
            raise ValueError(f"unsupported ItemType {named_item.type.name}")

def create_layout_item(
    name: str,
    placement_box: Box,
    rotated_degrees: int | None,
    reservation_box: Box,        
    reservation_no: int,
    latency_str: str,
    item: "Item"
) -> "LayoutItem":
    module = load_layoutitem_module(item.type)
    match item.type:
        case ItemType.IMAGE:
            return module.LayoutImage(name, placement_box, rotated_degrees, reservation_box, reservation_no, latency_str, item)
        case ItemType.TEXT:
            return module.LayoutText(name, placement_box, rotated_degrees, reservation_box, reservation_no, latency_str, item)
        case ItemType.TEXTIMAGE:
            return module.LayoutTextImage(name, placement_box, rotated_degrees, reservation_box, reservation_no, latency_str, item)
        case _:
            raise ValueError(f"unsupported ItemType {item.type.name}")


def load_named_item_row(row: Dict[str, Any]) -> "NamedItem":
    item = load_item_row(row)
    module = load_nameditem_module(item.type)
    match item.type:
        case ItemType.IMAGE:
            return module.NamedImage(item, item.name)
        case ItemType.TEXT:
            return module.NamedText(row[ITEM_NAME], item)
        case ItemType.TEXTIMAGE:
            return module.NamedTextImage(item.name, item)
        case _:
            raise ValueError(f"unsupported ItemType {item.type.name}")

def load_weighted_item_row(row: Dict[str, Any]) -> "WeightedItem":
    named_item = load_named_item_row(row)
    module = load_weighteditem_module(named_item.type)
    weight = float(row[ITEM_WEIGHT])
    match named_item.type:
        case ItemType.IMAGE:
            return module.WeightedImage(weight, named_item)
        case ItemType.TEXT:
            return module.WeightedText(weight, named_item)
        case ItemType.TEXTIMAGE:
            return module.WeightedTextImage(weight, named_item)
        case _:
            raise ValueError(f"unsupported ItemType {named_item.type.name}")


def load_weighted_items(csv_filepath: str) -> List["WeightedItem"]:
    rows: List[Dict[str, Any]] = load_rows(csv_filepath)
    result: List["WeightedItem"] = list()
    for row in rows:
        result.append(load_weighted_item_row(row))
    return result