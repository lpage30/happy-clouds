from PIL import Image, ImageDraw, ImageFont
from typing import List
from itemcloud.box import Box
from itemcloud.size import Size
from itemcloud.util.random import random_in_range
from textcloud.util.font_categories import FontUsageCategory, FontTypeCategories
from itemcloud.util.colors import Color

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

class Font:
    def __init__(self, font: FontName, size: FontSize) -> None:
        self._font = font
        self._size = size
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
    def font_size(self) -> float:
        return self._font_size
    
    @font_size.setter
    def font_size(self, v: float) -> None:
        self._font_size = v

    def to_image_font(self) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(self.font_name, self.font_size)
    
    def to_box(self, text: str) -> Box:
        return get_text_box(text, self.to_image_font())

    def find_best_fit(self, text: str, fit_size: Size) -> "Font":
        result: Font = Font(
            self._font,
            self._size,
        )
        result.font_size = self.font_size
        font_size = result.font_size
        box_size = result.to_box(text).size
        increment = 1 if box_size.is_less_than(fit_size) else -1
        while True:
            result.font_size = font_size + increment
            box_size = result.to_box(text).size
            if (0 < increment and box_size.is_less_than(fit_size)) or (increment < 0 and fit_size.is_less_than(box_size)):
                font_size = result.font_size
            else:
                result.font_size = font_size
                return result

    def to_image(self, 
                 text: str, 
                 fg_color: Color | None, 
                 bg_color: Color | None
    ) -> Image.Image:
        font = self.to_image_font()
        box_size = get_text_box(text, font).size

        if bg_color is not None:
            result = Image.new("RGB", (box_size.width, box_size.height), bg_color.image_color)
        else:
            result = Image.new("RGBA", (box_size.width, box_size.height))

        draw = ImageDraw.Draw(result)

        if fg_color is not None:
            if '\n' in text:
                draw.multiline_text((0, 0), text, fill=fg_color.image_color, font=font, anchor="lt")
            else:
                draw.text((0, 0), text, fill=fg_color.image_color, font=font, anchor="lt")
        else:
            if '\n' in self.text:
                draw.multiline_text((0, 0), text, font=font, anchor="lt")
            else:
                draw.text((0, 0), text, font=font, anchor="lt")

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
        FontName('Al Nile', [FontTypeCategories.CLEAN]),
        FontName('Al Tarikh', [FontTypeCategories.CLEAN]),
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
        FontName('Baghdad', []),
        FontName('Bangla MN', []),
        FontName('Bangla Sangam MN', []),
        FontName('Baskerville', [FontTypeCategories.CLASSIC, FontTypeCategories.CLEAN]),
        FontName('Beirut', []),
        FontName('Bodoni 72',[FontTypeCategories.CLASSIC, FontTypeCategories.CLEAN]),
        FontName('Bodoni Ornaments',[FontTypeCategories.CLASSIC, FontTypeCategories.CLEAN]),
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
        FontName('Farah', []),
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
        FontName('Kailasa', []),
        FontName('Kannada MN', []),
        FontName('Kannada Sangam MN', []),
        FontName('Kefa', []),
        FontName('Kokonor', []),
        FontName('Krungthep', []),
        FontName('KufiStandardGK', []),
        FontName('Lao MN', []),
        FontName('Lao Sangam MN', []),
        FontName('Lemon', []),
        FontName('Luminari', []),
        FontName('Malayalam MN', []),
        FontName('Malayalam Sangam MN', []),
        FontName('Marion', []),
        FontName('Menlo', []),
        FontName('Microsoft Sans Serif', [FontTypeCategories.MODERN, FontTypeCategories.CLEAN]),
        FontName('Mishafi', []),
        FontName('Mishafi Gold', []),
        FontName('Mogra', []),
        FontName('Monaco', []),
        FontName('Mshtakan', []),
        FontName('Muna', []),
        FontName('Nadeem', []),
        FontName('Noteworthy', []),
        FontName('Optima', []),
        FontName('Oriya MN', []),
        FontName('Oriya Sangam MN', []),
        FontName('Palatino', []),
        FontName('Papyrus', [FontTypeCategories.MODERN]),
        FontName('Phosphate', []),
        FontName('Prociono', []),
        FontName('Raanana', []),
        FontName('Raleway', []),
        FontName('Rockwell', [FontTypeCategories.CLASSIC]),
        FontName('Sana', []),
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
        FontName('Waseem', []),
        FontName('Zapfino', [])
    ]))

def get_text_box(text: str, font: ImageFont.FreeTypeFont) -> Box:
    text_bbox = font.getbbox(text)
    return Box(int(text_bbox[0]), int(text_bbox[1]), int(text_bbox[2]), int(text_bbox[3]))

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

