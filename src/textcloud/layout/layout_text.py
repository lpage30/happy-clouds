from itemcloud.logger.base_logger import BaseLogger
from itemcloud.layout.layout_item import LayoutItem
from textcloud.containers.named_text import NamedText
from itemcloud.containers.named_image import NamedImage
from itemcloud.box import Box
from itemcloud.size import Size


class LayoutText(LayoutItem):

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
            LayoutText.__name__
        )    
    @property
    def original_text(self) -> NamedText:
        return self._original_text

    def get_item_as_named_image(self, rotated_degrees: int | None = None, size: Size | None = None, logger: BaseLogger | None = None) -> NamedImage:
        new_image = self.original_text.to_image(
            rotated_degrees,
            size,
            logger
        )
        return NamedImage(new_image, self.original_text.name)

    def write_item(self, item_name: str, layout_directory: str) -> str:
        return self.original_text.write_item(item_name, layout_directory)


    def load_item(self, item_filepath: str) -> None:
        self._original_text = NamedText.load_item(item_filepath)
        self._name = self.original_image.name

    def to_reserved_item(
        self, 
        placement_box: Box,
        rotated_degrees: int,
        reservation_box: Box,
        latency_str: str
    ) -> LayoutItem:
        item = LayoutText(
            self.original_text.name,
            placement_box,
            rotated_degrees,
            reservation_box,
            self.reservation_no,
            latency_str
        )
        item._original_text = self.original_text
        return item

    @staticmethod
    def create_layout_Text(
        name: str,
        placement_box: Box,
        rotated_degrees: int,
        reservation_box: Box,        
        reservation_no: int,
        latency_str: str,
        _subclass_type_name: str
    ) -> LayoutItem:
        return LayoutText(
            name,
            placement_box,
            rotated_degrees,
            reservation_box,
            reservation_no,
            latency_str
        )