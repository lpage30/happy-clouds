from __future__ import annotations
from itemcloud.containers.base.image_item import ImageItem
from itemcloud.containers.base.named_item import NamedItem
from itemcloud.util.parsers import to_unused_filepath

class NamedImage(NamedItem):
    
    def __init__(self, image: ImageItem, name: str | None = None) -> None:
        NamedItem.__init__(self, name, image)

    @property
    def image(self) -> ImageItem:
        return self.item

    def show(self) -> None:
        self.image.show(self.name)

