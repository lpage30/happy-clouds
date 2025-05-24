import sys
from itemcloud.cli_support.cloud_generation_types import (
    CloudType,
    g_cloud_types,
    to_cloud_type_helper
)

def generate_imagecloud() -> None:
    g_cloud_types[CloudType.IMAGE_CLOUD].cli_generate(sys.argv[1:])

def generate_textcloud() -> None:
    g_cloud_types[CloudType.TEXT_CLOUD].cli_generate(sys.argv[1:])

def generate_textimagecloud() -> None:
    g_cloud_types[CloudType.TEXT_IMAGE_CLOUD].cli_generate(sys.argv[1:])

def generate_mixeditemcloud() -> None:
    g_cloud_types[CloudType.MIXED_CLOUD].cli_generate(sys.argv[1:])

def layout_imagecloud() -> None:
    g_cloud_types[CloudType.IMAGE_CLOUD].cli_layout(sys.argv[1:])

def layout_textcloud() -> None:
    g_cloud_types[CloudType.TEXT_CLOUD].cli_layout(sys.argv[1:])

def layout_textimagecloud() -> None:
    g_cloud_types[CloudType.TEXT_IMAGE_CLOUD].cli_layout(sys.argv[1:])

def layout_mixeditemcloud() -> None:
    g_cloud_types[CloudType.MIXED_CLOUD].cli_layout(sys.argv[1:])

if __name__ == '__main__':
    try:
        if 3 > len(sys.argv):
            raise ValueError('Insufficient arguments')
        cloud_type_helper = to_cloud_type_helper(sys.argv[2])
        if 'generate' == sys.argv[1].lower():
            cloud_type_helper.cli_generate(sys.argv[3:])
        elif 'layout' == sys.argv[1].lower():
            cloud_type_helper.cli_layout(sys.argv[3:])
        else:
            raise ValueError('{0} {1}> - {0} is not an action'.format(sys.argv[1], sys.argv[2]))
    except Exception as e:
        print('Failed executing cli {0}\n'.format(e))
        print('Usage: generate|layout {0} ...arguments for activity...'.format('|'.join([h.name for h in g_cloud_types.values()])))
        
