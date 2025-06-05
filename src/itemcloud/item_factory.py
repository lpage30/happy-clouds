from typing import Any, Dict
from itemcloud.util.parsers import field_exists
from itemcloud.box import Box
from itemcloud.containers.base.item import ItemType, Item
from itemcloud.containers.base.named_item import NamedItem, ITEM_NAME
from itemcloud.containers.base.weighted_item import WeightedItem, ITEM_WEIGHT
from itemcloud.layout.base.layout_item import LayoutItem

from itemcloud.containers.base.image_item import ImageItem, IMAGE_FILEPATH
from itemcloud.containers.base.text_item import TextItem, TEXT_TEXT
from itemcloud.containers.base.textimage_item import TextImageItem

from itemcloud.containers.named_image import NamedImage
from itemcloud.containers.named_text import NamedText
from itemcloud.containers.named_textimage import NamedTextImage

from itemcloud.containers.weighted_image import WeightedImage
from itemcloud.containers.weighted_text import WeightedText
from itemcloud.containers.weighted_textimage import WeightedTextImage

from itemcloud.layout.layout_image import LayoutImage
from itemcloud.layout.layout_text import LayoutText
from itemcloud.layout.layout_textimage import LayoutTextImage

def get_item_type(row: Dict[str, Any]) -> ItemType:
    if field_exists(TEXT_TEXT, row) and field_exists(IMAGE_FILEPATH, row):
        return ItemType.TEXTIMAGE
    elif field_exists(TEXT_TEXT, row):
        return ItemType.TEXT
    elif field_exists(IMAGE_FILEPATH, row):
        return ItemType.IMAGE
    else:
        raise ValueError('Unable to resolve row to ItemType {0}'.format(row.__str__()))


def load_item(row: Dict[str, Any]) -> Item:
    type = get_item_type(row)
    match type:
        case ItemType.IMAGE:
            return ImageItem.load_item(row)
        case ItemType.TEXT:
            return TextItem.load_item(row)
        case ItemType.TEXTIMAGE:
            return TextImageItem.load_item(row)
        case _:
            raise ValueError(f"unsupported ItemType {type}")


def create_named_item(name: str, item: Item) -> NamedItem:
    match item.type:
        case ItemType.IMAGE:
            return NamedImage(item, name)
        case ItemType.TEXT:
            return NamedText(name, item)
        case ItemType.TEXTIMAGE:
            return NamedTextImage(name, item)
        case _:
            raise ValueError(f"unsupported ItemType {item.type}")


def create_weighted_item(weight: float, named_item: NamedItem) -> WeightedItem:
    match named_item.type:
        case ItemType.IMAGE:
            return WeightedImage(weight, named_item)
        case ItemType.TEXT:
            return WeightedText(weight, named_item)
        case ItemType.TEXTIMAGE:
            return WeightedTextImage(weight, named_item)
        case _:
            raise ValueError(f"unsupported ItemType {named_item.type}")

def create_layout_item(
    type: ItemType,
    name: str,
    placement_box: Box,
    rotated_degrees: int | None,
    reservation_box: Box,        
    reservation_no: int,
    latency_str: str
) -> LayoutItem:
    match type:
        case ItemType.IMAGE:
            return LayoutImage(name, placement_box, rotated_degrees, reservation_box, reservation_no, latency_str)
        case ItemType.TEXT:
            return LayoutText(name, placement_box, rotated_degrees, reservation_box, reservation_no, latency_str)
        case ItemType.TEXTIMAGE:
            return LayoutTextImage(name, placement_box, rotated_degrees, reservation_box, reservation_no, latency_str)
        case _:
            raise ValueError(f"unsupported ItemType {type}")

def load_named_item(row: Dict[str, Any]) -> NamedItem:
    item = load_item(row)
    match item.type:
        case ItemType.IMAGE:
            return NamedImage(item, item.name)
        case ItemType.TEXT:
            return NamedText(row[ITEM_NAME], item)
        case ItemType.TEXTIMAGE:
            return NamedTextImage(item.name, item)
        case _:
            raise ValueError(f"unsupported ItemType {item.type}")

def load_weighted_item(row: Dict[str, Any]) -> WeightedItem:
    named_item = load_named_item(row)
    weight = float(row[ITEM_WEIGHT])
    match named_item.type:
        case ItemType.IMAGE:
            return WeightedImage(weight, named_item)
        case ItemType.TEXT:
            return WeightedText(weight, named_item)
        case ItemType.TEXTIMAGE:
            return WeightedTextImage(weight, named_item)
        case _:
            raise ValueError(f"unsupported ItemType {item.type}")