import csv
from typing import Dict, Any
from itemcloud.image_item import ImageItem
from itemcloud.containers.base.named_item import NamedItem
from itemcloud.util.parsers import (
    to_unused_filepath,
    validate_row,
)
from itemcloud.size import Size
from itemcloud.logger.base_logger import BaseLogger
from itemcloud.text_item import (TextItem, TEXT_TEXT, TEXT_ITEM_HEADERS)


class NamedText(NamedItem):

    def __init__(
        self,
        text: TextItem,
        name: str
    ) -> None:
        super().__init__(name, 0,0)
        self.text = text

    def copy_named_text(self) -> "NamedText":
        return NamedText(
            self.name,
            self.text
        )

    def resize(self, size: Size) -> "NamedText":
        if self.is_equal(size):
            return self
        result = NamedText(
            self.name,
            self.text.resize(size)
        )
        return result    

    def draw_on_image(
        self,
        image: ImageItem,
        rotated_degrees: int | None = None,
        size: Size | None = None,
        logger: BaseLogger | None = None,
        as_watermark: bool = False,
        xy: tuple[float, float] | None = None,
    ) -> ImageItem:
        return self.text.draw_on_image(
            image,
            rotated_degrees,
            size,
            logger,
            as_watermark,
            xy
        )

    def to_image(
        self,
        rotated_degrees: int | None = None,
        size: Size | None = None,
        logger: BaseLogger | None = None,
        as_watermark: bool = False
    ) -> ImageItem:
        return self.text.to_image(
            rotated_degrees,
            size,
            logger,
            as_watermark
        )
    
    def to_csv_row(self) -> Dict[str, Any]:
        return {
            TEXT_NAME: self.name,
        }.update(self.text.to_csv_row())

    def write_row(self, item_name: str, layout_directory: str, row: Dict[str, Any]) -> str:
        csv_filepath = to_unused_filepath(layout_directory, item_name, 'csv')
        with open(csv_filepath, 'w') as file:
            csv_writer = csv.DictWriter(file, fieldnames=list(row.keys()))
            csv_writer.writeheader()
            csv_writer.writerow(row)
        return csv_filepath        

    def write_item(self, item_name: str, layout_directory: str) -> str:
        return self.write_row(item_name, layout_directory, self.to_csv_row())

    @staticmethod
    def load_item(item_filepath: str) -> "NamedText":
        with open(item_filepath, 'r', encoding='utf-8-sig') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                return NamedText.load(row)

    @staticmethod
    def load(row: Dict[str, Any]) -> "NamedText":
        validate_row(row, [TEXT_NAME, TEXT_TEXT])
        return NamedText(
            row[TEXT_NAME],
            TextItem.load(row)
        )


TEXT_NAME = 'name'

TEXT_HEADERS = [
    TEXT_NAME,
    *TEXT_ITEM_HEADERS
]