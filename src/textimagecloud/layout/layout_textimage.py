from textimagecloud.containers.named_textimage import NamedTextImage
from itemcloud.layout.layout_item import LayoutItem
from itemcloud.box import Box
from itemcloud.logger.base_logger import BaseLogger
from itemcloud.containers.named_image import NamedImage
from itemcloud.size import Size


class LayoutTextImage(LayoutItem):
    def __init__(
        self,
        name: str,
        placement_box: Box,
        rotated_degrees: int | None,
        reservation_box: Box,        
        reservation_no: int,
        latency_str: str
    ) -> None:
        super().__init__(
            name,
            placement_box,
            rotated_degrees,
            reservation_box,
            reservation_no,
            latency_str,
            LayoutTextImage.__name__
        )    

    @property
    def original_textimage(self) -> NamedTextImage:
        return self._original_textimage

    def get_item_as_named_image(
        self,
        rotated_degrees: int | None = None,
        size: Size | None = None,
        logger: BaseLogger | None = None
    ) -> NamedImage:
        new_image = self.original_textimage.to_image(
            rotated_degrees,
            size,
            logger
        )
        return NamedImage(new_image, self.original_textimage.name)


    def write_item(self, item_name: str, layout_directory: str) -> str:
        return self.original_textimage.write_item(item_name, layout_directory)

    def load_item(self, item_filepath: str) -> None:
        self._original_textimage = NamedTextImage.load_item(item_filepath)
        self._name = self._original_textimage.name

    def to_reserved_item(
        self,
        placement_box: Box,
        rotated_degrees: int,
        reservation_box: Box,
        latency_str: str
    ) -> "LayoutItem":
        item = LayoutTextImage(
            self.original_textimage.name,
            placement_box,
            rotated_degrees,
            reservation_box,
            self.reservation_no,
            latency_str
        )
        item._original_textimage = self.original_textimage
        return item

    @staticmethod
    def create_layout_TextImage(
        name: str,
        placement_box: Box,
        rotated_degrees: int,
        reservation_box: Box,        
        reservation_no: int,
        latency_str: str,
        _subclass_type_name: str
    ) -> LayoutItem:
        return LayoutTextImage(
            name,
            placement_box,
            rotated_degrees,
            reservation_box,
            reservation_no,
            latency_str
        )