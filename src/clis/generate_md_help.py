from itemcloud.cli_support.cloud_generation_types import (
    g_cloud_types,
)
from itemcloud.layout.base.layout_defaults import (
    LAYOUT_CSV_HEADERS,
    LAYOUT_CSV_HEADER_HELP,
)

def generate_md_help() -> None:
    args = ['-h']
    print("## script usage")
    for h in g_cloud_types.values():
        print("### `generate_{0}`".format(h.name))
        print("```")
        print(h.generate_args(args).help())
        print("```")
        print("#### input CSV format")
        print("```csv")
        print('"{0}"'.format('","'.join(h.csv_fields)))
        print('{0}'.format(','.join(h.csv_value_type)))
        print("```")
        print("### `layout_{0}`".format(h.name))
        print("```")
        print(h.layout_args(args).help())
        print("```")
        print("#### input CSV format")
        print("```csv")
        print('"{0}"'.format('","'.join(LAYOUT_CSV_HEADERS)))
        print('{0}'.format(','.join(LAYOUT_CSV_HEADER_HELP)))
        print("```")

if __name__ == '__main__':
    generate_md_help()