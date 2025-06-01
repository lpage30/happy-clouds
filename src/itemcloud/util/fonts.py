from PIL import ImageDraw, ImageFont
from typing import List
from itemcloud.image_item import ImageItem
from itemcloud.box import Box, RotateDirection
from itemcloud.size import Size
from itemcloud.util.random import random_in_range
from itemcloud.util.font_categories import FontUsageCategory, FontTypeCategories
from itemcloud.util.colors import Color
from itemcloud.logger.base_logger import BaseLogger

# https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html
ANCHOR = 'lt'
# font sizings taken from: https://www.learnui.design/blog/mobile-desktop-website-font-size-guidelines.html
class FontSize:
    def __init__(self, usage: FontUsageCategory, min: float, max: float) -> None:
        self.usage = usage
        self.min = min
        self.max = max
    @property
    def median_size(self) -> float:
        return self.min + (self.max - self.min) / 2


# font names taken from: https://www.manypixels.co/blog/brand-design/popular-fonts and matplotlib
# https://www.lifehack.org/428846/top-20-most-popular-fonts-of-all-time
class FontName:
    def __init__(self,name: str, categories: List[FontTypeCategories]) -> None:
        self.name = name
        self.categories = categories
    
    def is_valid(self) -> bool:
        try:
            ImageFont.truetype(self.name, 16)
            return True
        except:
            return False


class FontTextAttributes:
    def __init__(
        self,
        layout: ImageFont.Layout | None = None,
        stroke_width: int | None = None,
        anchor: str | None = None,
        align: str | None = None
    ) -> None:
        self.layout = layout.value if layout is not None else ImageFont.Layout.BASIC.value
        self.stroke_width = stroke_width if stroke_width is not None else 2
        self.anchor = anchor if anchor is not None else ANCHOR
        self.align = align if align is not None else 'center'


