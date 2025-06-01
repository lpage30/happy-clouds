import os
from typing import (Dict, Any)
from itemcloud.image_item import ImageItem
from itemcloud.size import Size
from itemcloud.util.parsers import to_unused_filepath, validate_row
from itemcloud.containers.base.named_item import NamedItem
from itemcloud.logger.base_logger import BaseLogger

class NamedImage(NamedItem):
    
    def __init__(self, image: ImageItem, name: str | None = None, original_image: ImageItem | None = None) -> None:
        NamedItem.__init__(self, name, image.width, image.height)
        self._original_image = original_image if original_image is not None else image
        self._image = image
    
    def copy_named_image(self) -> "NamedImage":
        return NamedImage(
            self._image,
            self.name,
            self._original_image
        )

    @property
    def image(self) -> ImageItem:
        return self._image

    def resize(self, size: Size) -> "NamedImage":
        return NamedImage(
            self.image.resize((size.width, size.height)),
            self.name,
            self._original_image
        )

    def show(self) -> None:
        self.image.show(self.name)

    def to_image(
        self,
        rotated_degrees: int | None = None,
        size: Size | None = None,
        logger: BaseLogger | None = None,
        as_watermark: bool = False
    ) -> ImageItem:
        new_image = self.image
        if rotated_degrees is not None and 0 < rotated_degrees:
            if logger:
                logger.info('Rotating {0} {1} degrees'.format(self.name, rotated_degrees))
            # always rotate clockwise (negative degrees)
            new_image = new_image.rotate(-rotated_degrees, expand=1)
        
        if size is not None and new_image.size != size.image_tuple:
            if logger:
                logger.info('Resizing {0} ({1},{2}) -> {3}'.format(
                    self.name,
                    new_image.width, new_image.height,
                    size.size_to_string()
                ))
            new_image = new_image.resize(size.image_tuple)
        if as_watermark:
            new_image = new_image.convert('RGBA')
        return new_image

    def write_item(self, item_name: str, layout_directory: str) -> str:
        image_filepath = to_unused_filepath(layout_directory, item_name, 'png')
        self._image.save(image_filepath, 'png')
        return image_filepath

    @staticmethod
    def load_item(image_filepath: str) -> "NamedImage":
        name = os.path.splitext(os.path.basename(image_filepath))[0]
        image = ImageItem.open(image_filepath)
        return NamedImage(image, name)

    @staticmethod
    def load(row: Dict[str, Any]) -> "NamedImage":
        validate_row(row, [IMAGE_FILEPATH])
        return NamedImage.load_item(row[IMAGE_FILEPATH])


IMAGE_FILEPATH = 'image_filepath'