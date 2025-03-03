
from itemcloud.box import Box
from itemcloud.layout.layout_item import LayoutItem
from imagecloud.layout.layout_image import LayoutImage
from textcloud.layout.layout_text import LayoutText
from textimagecloud.layout.layout_textimage import LayoutTextImage


def create_layout_item(
    name: str,
    placement_box: Box,
    rotated_degrees: int,
    reservation_box: Box,        
    reservation_no: int,
    latency_str: str,
    subclass_type_name: str
) -> LayoutItem:
    if LayoutImage.__name__ == subclass_type_name:
        return LayoutImage(
            name,
            placement_box,
            rotated_degrees,
            reservation_box,
            reservation_no,
            latency_str
        )
    if LayoutText.__name__ == subclass_type_name:
        return LayoutText(
            name,
            placement_box,
            rotated_degrees,
            reservation_box,
            reservation_no,
            latency_str
        )
    if LayoutTextImage.__name__ == subclass_type_name:
        return LayoutTextImage(
            name,
            placement_box,
            rotated_degrees,
            reservation_box,
            reservation_no,
            latency_str
        )
    raise ValueError('Unsupported LayoutItem subclass {0}'.format(subclass_type_name))