class Font:
    def __init__(self, font: FontName, size: FontSize, attributes: FontTextAttributes) -> None:
        self._font = font
        self._size = size
        self._attributes = attributes
        self._font_size = size.median_size

    @property
    def font_name(self) -> str:
        return self._font.name

    @property
    def min_font_size(self) -> float:
        return self._size.min

    @property
    def max_font_size(self) -> float:
        return self._size.max
    
    @property
    def layout(self) -> int:
        return self._attributes.layout

    @property
    def stroke_width(self) -> int | None:
        return self._attributes.stroke_width

    @property
    def anchor(self) -> str:
        return self._attributes.anchor
    
    @property
    def align(self) -> str:
        return self._attributes.align

    @property
    def font_size(self) -> float:
        return self._font_size
    
    @font_size.setter
    def font_size(self, v: float) -> None:
        self._font_size = v

    def to_image_font(
        self,
        text: str | None = None, 
        rotated_degrees: int | None = None,
        size: Size | None = None,
        logger: BaseLogger | None = None
    ) -> ImageFont.FreeTypeFont:
        f = self
        if text is not None and size is not None:
            fit_size = size
            # put rotated size back so we resize to horizontal size
            # we then rotate image later
            if rotated_degrees is not None and 0 < rotated_degrees:
                fit_size = Box(0, 0, size.width, size.height).rotate(rotated_degrees, RotateDirection.COUNTERCLOCKWISE).size

            if logger:
                logger.info('Best-fit Font Resizing {0} -> {1}'.format(
                    self.to_box(text).size.size_to_string(),
                    fit_size.size_to_string()
                ))
            f = self.find_best_fit(text, fit_size)
        return ImageFont.truetype(f.font_name, f.font_size)
    
    def to_box(self, text: str) -> Box:
        return get_text_box(text, self.to_image_font(), self._attributes)

    def find_best_fit(self, text: str, fit_size: Size) -> "Font":
        result: Font = Font(
            self._font,
            self._size,
            self._attributes
        )
        result.font_size = self.font_size
        font_size = result.font_size
        box_size = result.to_box(text).size
        fit_area = fit_size.area
        box_area = box_size.area
        increment = 0.25 if box_area < fit_area else -0.25
        while True:
            result.font_size = font_size + increment
            box_size = result.to_box(text).size
            box_area = box_size.area
            if (0 < increment and 
                box_area < fit_area and 
                box_size.width < fit_size.width and 
                box_size.height < fit_size.height) or (
                    increment < 0 and 
                    fit_area < box_area and
                    fit_size.width < box_size.width and
                    fit_size.height < box_size.height):
                font_size = result.font_size
            else:
                result.font_size = font_size
                return result
        
    
    def draw_with_font_on_image(
        self,
        text: str,
        font: ImageFont.FreeTypeFont,
        image: ImageItem,
        fg_color: Color | None,
        as_watermark: bool = False,
        xy: tuple[float, float] | None = None
    ) -> ImageItem:
        text_image = image
        text_rotation = 0
        if xy is None:
            xy = (0.0, 0.0)
        if as_watermark:
            box = get_text_box(text, font, self._attributes)
            text_rotation = box.rotate_until_wedged(Box(0,0, image.width, image.height))
            text_image = ImageItem.new('RGBA', box.size.image_tuple, (255,255,255,0))

        draw = text_image.create_draw()
        if fg_color is not None:
            if '\n' in text:
                draw.multiline_text(
                    xy,
                    text, 
                    fill=fg_color.image_color, 
                    font=font, 
                    anchor=self._attributes.anchor,
                    align = self._attributes.align,
                    stroke_width=self._attributes.stroke_width,
                    font_size=self.font_size
                )
            else:
                draw.text(
                    xy,
                    text,
                    fill=fg_color.image_color,
                    font=font,
                    anchor=self._attributes.anchor,
                    align = self._attributes.align,
                    stroke_width=self._attributes.stroke_width,
                    font_size=self.font_size
                )
        else:
            if '\n' in self.text:
                draw.multiline_text(
                    xy,
                    text,
                    font=font,
                    anchor=self._attributes.anchor,
                    align = self._attributes.align,
                    stroke_width=self._attributes.stroke_width,
                    font_size=self.font_size
                )
            else:
                draw.text(
                    xy,
                    text,
                    font=font,
                    anchor=self._attributes.anchor,
                    align = self._attributes.align,
                    stroke_width=self._attributes.stroke_width,
                    font_size=self.font_size

                )
        if as_watermark:
            image = image.convert('RGBA')
            if 0 < text_rotation:
                text_image = text_image.rotate(-text_rotation, expand=1)
            text_image = text_image.resize(image.size)
            return ImageItem.alpha_composite(image, text_image)
        
        return image

    def draw_on_image(
        self,
        text: str, 
        image: ImageItem,
        fg_color: Color | None, 
        rotated_degrees: int | None = None,
        size: Size | None = None,
        logger: BaseLogger | None = None,
        as_watermark: bool = False,
        xy: tuple[float, float] | None = None
    ) -> ImageItem:

        font = self.to_image_font(
            text,
            rotated_degrees,
            size,
            logger
        )
        return self.draw_with_font_on_image(
            text,
            font,
            image,
            fg_color,
            as_watermark,
            xy
        )

    def to_image(
        self, 
        text: str, 
        fg_color: Color | None, 
        bg_color: Color | None,
        rotated_degrees: int | None = None,
        size: Size | None = None,
        logger: BaseLogger | None = None,
        as_watermark: bool = False,
        xy: tuple[float, float] | None = None,
    )-> ImageItem:

        font = self.to_image_font(
            text,
            rotated_degrees,
            size,
            logger
        )

        box_size = get_text_box(text, font, self._attributes).size

        if not(as_watermark) and bg_color is not None:
            result = ImageItem.new("RGB", (box_size.width, box_size.height), bg_color.image_color)
        else:
            result = ImageItem.new("RGBA", (box_size.width, box_size.height))

        result = self.draw_with_font_on_image(
            text,
            font,
            result,
            fg_color,
            as_watermark,
            xy
        )
        
        if rotated_degrees is not None and 0 < rotated_degrees:
            if logger:
                logger.info('Rotating {1} degrees'.format(rotated_degrees))
            # always rotate clockwise (negative degrees)
            result = result.rotate(-rotated_degrees, expand=1)
                
        if size is not None and result.size != size.image_tuple:
            if logger:
                logger.info('Text Image Resizing ({0},{1}) -> {2}'.format(
                    result.width, result.height,
                    size.size_to_string()
                ))
            result = result.resize(size.image_tuple)

        return result

