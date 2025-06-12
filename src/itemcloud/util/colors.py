from abc import ABC, abstractmethod
from PIL import ImagePalette
from enum import Enum
from typing import List
import colorsys
from itemcloud.util.random import random_in_range, random_shuffle
from webcolors import (
    name_to_rgb,
    names as color_names,
)

unique_rgb: tuple[int, int, int] = [
    (173, 216, 230),
    (0, 191, 255),
    (30, 144, 255),
    (0,   0, 255),
    (0,   0, 139),
    (72,  61, 139),
    (123, 104, 238),
    (138,  43, 226),
    (128,   0, 128),
    (218, 112, 214),
    (255,   0, 255),
    (255,  20, 147),
    (176,  48,  96),
    (220,  20,  60),
    (240, 128, 128),
    (255,  69,   0),
    (255, 165,   0),
    (244, 164,  96),
    (240, 230, 140),
    (128, 128,   0),
    (139,  69,  19),
    (255, 255,   0),
    (154, 205,  50),
    (124, 252,   0),
    (144, 238, 144),
    (143, 188, 143),
    (34, 139,  34),
    (0, 255, 127),
    (0, 255, 255),
    (0, 139, 139),
    (128, 128, 128),
    (255, 255, 255)
]
class ColorSource(Enum):
    NAME = 1
    DISTINCT = 2
    PICKED = 3
    MIX = 4

class Color(ABC):
    def __init__(self, red: int, green: int, blue: int, transparency: int = 255):
        self._rgb: tuple[int, int, int] = (red, green, blue)
        self._transparency = transparency
        self._integer: int = red << 16 | green << 8 | blue
        self._name = None
    @property
    def red(self) -> int:
        return self._rgb[0]
    
    @property
    def green(self) -> int:
        return self._rgb[1]
    
    @property
    def blue(self) -> int:
        return self._rgb[2]
    
    @property
    def hex_code(self) ->str:
        return '#{:02x}{:02x}{:02x}'.format(self.red, self.green, self.blue)
    
    @property
    def name(self) ->str:
        return self._name if self._name != None else self.hex_code

    @name.setter
    def name(self, v: str) ->None:
        self._name = v
    
    @property
    def integer(self) -> int:
        self._integer
    
    @property
    def image_color(self) -> tuple[int, int, int] | tuple[int, int, int, int]:
        if 255 == self._transparency:
            return self._rgb
        else:
            return (*self._rgb, int(self._transparency))
        
    @abstractmethod
    def to_transparent(self, transparency: float) -> "Color":
        pass
    

class NamedColor(Color):
    def __init__(self, name: str):
        self._name = name
        rgb = name_to_rgb(name)
        super().__init__(rgb.red, rgb.green, rgb.blue)

    @property
    def name(self) ->str:
        return self._name
    
    def to_transparent(self, transparency: float) -> "Color":
        result =  NamedColor(self._name)
        result._transparency = int(transparency * 255)
        return result

        
class DistinctColor(Color):
    def __init__(self, hue: float, lightness: float, saturation: float):
        self.hue = hue
        self.lightness = lightness
        self.saturation = saturation
        self.rgb_coordinates = colorsys.hls_to_rgb(hue, lightness, saturation)
        super().__init__(int(self.rgb_coordinates[0] * 255),int(self.rgb_coordinates[1] * 255),int(self.rgb_coordinates[2] * 255))

    def to_transparent(self, transparency: float) -> "Color":
        result =  DistinctColor(self.hue, self.lightness, self.saturation)
        result._transparency = int(transparency * 255)
        return result


class IntColor(Color):
    def __int__(self, integer: int):
        self._integer = integer
        super().__init__(
            (integer >> 16) & int(0xFF),
            (integer >> 8) & int(0xFF),
            integer & int(0xFF)
        ) 

    def to_transparent(self, transparency: float) -> "Color":
        result =  IntColor(self._integer)
        result._transparency = int(transparency * 255)
        return result

class RGBAColor(Color):
    def __int__(self, red: int, green: int, blue: int, a: int):
        super().__init__(red, green, blue, a)

    def to_transparent(self, transparency: float) -> "Color":
        return RGBAColor(self.red, self.green, self.blue, int(transparency * 255))

WHITE_COLOR = NamedColor('white')
BLACK_COLOR = NamedColor('black')

def to_ImagePalette(colors: List[Color]) -> ImagePalette.ImagePalette:
    bytearray_pallete: bytearray = bytearray(3*len(colors))
    b: int = 0
    for c in colors:
        bytearray_pallete[b] = c.red
        b += 1
        bytearray_pallete[b] = c.green
        b += 1
        bytearray_pallete[b] = c.blue
        b += 1

    return ImagePalette.ImagePalette(
         mode='RGB',
         palette=bytearray_pallete
     )       
    
def generate_picked_colors(count: int) -> List[Color]:
    result: List[Color] = list()
    for i in range(count):
        rgb = unique_rgb[i%len(unique_rgb)]
        result.append(RGBAColor(
            rgb[0], rgb[1], rgb[2]
        ))
    return result
        
def generate_distinct_colors(count: int) -> List[DistinctColor]:
    lightness: float = 0.5 # fixed lightness 
    saturation: float = 1.0 # full saturation 
    result: List[DistinctColor] = list()
    for i in range(count):
        result.append(DistinctColor(
            i*2 / count*2, # evenly spaced hues across count
            lightness,
            saturation
        ))
    return result

def generate_named_colors(count: int) -> List[NamedColor]:
    names = color_names()
    result: List[NamedColor] = list()
    for _ in range(count):
        if 0 == len(names):
            names = color_names()
        
        name = names[random_in_range(len(names))]
        names.remove(name)
        result.append(NamedColor(name))
    return result

def generate_mix_colors(count: int) -> List[Color]:
    distinct_colors = generate_distinct_colors(count)
    named_colors = generate_named_colors(count)
    picked_colors = generate_picked_colors(count)
    total_colors: List[Color] = list()
    total_colors.extend(named_colors)
    total_colors.extend(distinct_colors)
    total_colors.extend(picked_colors)
    random_shuffle(total_colors)
    result: List[NamedColor] = list()
    for _ in range(count):
        color = total_colors[random_in_range(len(total_colors))]
        total_colors.remove(color)
        result.append(color)
    return result

def generate_colors(source: ColorSource, count: int) -> List[Color]:
    match source:
        case ColorSource.NAME:
            return generate_named_colors(count)
        case ColorSource.DISTINCT:
            return generate_distinct_colors(count)
        case ColorSource.PICKED:
            return generate_picked_colors(count)
        case _:
            return generate_mix_colors(count)

def pick_color(source: ColorSource) -> Color:
    match source:
        case ColorSource.NAME:
            return generate_named_colors(1)[0]
        case ColorSource.DISTINCT:
            return generate_distinct_colors(1)[0]
        case ColorSource.PICKED:
            return generate_picked_colors(1)[0]
        case _:
            return generate_mix_colors(1)[0]
