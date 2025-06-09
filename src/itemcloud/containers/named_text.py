from __future__ import annotations
from itemcloud.containers.base.image_item import ImageItem
from itemcloud.containers.base.named_item import NamedItem, ITEM_NAME
from itemcloud.size import Size
from itemcloud.logger.base_logger import BaseLogger
from itemcloud.containers.base.text_item import (TextItem, TEXT_ITEM_HEADERS)

class NamedText(NamedItem):

    def __init__(
        self,
        name: str,
        text: TextItem
    ) -> None:
        super().__init__(name, text)

    def draw_on_image(
        self,
        image: ImageItem,
        rotated_degrees: int | None = None,
        size: Size | None = None,
        logger: BaseLogger | None = None,
        as_watermark: bool = False,
        xy: tuple[float, float] | None = None,
    ) -> ImageItem:
        return self.item.draw_on_image(
            image,
            rotated_degrees,
            size,
            logger,
            as_watermark,
            xy
        )


TEXT_HEADERS = [
    ITEM_NAME,
    *TEXT_ITEM_HEADERS
]