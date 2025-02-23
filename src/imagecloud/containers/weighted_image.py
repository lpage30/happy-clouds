import csv
from PIL import Image
from itemcloud.containers.weighted_item import WeightedItem
from itemcloud.containers.named_image import NamedImage
from itemcloud.layout.layout_item import LayoutItem
from itemcloud.box import Box
from imagecloud.layout.layout_image import LayoutImage

class WeightedImage(WeightedItem, NamedImage):
    
    def __init__(self, weight: float, image: Image.Image, name: str | None = None, original_image: Image.Image | None = None) -> None:
        WeightedItem.__init__(self, weight, name, image.width, image.height)
        NamedImage.__init__(self, image, name, original_image)

    def to_layout_item(
        self,
        placement_box: Box,
        rotated_degrees: int,
        reservation_box: Box,        
        reservation_no: int,
        latency_str: str
    ) -> LayoutItem:
        item =  LayoutImage(
            self.name,
            placement_box,
            rotated_degrees,
            reservation_box,
            reservation_no,
            latency_str
        )
        item._original_image = self._original_image
        return item
        
    
    def to_fitted_weighted_item(self, weight: float, width: int, height: int) -> "WeightedItem":
        image = self.original_named_image.image.resize((width, height))
        return WeightedImage(weight, image, self.name, self.original_named_image)

    @staticmethod
    def load(weight: float, image_filepath: str):
        named_image = NamedImage.load(image_filepath)
        return WeightedImage(weight, named_image.image, named_image.name)
        
        

WEIGHTED_IMAGE_WEIGHT = 'weight'
WEIGHTED_IMAGE_IMAGE_FILEPATH = 'image_filepath'
WEIGHTED_IMAGES_CSV_FILE_HELP = '''csv file for weighted images with following format:
"{0}","{1}"
"<full-path-to-image-file-1>",<weight-as-number-1>
...
"<full-path-to-image-file-N>",<weight-as-number-N>

'''.format(WEIGHTED_IMAGE_IMAGE_FILEPATH, WEIGHTED_IMAGE_WEIGHT)

def load_weighted_images(csv_filepath: str) -> list[WeightedImage]:
    try:
        result: list[WeightedImage] = list()
        with open(csv_filepath, 'r') as file:    
            csv_reader = csv.DictReader(file, fieldnames=[WEIGHTED_IMAGE_IMAGE_FILEPATH, WEIGHTED_IMAGE_WEIGHT])
            next(csv_reader)
            for row in csv_reader:
                result.append(WeightedImage.load(float(row[WEIGHTED_IMAGE_WEIGHT]), row[WEIGHTED_IMAGE_IMAGE_FILEPATH]))
        return result
    except Exception as e:
        raise Exception(str(e))
