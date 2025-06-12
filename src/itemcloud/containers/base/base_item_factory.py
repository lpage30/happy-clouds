from typing import Any, Dict
from types import ModuleType
from itemcloud.util.parsers import field_exists
from itemcloud.containers.base.item_types import ItemType, IMAGE_FILEPATH, TEXT_TEXT


def get_item_type(row: Dict[str, Any]) -> ItemType:
    if field_exists(TEXT_TEXT, row) and field_exists(IMAGE_FILEPATH, row):
        return ItemType.TEXTIMAGE
    elif field_exists(TEXT_TEXT, row):
        return ItemType.TEXT
    elif field_exists(IMAGE_FILEPATH, row):
        return ItemType.IMAGE
    else:
        raise ValueError('Unable to resolve row to ItemType {0}'.format(row.__str__()))

def load_item_module(type: ItemType) -> ModuleType:
    match type:
        case ItemType.IMAGE:
            return __import__('itemcloud.containers.base.image_item').containers.base.image_item
        case ItemType.TEXT:
            return __import__('itemcloud.containers.base.text_item').containers.base.text_item
        case ItemType.TEXTIMAGE:
            return __import__('itemcloud.containers.base.textimage_item').containers.base.textimage_item
        case _:
            raise ValueError(f"unsupported ItemType {type.name}")

def load_nameditem_module(type: ItemType) -> ModuleType:
    match type:
        case ItemType.IMAGE:
            return __import__('itemcloud.containers.named_image').containers.named_image
        case ItemType.TEXT:
            return __import__('itemcloud.containers.named_text').containers.named_text
        case ItemType.TEXTIMAGE:
            return __import__('itemcloud.containers.named_textimage').containers.named_textimage
        case _:
            raise ValueError(f"unsupported ItemType {type.name}")

def load_weighteditem_module(type: ItemType) -> ModuleType:
    match type:
        case ItemType.IMAGE:
            return __import__('itemcloud.containers.weighted_image').containers.weighted_image
        case ItemType.TEXT:
            return __import__('itemcloud.containers.weighted_text').containers.weighted_text
        case ItemType.TEXTIMAGE:
            return __import__('itemcloud.containers.weighted_textimage').containers.weighted_textimage
        case _:
            raise ValueError(f"unsupported ItemType {type.name}")

def load_layoutitem_module(type: ItemType) -> ModuleType:
    match type:
        case ItemType.IMAGE:
            return __import__('itemcloud.layout.layout_image').layout.layout_image
        case ItemType.TEXT:
            return __import__('itemcloud.layout.layout_text').layout.layout_text
        case ItemType.TEXTIMAGE:
            return __import__('itemcloud.layout.layout_textimage').layout.layout_textimage
        case _:
            raise ValueError(f"unsupported ItemType {type.name}")
