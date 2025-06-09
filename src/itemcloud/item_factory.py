import csv
from typing import Any, Dict, List
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


def create_named_item(name: str, item: Item) -> NamedItem:
    match item.type:
        case ItemType.IMAGE:
            return NamedImage(item, name)
        case ItemType.TEXT:
            return NamedText(name, item)
        case ItemType.TEXTIMAGE:
            return NamedTextImage(name, item)
        case _:
            raise ValueError(f"unsupported ItemType {item.type.name}")


def create_weighted_item(weight: float, named_item: NamedItem) -> WeightedItem:
    match named_item.type:
        case ItemType.IMAGE:
            return WeightedImage(weight, named_item)
        case ItemType.TEXT:
            return WeightedText(weight, named_item)
        case ItemType.TEXTIMAGE:
            return WeightedTextImage(weight, named_item)
        case _:
            raise ValueError(f"unsupported ItemType {named_item.type.name}")

def create_layout_item(
    name: str,
    placement_box: Box,
    rotated_degrees: int | None,
    reservation_box: Box,        
    reservation_no: int,
    latency_str: str,
    item: Item
) -> LayoutItem:
    match item.type:
        case ItemType.IMAGE:
            return LayoutImage(name, placement_box, rotated_degrees, reservation_box, reservation_no, latency_str, item)
        case ItemType.TEXT:
            return LayoutText(name, placement_box, rotated_degrees, reservation_box, reservation_no, latency_str, item)
        case ItemType.TEXTIMAGE:
            return LayoutTextImage(name, placement_box, rotated_degrees, reservation_box, reservation_no, latency_str, item)
        case _:
            raise ValueError(f"unsupported ItemType {type.name}")

def load_item_row(row: Dict[str, Any]) -> Item:
    type = get_item_type(row)
    match type:
        case ItemType.IMAGE:
            return ImageItem.load_row(row)
        case ItemType.TEXT:
            return TextItem.load_row(row)
        case ItemType.TEXTIMAGE:
            return TextImageItem.load_row(row)
        case _:
            raise ValueError(f"unsupported ItemType {type.name}")

def load_named_item_row(row: Dict[str, Any]) -> NamedItem:
    item = load_item_row(row)
    match item.type:
        case ItemType.IMAGE:
            return NamedImage(item, item.name)
        case ItemType.TEXT:
            return NamedText(row[ITEM_NAME], item)
        case ItemType.TEXTIMAGE:
            return NamedTextImage(item.name, item)
        case _:
            raise ValueError(f"unsupported ItemType {item.type.name}")

def load_weighted_item_row(row: Dict[str, Any]) -> WeightedItem:
    named_item = load_named_item_row(row)
    weight = float(row[ITEM_WEIGHT])
    match named_item.type:
        case ItemType.IMAGE:
            return WeightedImage(weight, named_item)
        case ItemType.TEXT:
            return WeightedText(weight, named_item)
        case ItemType.TEXTIMAGE:
            return WeightedTextImage(weight, named_item)
        case _:
            raise ValueError(f"unsupported ItemType {item.type.name}")

def load_rows(csv_filepath: str) -> List[Dict[str, Any]]:
    try:
        result: List[Dict[str, Any]] = list()
        with open(csv_filepath, 'r', encoding='utf-8-sig') as file:    
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                result.append(row)
        return result
    except Exception as e:
        raise Exception(str(e))

def write_rows(csv_filepath: str, rows: List[Dict[str,Any]]) -> str:
    field_names = {}
    for row in rows:
        field_names = sorted(field_names.update(set(row.keys())))
    field_names = list(field_names)
    empty_row = dict.fromkeys(field_names)
    try:
        with open(csv_filepath, 'w') as file:
            csv_writer = csv.DictWriter(file, fieldnames=field_names)
            csv_writer.writeheader()
            for row in rows:
                record = dict()
                record.update(empty_row)
                record.update(row)
                csv_writer.writerow(dict(sorted(record.entries())))
        return csv_filepath        
    except Exception as e:
        raise Exception(str(e))
