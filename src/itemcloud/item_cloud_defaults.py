
from itemcloud.size import ResizeType
from itemcloud.util.search import SEARCH_PATTERNS
DEFAULT_CLOUD_SIZE = '400,200'
DEFAULT_STEP_SIZE = '1'
DEFAULT_ROTATION_INCREMENT = '90'
DEFAULT_MAX_ITEM_SIZE = None
DEFAULT_MIN_ITEM_SIZE = '4,4'
DEFAULT_BACKGROUND_COLOR = None
DEFAULT_CONTOUR_WIDTH = '0'
DEFAULT_CONTOUR_COLOR = 'black'
DEFAULT_MARGIN = '1'
DEFAULT_MODE = 'RGBA'
DEFAULT_MAX_ITEMS = '200'
DEFAULT_RESIZE_TYPE = 'MAINTAIN_ASPECT_RATIO'
DEFAULT_SCALE = '1.0'
DEFAULT_TOTAL_THREADS = '1'
DEFAULT_SEARCH_PATTERN = 'NONE'

SEARCH_PATTERN_HELP = '''Search for openings using a pattern: https://i.ytimg.com/vi/8rXv-0gg-ZY/maxresdefault.jpg
{0}'''.format('|'.join(SEARCH_PATTERNS))
MAX_ITEM_SIZE_HELP = '''Maximum item size for the largest item.
If None, height of the item is used.
'''

    
MASK_HELP = '''Image file
If not None, gives a binary mask on where to draw words.
If mask is not None, width and height will be ignored
and the shape of mask will be used instead. 
All white (#FF or #FFFFFF) entries will be considered "masked out"
while other entries will be free to draw on.\
'''

CLOUD_SIZE_HELP = 'width and height of canvas'

RESIZE_TYPE_HELP = 'Image resizing can be done by maintaining aspect ratio ({0}), step/width percent change evenly applied ({1}), or simply step change ({2})'.format(ResizeType.MAINTAIN_ASPECT_RATIO.name, ResizeType.MAINTAIN_PERCENTAGE_CHANGE.name, ResizeType.NO_RESIZE_TYPE.name)
STEP_SIZE_HELP = '''Step size for the item. 
step > 1 might speed up computation
but give a worse fit.
'''
ROTATION_INCREMENT_HELP = '''Degrees rotation increment for fitting the item in cloud. 
small rotation_increments may result in longer runtimes to fit item.
Images are 1st rotated, until the sum rotation is 360, and then shrunk and rotated again.
'''

MAX_ITEM_SIZE_HELP = '''Maximum item size for the largest item.
If None, height of the item is used.
'''

MIN_ITEM_SIZE_HELP = '''Smallest item size to use.
Will stop when there is no more room in this size.
'''

BACKGROUND_COLOR_HELP = 'Background color for the cloud image.'

CONTOUR_WIDTH_HELP = 'If mask is not None and contour_width > 0, draw the mask contour.'

CONTOUR_COLOR_HELP = 'Mask contour color.'

MARGIN_HELP = 'The gap to allow between items.'

MODE_TYPES = [
    '1', # (1-bit pixels, black and white, stored with one pixel per byte)
    'L', # (8-bit pixels, grayscale)
    'P', # (8-bit pixels, mapped to any other mode using a color palette)
    'RGB', # (3x8-bit pixels, true color)
    'RGBA', # (4x8-bit pixels, true color with transparency mask)
    'CMYK', # (4x8-bit pixels, color separation)
    'YCbCr', # (3x8-bit pixels, color video format)
    'LAB', # (3x8-bit pixels, the L*a*b color space)
    'HSV', # (3x8-bit pixels, Hue, Saturation, Value color space)
    'I', # (32-bit signed integer pixels)
    'F', # (32-bit floating point pixels)
    'LA', # (L with alpha)
    'PA', # (P with alpha)
    'RGBX', # (true color with padding)
    'RGBa', # (true color with premultiplied alpha)
    'La', # (L with premultiplied alpha)
    'I;16', # (16-bit unsigned integer pixels)
    'I;16L', # (16-bit little endian unsigned integer pixels)
    'I;16B', # (16-bit big endian unsigned integer pixels)
    'I;16N'
]
MODE_HELP = 'Transparent background will be generated when mode is "RGBA" and background_color is None.'
TOTAL_THREADS_HELP = '''Experimental, using parallel algorithms with thread-allocations to accomplish image-cloud generation.  Value is the number of threads-of-execution to commit to generation.  A value of 1 will execute sequentially (not experimental); uses no parallel algorithms.
'''