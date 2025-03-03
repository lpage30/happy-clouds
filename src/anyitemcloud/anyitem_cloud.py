from PIL import Image
from itemcloud.item_cloud import ItemCloud 
from itemcloud.logger.base_logger import BaseLogger
from itemcloud.size import (Size, ResizeType)
from itemcloud.layout.layout import Layout

class AnyItemCloud(ItemCloud):

    def __init__(self,
                 logger: BaseLogger,
                 mask: Image.Image | None = None,
                 size: Size | None = None,
                 background_color: str | None = None,
                 max_items: int | None = None,
                 max_item_size: Size | None = None,
                 min_item_size: Size | None = None,
                 item_step: int | None = None,
                 item_rotation_increment: int | None = None,
                 resize_type: ResizeType | None = None,
                 scale: float | None = None,
                 contour_width: float | None = None,
                 contour_color: str | None = None,
                 margin: int | None = None,
                 mode: str | None = None,
                 name: str | None = None,
                 total_threads: int | None = None,
    ) -> None:
        super().__init__(
            logger,
            mask,
            size,
            background_color,
            max_items,
            max_item_size,
            min_item_size,
            item_step,
            item_rotation_increment,
            resize_type,
            scale,
            contour_width,
            contour_color,
            margin,
            mode,
            name if name is not None else 'textimagecloud',
            total_threads
        )

    @staticmethod
    def create(
        layout: Layout,
        logger: BaseLogger
    ):
        result = AnyCloud(
            logger,
            layout.contour.mask,
            layout.canvas.size,
            layout.canvas.background_color,
            layout.max_items,
            None,
            layout.min_item_size,
            layout.item_step,
            layout.item_rotation_increment,
            layout.resize_type,
            layout.scale,
            layout.contour.width,
            layout.contour.color,
            layout.margin,
            layout.canvas.mode,
            layout.canvas.name
        )
        result.layout_ = layout
        return result
    
