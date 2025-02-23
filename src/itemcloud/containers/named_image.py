import os
from PIL import Image
from itemcloud.size import Size
from itemcloud.containers.named_item import NamedItem

class NamedImage(NamedItem):
    
    def __init__(self, image: Image.Image, name: str | None = None, original_image: Image.Image | None = None) -> None:
        NamedItem.__init__(self, name, image.width, image.height)
        self._original_image = original_image if original_image is not None else image
        self._image = image
    
    @property
    def image(self) -> Image.Image:
        return self._image
        
    @property
    def original_named_image(self):
        return NamedImage(self._original_image, self.name)
    
    def show(self) -> None:
        self.image.show(self.name)

    @staticmethod
    def load(image_filepath: str):
        name = os.path.splitext(os.path.basename(image_filepath))[0]
        image = Image.open(image_filepath)
        return NamedImage(image, name)
