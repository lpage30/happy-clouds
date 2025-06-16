from typing import List

from itemcloud.box import Box
from itemcloud.containers.base.image_item import ImageItem, to_img_size
from itemcloud.util.colors import BLACK_COLOR, WHITE_COLOR
from itemcloud.logger.base_logger import BaseLogger, LoggerLevel
from itemcloud.size import Size
from itemcloud.util.fonts import (
    Font,
    FontSize,
    FontTextAttributes,
    FontUsageCategory,
    get_font_names,
)
def show_all_fonts() -> None:
    logger = BaseLogger('ShowAllFonts', LoggerLevel.DEBUG)
    fs = FontSize(FontUsageCategory.MOBILE_TEXT_HEAVY, 32, 32)
    fa = FontTextAttributes()
    images: List[ImageItem] = list()
    max_size: Size = Size(0,0)
    margin = 3
    fontNames = get_font_names()
    total_fonts = len(fontNames)
    logger.info('Loading {0} fonts..'.format(total_fonts))
    for index in range(total_fonts):
        f = fontNames[index]
        i = Font(f,fs, fa).to_image(
            f.name,
            BLACK_COLOR,
            WHITE_COLOR,
            0,
            Size(1500,500)
        )
        max_size.width = i.width if i.width > max_size.width else max_size.width
        max_size.height += i.height + margin
        images.append(i)
        if 0 == (index+1) % 10:
            logger.debug("{0}/{1} fonts loaded...".format(index+1, total_fonts))

    logger.info('Rendering {0} fonts in 1 {1} x {2} image'.format(total_fonts, max_size.width, max_size.height))
    image = ImageItem.new(
        'RGBA', 
        to_img_size(max_size),
        WHITE_COLOR.name
    )
    height = 0
    for i in images:
        image.paste(
            im=i,
            box=(0, height, max_size.width, height + i.height)
        )
        height += i.height + margin
    image.show()

if __name__ == '__main__':
    show_all_fonts()