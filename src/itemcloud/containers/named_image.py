from __future__ import annotations
from itemcloud.containers.base.image_item import ImageItem
from itemcloud.containers.base.named_item import NamedItem

class NamedImage(NamedItem):
    
    def __init__(self, image: ImageItem, name: str | None = None, original_image: ImageItem | None = None) -> None:
        NamedItem.__init__(self, name, image)
        self._original_image = original_image if original_image is not None else image

    @property
    def image(self) -> ImageItem:
        return self._image

    def show(self) -> None:
        self.image.show(self.name)
