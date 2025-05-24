import csv
from PIL import Image
from typing import (Dict, Any)
from itemcloud.util.parsers import (
    to_unused_filepath,
    validate_row,
    get_value_or_default
)
from itemcloud.containers.base.named_item import NamedItem
from itemcloud.containers.named_text import NamedText
from itemcloud.containers.named_image import (
    NamedImage,
    IMAGE_FILEPATH
)
from itemcloud.util.colors import RGBAColor
from itemcloud.size import Size
from itemcloud.logger.base_logger import BaseLogger

class NamedTextImage(NamedItem):
    def __init__(
        self, 
        name: str,
        text: NamedText,
        image: NamedImage,
        watermark_transparency: float = 1.0,
    ) -> None:
        super().__init__(name, 0,0)
        self._text = text
        self._watermark_transparency = watermark_transparency
        if self._text.foreground_color:
            self._text.foreground_color = self._text.foreground_color.to_transparent(watermark_transparency)
        else:
            self._text.foreground_color = RGBAColor(255,255,255, watermark_transparency * 255)
        self._text.background_color = None
        self._image = image
        self.width = image.width
        self.height = image.height
        if self.width < text.width:
            self.width = text.width
        if self.height < text.height:
            self.height = text.height

    def copy_named_textimage(self) -> "NamedTextImage":
        return NamedTextImage(
            self.name,
            self._text.copy_named_text(),
            self._image.copy_named_image(),
            self._watermark_transparency
        )

    def to_image(
        self,
        rotated_degrees: int | None = None,
        size: Size | None = None,
        logger: BaseLogger | None = None
    ) -> Image.Image:
        image = self._image.to_image(
            rotated_degrees,
            size,
            logger
        )
        return self._text.draw_on_image(
            image,
            rotated_degrees,
            size,
            logger,
            True
        )
    
    def resize(self, size: Size) -> "NamedTextImage":
        return  NamedTextImage(
                self.name,
                self._text.resize(size), 
                NamedImage(
                    self._image.image.resize((size.width, size.height)),
                    self.name,
                    self._image.image
                ),
                self._watermark_transparency
            )

    def write_item(self, item_name: str, layout_directory: str) -> str:
        image_filepath = self._image.write_item(item_name, layout_directory)
        row = self._text.to_csv_row()
        row[IMAGE_FILEPATH] = image_filepath
        row[TEXT_TRANSPARENCY_PERCENT] = self._watermark_transparency
        csv_filepath = to_unused_filepath(layout_directory, item_name, 'csv')
        with open(csv_filepath, 'w') as file:
            csv_writer = csv.DictWriter(file, fieldnames=list(row.keys()))
            csv_writer.writeheader()
            csv_writer.writerow(row)
        return csv_filepath

    @staticmethod
    def load_item(item_filepath: str) -> "NamedTextImage":
        with open(item_filepath, 'r', encoding='utf-8-sig') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                return NamedTextImage.load(row)


    @staticmethod
    def load(row: Dict[str, Any]) -> "NamedTextImage":
        validate_row(row, [IMAGE_FILEPATH])
        image = NamedImage.load_item(row[IMAGE_FILEPATH])
        text = NamedText.load(row)

        return NamedTextImage(
            image.name,
            text,
            image,
            get_value_or_default(TEXT_TRANSPARENCY_PERCENT, row, 1.0, float)
        )

TEXT_TRANSPARENCY_PERCENT = 'transparency_percent'