import argparse
import sys
from itemcloud.clis.cli_base_arguments import CLIBaseArguments
import itemcloud.clis.cli_helpers as cli_helpers
from itemcloud.layout.layout import Layout
from itemcloud.layout.layout_defaults import LAYOUT_CSV_FILE_HELP
from anyitemcloud.layout.layout_item import create_layout_item
from anyitemcloud.anyitem_cloud import AnyItemCloud

DEFAULT_SCALE = '1.0'
DEFAULT_VERBOSE = False
DEFAULT_SHOW = False

class LayoutCLIArguments(CLIBaseArguments):
    name = 'layout_anyitemcloud'
    def __init__ (
        self, 
        parsedArgs
    ) -> None:
        super().__init__(self.name, parsedArgs)
        self.scale: float = parsedArgs.scale
    
    @staticmethod
    def parse(arguments: list[str]):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            prog=LayoutCLIArguments.name,
            description='''
            Layout and show a generated \'AnyItemCloud\' from its layout csv file
            '''
        )
        CLIBaseArguments.add_parser_arguments(
            parser,
            LAYOUT_CSV_FILE_HELP,
            DEFAULT_SHOW,
            DEFAULT_VERBOSE
        )
        parser.add_argument(
            '-scale',
            default=DEFAULT_SCALE,
            metavar='<float>',
            type=lambda v: cli_helpers.is_float(parser, v),
            help='Optional, (default %(default)s) scale up/down all images'
        )


        args = parser.parse_args(arguments if 0 < len(arguments) else ['-h'])
        return LayoutCLIArguments(args)


def layout(args: LayoutCLIArguments | None = None) -> None:
    sys_args = sys.argv[1:]    
    if args == None:
        args = LayoutCLIArguments.parse(sys_args)

    
    args.logger.info('{0} {1}'.format(LayoutCLIArguments.name, ' '.join(sys_args)))
    args.logger.info('loading {0} ...'.format(args.input))
    layout = Layout.load(args.input, create_layout_item)
    args.logger.info('loaded layout with {0} items'.format(len(layout.items)))
    args.logger.info('laying-out and showing anyitemcloud layout with {0} scaling.'.format(args.scale))
    
    layout.set_names(
        args.get_output_name(layout.name),
        args.get_output_name(layout.canvas.name)
    )

    if args.maximize_empty_space:
        args.logger.info('Maximizing {0} images: expanding them to fit their surrounding empty space.'.format(len(layout.items)))
        cloud = AnyItemCloud.create(layout, args.logger)
        layout = cloud.maximize_empty_space(layout)
        
    collage = layout.to_image(args.logger, args.scale)
    reservation_chart = layout.to_reservation_chart_image()
    args.try_save_output(collage, reservation_chart, layout)
        
    if args.show_itemcloud:
        collage.show()

    if args.show_itemcloud_reservation_chart:
        reservation_chart.show()



if __name__ == '__main__':
    layout()