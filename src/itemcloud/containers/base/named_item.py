from abc import abstractmethod
from PIL import Image
from itemcloud.size import Size
from itemcloud.logger.base_logger import BaseLogger

class NamedItem(Size):
    
    def __init__(self, name: str, width: int, height: int) -> None:
        Size.__init__(self, width, height)
        self._name = name if name is not None else ''
    
    @property
    def name(self) -> str:
        return self._name
    
    @abstractmethod
    def to_image(
        self,
        rotated_degrees: int | None = None,
        size: Size | None = None,
        logger: BaseLogger | None = None,
        as_watermark: bool = False
    ) -> Image.Image:
        pass

    @abstractmethod
    def write_item(self, item_name: str, layout_directory: str) -> str:
        pass


    