def get_font_sizes() -> List[FontSize]:
    return [
        FontSize(FontUsageCategory.MOBILE_INTERACTION_HEAVY, 16, 18),
        FontSize(FontUsageCategory.MOBILE_TEXT_HEAVY, 16, 20),
        FontSize(FontUsageCategory.DESKTOP_INTERACTION_HEAVY, 14, 20),
        FontSize(FontUsageCategory.DESKTOP_TEXT_HEAVY, 18, 24),
        FontSize(FontUsageCategory.SECONDARY_MOBILE_INTERACTION_HEAVY, 14, 16),
        FontSize(FontUsageCategory.SECONDARY_MOBILE_TEXT_HEAVY, 14, 18),
        FontSize(FontUsageCategory.SECONDARY_DESKTOP_INTERACTION_HEAVY, 12, 18),
        FontSize(FontUsageCategory.SECONDARY_DESKTOP_TEXT_HEAVY, 16, 22),
    ]

def get_font_names() -> List[FontName]:

    return list(filter(lambda f: f.is_valid(), [
        FontName('Airstream NF', [FontTypeCategories.MODERN, FontTypeCategories.SCRIPT]),
        FontName('Andale Mono', [FontTypeCategories.CLEAN]),
        FontName('Apple Chancery', []),
        FontName('AppleGothic', []),
        FontName('AppleMyungjo', []),
        FontName('Arial', [FontTypeCategories.MODERN, FontTypeCategories.CLEAN]),
        FontName('Arial Black', [FontTypeCategories.MODERN, FontTypeCategories.CLEAN]),
        FontName('Arial Narrow', [FontTypeCategories.MODERN, FontTypeCategories.CLEAN]),
        FontName('Athelas', []),
        FontName('Avenir', [FontTypeCategories.MODERN]),
        FontName('Avenir Next', [FontTypeCategories.MODERN]),
        FontName('Avenir Next Condensed', [FontTypeCategories.MODERN]),
        FontName('Ayuthaya', []),
        FontName('Bangla MN', []),
        FontName('Bangla Sangam MN', []),
        FontName('Baskerville', [FontTypeCategories.CLASSIC, FontTypeCategories.CLEAN]),
        FontName('Bodoni 72',[FontTypeCategories.CLASSIC, FontTypeCategories.CLEAN]),
        FontName('Chalkboard', [FontTypeCategories.MODERN]),
        FontName('Chalkduster', [FontTypeCategories.MODERN]),
        FontName('Changa One', []),
        FontName('Charter', []),
        FontName('Cochin', []),
        FontName('Comic Sans MS', [FontTypeCategories.MODERN]),
        FontName('Convergence', []),
        FontName('Copperplate', [FontTypeCategories.CLASSIC, FontTypeCategories.CLEAN]),
        FontName('Courgette', []),
        FontName('Courier', [FontTypeCategories.CLEAN]),
        FontName('Courier New', [FontTypeCategories.CLEAN]),
        FontName('D-DIN', []),
        FontName('Devanagari Sangam MN', []),
        FontName('Didot', [FontTypeCategories.CLASSIC]),
        FontName('Fenix', []),
        FontName('Futura', [FontTypeCategories.MODERN, FontTypeCategories.CLEAN]),
        FontName('Galvji', []),
        FontName('Geneva', []),
        FontName('Georgia', [FontTypeCategories.CLASSIC]),
        FontName('Gochi Hand', []),
        FontName('Gujarati Sangam MN', []),
        FontName('Gurmukhi MN', []),
        FontName('Gurmukhi Sangam MN', []),
        FontName('Helvetica', [FontTypeCategories.CLEAN]),
        FontName('Herculanum', []),
        FontName('Hiragino Sans GB', []),
        FontName('Hoefler Text', []),
        FontName('Impact', []),
        FontName('Iowan Old Style', []),
        FontName('Jua', []),
        FontName('Kannada MN', []),
        FontName('Kannada Sangam MN', []),
        FontName('Kefa', []),
        FontName('Krungthep', []),
        FontName('Lao MN', []),
        FontName('Lao Sangam MN', []),
        FontName('Lemon', []),
        FontName('Luminari', []),
        FontName('Malayalam MN', []),
        FontName('Malayalam Sangam MN', []),
        FontName('Marion', []),
        FontName('Menlo', []),
        FontName('Microsoft Sans Serif', [FontTypeCategories.MODERN, FontTypeCategories.CLEAN]),
        FontName('Mogra', []),
        FontName('Monaco', []),
        FontName('Noteworthy', []),
        FontName('Optima', []),
        FontName('Oriya MN', []),
        FontName('Oriya Sangam MN', []),
        FontName('Palatino', []),
        FontName('Papyrus', [FontTypeCategories.MODERN]),
        FontName('Phosphate', []),
        FontName('Prociono', []),
        FontName('Raleway', []),
        FontName('Rockwell', [FontTypeCategories.CLASSIC]),
        FontName('Sathu', []),
        FontName('Savoye LET', []),
        FontName('Seravek', []),
        FontName('SignPainter', []),
        FontName('Silom', []),
        FontName('Sinhala MN', []),
        FontName('Sinhala Sangam MN', []),
        FontName('Skia', []),
        FontName('Tahoma', [FontTypeCategories.MODERN]),
        FontName('Tamil MN', []),
        FontName('Tamil Sangam MN', []),
        FontName('Tauri', []),
        FontName('Telugu MN', []),
        FontName('Telugu Sangam MN', []),
        FontName('Thonburi', []),
        FontName('Times', [FontTypeCategories.CLASSIC]),
        FontName('Times New Roman', [FontTypeCategories.CLASSIC]),
        FontName('Trattatello', []),
        FontName('Trebuchet MS', []),
        FontName('Verdana', [FontTypeCategories.MODERN, FontTypeCategories.CLEAN]),
        FontName('Zapfino', [])
    ]))

