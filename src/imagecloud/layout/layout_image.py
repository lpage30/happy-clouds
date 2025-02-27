from PIL import Image
from itemcloud.layout.layout_item import LayoutItem
from itemcloud.containers.named_image import NamedImage
from itemcloud.util.parsers import to_unused_filepath
from itemcloud.box import Box
from itemcloud.size import Size


class LayoutImage(LayoutItem):

    def __init__(
        self,
        name: str,
        placement_box: Box,
        rotated_degrees: int | None,
        reservation_box: Box,        
        reservation_no: int,
        latency_str: str = ''
    ) -> None:
        super().__init__(
            name,
            placement_box,
            rotated_degrees,
            reservation_box,
            reservation_no,
            latency_str
        )
    
    @property
    def original_image(self) -> NamedImage:
        return self._original_image
    
    def get_item_as_named_image(self, rotated_degrees: int | None = None, size: Size | None = None, logger: BaseLogger | None = None) -> NamedImage:
        new_image = self.original_image.image
        if rotated_degrees is not None and 0 < rotated_degrees:
            if logger:
                logger.info('Rotating {0} {1} degrees'.format(self.original_image.name, rotated_degrees))
            # always rotate clockwise (negative degrees)
            new_image = new_image.rotate(-rotated_degrees, expand=1)
        
        if size is not None and new_image.size != size.image_tuple:
            if logger:
                logger.info('Resizing {0} ({1},{2}) -> {3}'.format(
                    self.original_image.name,
                    new_image.width, new_image.height,
                    size.size_to_string()
                ))
            new_image = new_image.resize(size.image_tuple)
        return NamedImage(new_image, self.original_image.name, self.original_image.image)

    def write_item(self, item_name: str, layout_directory: str) -> str:
        image_filepath = to_unused_filepath(layout_directory, item_name, 'png')
        self.original_image.image.save(image_filepath, 'png')
        return image_filepath

    def load_item(self, item_filepath: str) -> None:
        self._original_image = NamedImage.load(item_filepath)
        self._name = self.original_image.name

    def to_reserved_item(
        self, 
        placement_box: Box,
        rotated_degrees: int,
        reservation_box: Box,
        latency_str: str
    ) -> LayoutItem:
        item = LayoutImage(
            self.name,
            placement_box,
            rotated_degrees,
            reservation_box,
            self.reservation_no,
            latency_str
        )
        item._original_image = self._original_image
        return item

    @staticmethod
    def create_layout_image(
        name: str,
        placement_box: Box,
        rotated_degrees: int,
        reservation_box: Box,        
        reservation_no: int,
        latency_str: str
    ) -> LayoutItem:
        return LayoutImage(
            name,
            placement_box,
            rotated_degrees,
            reservation_box,
            reservation_no,
            latency_str
        )