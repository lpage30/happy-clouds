
from itemcloud.box import Box
from itemcloud.layout.base.layout_item import LayoutItem
from itemcloud.layout.layout_image import LayoutImage
from itemcloud.layout.layout_text import LayoutText
from itemcloud.layout.layout_textimage import LayoutTextImage


def create_layout_mix(
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
