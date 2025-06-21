import numpy as np
from typing import List
from itemcloud.item_cloud import ItemCloud
from itemcloud.containers.base.item_factory import load_weighted_items
from itemcloud.containers.base.weighted_item import WeightedItem
from itemcloud.layout.base.layout import Layout
from itemcloud.cli_support.base.cli_base_generate_arguments import (
    CLIBaseGenerateArguments,
    create_item_cloud
)

class CLIGenerateResult:
    def __init__(
        self,
        loaded_items: List[WeightedItem],
        cloud: ItemCloud,
        layout: Layout
    ) -> None:
        self.loaded_items = loaded_items
        self.cloud = cloud
        self.layout = layout

def save_layout(
    args: CLIBaseGenerateArguments,
    layout: Layout
) -> None:
    reconstructed_reservation_map = layout.reconstruct_reservation_map(args.logger)
    if not(np.array_equal(layout.canvas.reservation_map, reconstructed_reservation_map)):
        args.logger.info('Warning reservations map from generation not same as reconstructed from items.')
    
    collage = layout.to_image(args.logger)
    reservation_chart = layout.to_reservation_chart_image()

    args.try_save_output(collage, reservation_chart, layout)

    if args.show_itemcloud_reservation_chart:
        reservation_chart.show()

    if args.show_itemcloud:
        collage.show()

def cli_generate(
    sys_args: List[str],
    args: CLIBaseGenerateArguments
) -> CLIGenerateResult:
    args.load()
    print('{0} {1}'.format(args.name, ' '.join(sys_args)))
    args.logger.info('{0} {1}'.format(args.name, ' '.join(sys_args)))
    cloud = create_item_cloud(args, ItemCloud)
    args.logger.info('loading {0} ...'.format(args.input))
    weighted_items: List[WeightedItem] = load_weighted_items(args.input)
    total_items = len(weighted_items)
    args.logger.info('loaded {0} weights and items'.format(total_items))
    args.logger.info('generating cloud from {0} weighted and normalized items.{1}'.format(
        total_items,
        ' Cloud will be expanded iteratively by cloud_expansion_step_size until all items are positioned.' if 0 != args.cloud_expansion_step_size else ''
    ))

    layout = cloud.generate(weighted_items, cloud_expansion_step_size=args.cloud_expansion_step_size)
    save_layout(
        args,
        layout
    )
    if args.maximize_empty_space:
        args.logger.info('Maximizing {0} items: expanding them to fit their surrounding empty space.'.format(len(layout.items)))
        layout = cloud.maximize_empty_space(layout)
        save_layout(
            args,
            layout
        )

    return CLIGenerateResult(weighted_items, cloud, layout)
