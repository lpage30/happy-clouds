from PIL import Image
from itemcloud.item_cloud import ItemCloud 
from itemcloud.logger.base_logger import BaseLogger
from itemcloud.size import (Size, ResizeType)
from itemcloud.layout.layout import Layout

class ImageCloud(ItemCloud):

    def __init__(self,
                 logger: BaseLogger,
                 mask: Image.Image | None = None,
                 size: Size | None = None,
                 background_color: str | None = None,
                 max_images: int | None = None,
                 max_image_size: Size | None = None,
                 min_image_size: Size | None = None,
                 image_step: int | None = None,
                 image_rotation_increment: int | None = None,
                 resize_type: ResizeType | None = None,
                 scale: float | None = None,
                 contour_width: float | None = None,
                 contour_color: str | None = None,
                 margin: int | None = None,
                 mode: str | None = None,
                 name: str | None = None,
                 total_threads: int | None = None
    ) -> None:
        super().__init__(
            logger,
            mask,
            size,
            background_color,
            max_images,
            max_image_size,
            min_image_size,
            image_step,
            image_rotation_increment,
            resize_type,
            scale,
            contour_width,
            contour_color,
            margin,
            mode,
            name if name is not None else 'imagecloud',
            total_threads
        )

    @staticmethod
    def create(
        layout: Layout,
        logger: BaseLogger
    ):
        result = ImageCloud(
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
    