def get_text_box(text: str, font: ImageFont.FreeTypeFont, attributes: FontTextAttributes) -> Box:
    text_bbox = font.getbbox(text, stroke_width=attributes.stroke_width, anchor=attributes.anchor)
    horizontal_offset = 0
    vertical_offset = 0
    if int(text_bbox[0]) < 0:
        horizontal_offset = max(abs(int(text_bbox[0])), horizontal_offset)
    if int(text_bbox[1]) < 0:
        vertical_offset = max(abs(int(text_bbox[1])), vertical_offset)
    return Box(int(text_bbox[0]) + horizontal_offset, int(text_bbox[1]) + vertical_offset, int(text_bbox[2]) + horizontal_offset, int(text_bbox[3]) + vertical_offset)

def generate_fonts(count: int) -> List[FontName]:
    names = get_font_names()
    result: List[FontName] = list()
    for _ in range(count):
        result.append(names[random_in_range(len(names))])
    return result

def generate_font_sizes(count: int) -> List[FontSize]:
    sizes = get_font_sizes()
    result: List[FontSize] = list()
    for _ in range(count):
        result.append(sizes[random_in_range(len(sizes))])
    return result

def pick_font() -> FontName:
    return generate_fonts(1)[0]

def pick_font_size() -> FontSize:
    return generate_font_sizes(1)[0]
