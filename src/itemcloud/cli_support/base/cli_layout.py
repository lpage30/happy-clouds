from typing import List
from itemcloud.item_cloud import ItemCloud
from itemcloud.layout.base.layout import (
    Layout, create_layout_item_f
)
from itemcloud.cli_support.base.cli_base_layout_arguments import (
    CLIBaseLayoutArguments,
    create_item_cloud
)

class CLILayoutResult:
    def __init__(
        self,
        cloud: ItemCloud,
        layout: Layout
    ) -> None:
        self.cloud = cloud
        self.layout = layout


def cli_layout(
    sys_args: List[str],
    args: CLIBaseLayoutArguments,
    create_layout_item: create_layout_item_f
) -> CLILayoutResult:
    args.load()
    args.logger.info('{0} {1}'.format(args.name, ' '.join(sys_args)))
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
        cloud = create_item_cloud(layout, args.logger, ItemCloud)
        layout = cloud.maximize_empty_space(layout)
        
    collage = layout.to_image(args.logger, args.scale)
    reservation_chart = layout.to_reservation_chart_image()
    args.try_save_output(collage, reservation_chart, layout)
        
    if args.show_itemcloud:
        collage.show()

    if args.show_itemcloud_reservation_chart:
        reservation_chart.show()
    
    return CLILayoutResult(cloud, layout)