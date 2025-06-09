from itemcloud.layout.base.layout_item import LayoutItem
from itemcloud.containers.named_text import NamedText
from itemcloud.box import Box

class LayoutText(LayoutItem):

    def __init__(
        self,
        name: str,
        placement_box: Box,
        rotated_degrees: int | None,
        reservation_box: Box,        
        reservation_no: int,
        latency_str: str,
        text: NamedText
    ) -> None:
        super().__init__(
            name,
            placement_box,
            rotated_degrees,
            reservation_box,
            reservation_no,
            latency_str,
            text
        )    
