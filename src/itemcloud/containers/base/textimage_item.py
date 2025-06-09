from __future__ import annotations
from typing import Any, Dict, List
from itemcloud.size import Size
from itemcloud.containers.base.item import (Item, ItemType)
from itemcloud.containers.base.image_item import (
    extend_filename,
    ImageItem
)
from itemcloud.containers.base.text_item import TextItem
from itemcloud.util.colors import RGBAColor
from itemcloud.box import RotateDirection 
from itemcloud.util.display_map import (
    DISPLAY_MAP_TYPE,
    img_to_display_map
)
from itemcloud.logger.base_logger import BaseLogger
from itemcloud.util.parsers import get_value_or_default

class TextImageItem(Item):
    def __init__(
        self,
        image: ImageItem,
        text: TextItem,
        watermark_transparency: float = 1.0,
        version_stack: List[TextImageItem] = list()
    ) -> None:
        self._image = image
        self._text = text
        self._versions = version_stack

        self._watermark_transparency = watermark_transparency
        if self._text._foreground_color:
            self._text._foreground_color = self._text._foreground_color.to_transparent(watermark_transparency)
        else:
            self._text._foreground_color = RGBAColor(255,255,255, watermark_transparency * 255)
        self._text._background_color = None
        self._image = image
        self._width = image.width
        self._height = image.height
        if self.width < text.width:
            self._width = text.width
        if self.height < text.height:
            self._height = text.height
        self._combined_image = self.to_image()
        self._display_map = self._combined_image.display_map()

    @property
    def type(self) -> ItemType:
        return ItemType.TEXTIMAGE

    @property
    def display_map(self) -> DISPLAY_MAP_TYPE:
        return self._display_map

    @property
    def version_count(self) -> int:
        return len(self._versions)

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def size(self) -> tuple[int, int]:
        return (self._width, self._height)

    def all_versions(self) -> List[TextItem]:
        versions = self._versions.copy()
        versions.append(self)
        return versions
    
    def get_version(self, versionNo: int) -> TextImageItem | None:
        if versionNo < len(self._versions):
            return self._versions[versionNo]
        return None

    def reset_to_version(self, versionNo: int = 0) -> bool:
        reset_version = self.get_version(versionNo)
        if reset_version is None:
            return False
        self._image = reset_version._image
        self._text = reset_version._text
        self._versions = reset_version._version_stack

        self._watermark_transparency = reset_version._watermark_transparency
        self._width = reset_version._width
        self._height = reset_version._height
        self._combined_image = reset_version._combined_image
        self.reset_display_map()
        return True    

    def reset_to_original_version(self) -> bool:
        return self.reset_to_version()

    def reset_display_map(self) -> None:
        self._display_map = img_to_display_map(self._combined_image)        

    def resize(self, size: Size) -> TextImageItem:
        return TextImageItem(
            self._image.resize(size.width, size.height),
            self._text.resize(size.width, size.height),
            self._watermark_transparency,
            self.all_versions()
        )

    def rotate(self, angle: float) -> TextImageItem:
        return TextImageItem(
            self._image.rotate(angle),
            self._text.rotate(angle),
            self._watermark_transparency,
            self.all_versions(),
            angle
        )

    def copy(self) -> TextImageItem:
        return TextImageItem(
            self._image.copy(),
            self._text.copy(),
            self._watermark_transparency,
        )

    def to_image(
        self,
        rotated_degrees: int | None = None,
        size: Size | None = None,
        logger: BaseLogger | None = None,
        _as_watermark: bool = False
    ) -> ImageItem:
        image = self._image.to_image(
            rotated_degrees,
            size,
            logger
        )
        image = self._text.draw_on_image(
            image,
            rotated_degrees,
            size,
            logger,
            True
        )
        image.filepath = extend_filename(self._image.filepath, 'text-image')
        return image
    
    def resize_item(self, size: tuple[int, int]) -> Item:
        return self.resize(Size(size[0], size[1]))

    def rotate_item(self, angle: float, direction: RotateDirection = RotateDirection.CLOCKWISE) -> Item:
        return self.rotate(angle if direction == RotateDirection.CLOCKWISE else -1.0 * angle)
    
    def copy_item(self) -> Item:
        return self.copy()

    def to_csv_row(self) -> Dict[str, Any]:
        return self._image.to_csv_row().update(
            self._text.to_csv_row()
        ).update({
            TEXT_TRANSPARENCY_PERCENT: self._watermark_transparency
        })

    def write_row(self, name: str, directory: str, row: Dict[str, Any]) -> str:
        return self._image.write_row(name, directory, row)

    @staticmethod
    def load_row(row: Dict[str, Any]) -> Item:
        image = ImageItem.load_row(row)
        text = TextItem.load_row(row)
        return TextImageItem(
            image,
            text,
            get_value_or_default(TEXT_TRANSPARENCY_PERCENT, row, 1.0, float)
        )
    
TEXT_TRANSPARENCY_PERCENT = 'transparency_percent'