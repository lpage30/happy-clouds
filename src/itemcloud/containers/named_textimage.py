from __future__ import annotations
from itemcloud.containers.base.textimage_item import TextImageItem
from itemcloud.containers.base.named_item import NamedItem

class NamedTextImage(NamedItem):
    def __init__(
        self, 
        name: str,
        text_image: TextImageItem,
    ) -> None:
        super().__init__(name, 0,0)
        self._text_image = text_image
    