from PIL import Image
import warnings
import numpy as np
from itemcloud.logger.base_logger import BaseLogger
from itemcloud.size import (Size, ResizeType)
from itemcloud.util.parsers import (parse_to_float, parse_to_int)
from itemcloud.reservations import (Reservations, SampledUnreservedOpening)
from itemcloud.util.search import SearchPattern, SearchProperties
from itemcloud.util.time_measure import TimeMeasure
from itemcloud.layout.base.layout import (
    LayoutContour,
    LayoutCanvas,
    Layout
)
from itemcloud.layout.base.layout_item import LayoutItem
from itemcloud.containers.base.weighted_item import (
    WeightedItem,
    resize_items_to_proportionally_fit,
    sort_by_weight
)
import itemcloud.item_cloud_defaults as item_cloud_defaults
# implementation was extrapolated from wordcloud and adapted for generic renderable objects
 
class ItemCloud(object):
    r"""itemcloud object for generating and pasting.

    Parameters
    ----------
    mask : Image or None (default=None)
        If not None, gives a binary mask on where to draw words. If mask is not
        None, width and height will be ignored and the shape of mask will be
        used instead. All white (#FF or #FFFFFF) entries will be considerd
        "masked out" while other entries will be free to draw on. [This
        changed in the most recent version!]

    size: (width, height) see objectcloud_defaults.DEFAULT_CLOUD_SIZE
        width and height of ItemCloud

    background_color : color value (default=objectcloud_defaults.DEFAULT_BACKGROUND_COLOR)
        Background color for the ItemCloud image.
    
    max_items : number (default=objectcloud_defaults.DEFAULT_MAX_ITEMS)
        The maximum number of items.

    max_item_size : (width, height) or None (default=None)
        Maximum item size for the largest item. If None, height of the item is
        used.

    min_item_size : (width, height) (default=objectcloud_defaults.DEFAULT_MIN_ITEM_SIZE)
        Smallest item size to use. Will stop when there is no more room in this
        size.

    item_step : int (default=objectcloud_defaults.DEFAULT_STEP_SIZE)
        Step size for the item. item_step > 1 might speed up computation but
        give a worse fit.

    item_rotation_increment: int (default=objectcloud_defaults.DEFAULT_ROTATION_INCREMENT)
    Degrees rotation increment for fitting the item in cloud. 
    small rotation_increments may result in longer runtimes to fit item.
    Items are 1st rotated, until the sum rotation is 360, and then shrunk and rotated again.
    
    resize_type: ResizeType (default=objectcloud_defaults.DEFAULT_RESIZE_TYPE)
    
    scale : float (default=objectcloud_defaults.DEFAULT_SCALE)
        Scaling between computation and drawing. For large word-cloud images,
        using scale instead of larger ItemCloud size is significantly faster, but
        might lead to a coarser fit for the words.

    contour_width: float (default=objectcloud_defaults.DEFAULT_CONTOUR_WIDTH)
        If mask is not None and contour_width > 0, draw the mask contour.
    
    contour_color: color value (default=objectcloud_defaults.DEFAULT_CONTOUR_COLOR)
        Mask contour color.
            
    margin: int (default=objectcloud_defaults.DEFAULT_MARGIN)
        The gap to allow between images
    
    mode : string (default=objectcloud_defaults.DEFAULT_MODE)
        Transparent background will be generated when mode is "RGBA" and
        background_color is None.
    """
    def __init__(self,
        logger: BaseLogger,
        mask: Image.Image | None = None,
        size: Size | None = None,
        background_color: str | None = None,
        max_items: int | None = None,
        max_item_size: Size | None = None,
        min_item_size: Size | None = None,
        item_step: int | None = None,
        item_rotation_increment: int | None = None,
        resize_type: ResizeType | None = None,
        scale: float | None = None,
        contour_width: float | None = None,
        contour_color: str | None = None,
        margin: int | None = None,
        mode: str | None = None,
        name: str | None = None,
        total_threads: int | None = None,
        search_pattern: SearchPattern | None = None
    ) -> None:
        self._mask: np.ndarray | None = np.array(mask) if mask is not None else None
        self._size = size if size is not None else Size.parse(item_cloud_defaults.DEFAULT_CLOUD_SIZE)
        self._background_color = background_color if background_color is not None else item_cloud_defaults.DEFAULT_BACKGROUND_COLOR
        self._max_items = max_items if max_items is not None else parse_to_int(item_cloud_defaults.DEFAULT_MAX_ITEMS)
        self._max_item_size = max_item_size
        self._min_item_size = min_item_size if min_item_size is not None else Size.parse(item_cloud_defaults.DEFAULT_MIN_ITEM_SIZE)
        self._item_step = item_step if item_step is not None else parse_to_int(item_cloud_defaults.DEFAULT_STEP_SIZE)
        self._item_rotation_increment = item_rotation_increment if item_rotation_increment is not None else parse_to_int(item_cloud_defaults.DEFAULT_ROTATION_INCREMENT)
        self._resize_type = resize_type if resize_type is not None else item_cloud_defaults.DEFAULT_RESIZE_TYPE
        self._scale = scale if scale is not None else parse_to_float(item_cloud_defaults.DEFAULT_SCALE)
        self._contour_width = contour_width if contour_width is not None else parse_to_int(item_cloud_defaults.DEFAULT_CONTOUR_WIDTH)
        self._contour_color = contour_color if contour_color is not None else item_cloud_defaults.DEFAULT_CONTOUR_COLOR
        self._logger = logger
        self._logger.reset_context()

        self._margin = margin if margin is not None else parse_to_int(item_cloud_defaults.DEFAULT_MARGIN)
        self._mode = mode if mode is not None else item_cloud_defaults.DEFAULT_MODE
        self._name = name if name is not None else 'itemcloud'
        self._total_threads = total_threads if total_threads is not None else parse_to_int(item_cloud_defaults.DEFAULT_TOTAL_THREADS)
        self._search_pattern = search_pattern if search_pattern is not None else SearchPattern[item_cloud_defaults.DEFAULT_SEARCH_PATTERN]
        self.layout_: Layout | None = None

    @property
    def mask(self) -> np.ndarray | None:
        return self._mask
    
    @mask.setter
    def mask(self, v: np.ndarray | None) -> None:
        self._mask = v

    @property
    def size(self) -> Size:
        return self._size
    
    @size.setter
    def size(self, v: Size) -> None:
        self._size = v
        if self._mask is not None:
            self._mask = None
            
    @property
    def item_step(self) -> int:
        return self._item_step

    @property
    def item_rotation_incremenet(self) -> int:
        return self._item_rotation_increment

    @property
    def resize_type(self) -> ResizeType:
        return self._resize_type

    @property
    def layout(self) -> Layout | None:
        return self.layout_
        
    def generate(self,
                weighted_items: list[WeightedItem],
                max_item_size: Size | None = None,
                cloud_expansion_step_size: int = 0,
    ) -> Layout:
        weighted_items = sort_by_weight(weighted_items, True)[:self._max_items]
        resize_count = 0
        itemcloud_size = self.size
        self._logger.info('Generating ItemCloud from {0} items'.format(len(weighted_items)))
        self._logger.push_indent('generating')

        proportional_items = resize_items_to_proportionally_fit(
            weighted_items,
            itemcloud_size,
            self.resize_type,
            self.item_step,
            self._margin
        )
        measure = TimeMeasure()
        measure.start()
        while True:
            self._logger.push_indent('creating-itemcloud')
            if self.mask is not None:
                itemcloud_size = Size(
                    self.mask.shape[0],
                    self.mask.shape[1]
                )
            
            result = self._generate(
                proportional_items,
                itemcloud_size,
                max_item_size
            )
            self._logger.pop_indent()
            if 0 < resize_count:
                self._logger.pop_indent()
            if 0 < cloud_expansion_step_size and len(result.items) != len(weighted_items):
                resize_count += 1
                if 1 == resize_count:                    
                    if self.mask is not None:
                        raise ValueError('Cannot expand_cloud_to_fit_all when mask is provided.')  

                new_ObjectCloud_size = itemcloud_size.adjust(
                    cloud_expansion_step_size, 
                    self.resize_type
                )
                self._logger.info('Expanded ItemCloud ({0} -> {1}) for dropped items ({2}/{3})'.format(
                    itemcloud_size.size_to_string(),
                    new_ObjectCloud_size.size_to_string(),
                    (len(weighted_items) - len(result.items)),
                    len(weighted_items)
                ))
                itemcloud_size = new_ObjectCloud_size
                
                self._logger.push_indent('expanded-itemcloud-{0}'.format(resize_count))
                continue
            break

        measure.stop()
        self._logger.pop_indent()
        self._logger.info('Generated: {0}/{1} items ({2})'.format(
            len(result.items),
            len(proportional_items),
            measure.latency_str()
        ))
        self._logger.reset_context()

        return result
    
    
    def maximize_empty_space(self, layout: Layout | None = None) -> Layout:
        if layout is None:
            self._check_generated()
            layout = self.layout_
        self.layout_ = layout
        reservations = Reservations.create_reservations(layout.canvas.reservation_map, self._logger)

        new_items: list[LayoutItem] = list()
        
        total_items = len(layout.items)
        self._logger.info('Maximizing ItemCloud empty-space around  {0} images'.format(total_items))
        self._logger.push_indent('maximizing-empty-space')
        measure = TimeMeasure()
        measure.start()
        maximized_count = 0

        for i in range(total_items - 1, -1, -1):
            item: LayoutItem = layout.items[i]
            item_measure = TimeMeasure()
            item_measure.start()
            self._logger.push_indent('item-{0}[{1}/{2}]'.format(item.name, total_items - i, total_items))
            self._logger.info('Maximizing...')
            new_reservation_box = reservations.maximize_existing_reservation(item.reservation_box)
            item_measure.stop()
            if item.reservation_box.equals(new_reservation_box):
                self._logger.info('Already Maximized ({0})'.format(item_measure.latency_str()))
                new_items.append(item)
                self._logger.pop_indent()
                continue
            self._logger.info('Maximized {0} -> {1} ({0})'.format(
                item.reservation_box.size.size_to_string(),
                new_reservation_box.size.size_to_string(),
                item_measure.latency_str()
            ))
            margin = 2 * (item.reservation_box.left - item.placement_box.left)
            if reservations.reserve_opening(item.name, item.reservation_no, new_reservation_box):
                new_items.append(
                    item.to_reserved_item(
                        new_reservation_box.remove_margin(margin),
                        item.rotated_degrees,
                        new_reservation_box,
                        item_measure.latency_str()
                    )
                )
                maximized_count += 1
                self._logger.info('resized {0} -> {1}. ({2})'.format(
                    item.reservation_box.box_to_string(),
                    new_reservation_box.box_to_string(),
                    item_measure.latency_str(),
                ))
            else:
                self._logger.error('Dropping new reservation. Failed to reserve maximized position. rotated_degrees ({1}), resize({2} -> {3}) ({4})'.format(
                    item.rotated_degrees,
                    item.reservation_box.box_to_string(),
                    new_reservation_box.box_to_string(),
                    item_measure.latency_str(),
                ))

            self._logger.pop_indent()

        measure.stop()
        self._logger.pop_indent()
        self._logger.info('Maximized {0}/{1} items ({2})'.format(
            maximized_count,
            len(new_items),
            measure.latency_str()
        ))    

        new_items.reverse()
        self.layout_ = Layout(
            LayoutCanvas(
                layout.canvas.size,
                layout.canvas.mode,
                layout.canvas.background_color,
                reservations.reservation_map,
                layout.canvas.name + '.maximized'
            ),
            LayoutContour(
                layout.contour.mask,
                layout.contour.width,
                layout.contour.color
            ),
            new_items,
            layout.max_items,
            layout.min_item_size,
            layout.item_step,
            layout.item_rotation_increment,
            layout.resize_type,
            layout.scale,
            layout.margin,
            layout.name + '.maximized',
            self._total_threads,
            measure.latency_str()
        )
        self._logger.reset_context()

        return self.layout_

    def _generate(self,
                proportional_items: list[WeightedItem],
                ObjectCloud_size: Size,
                max_item_size: Size | None
    ) -> Layout: 

        if len(proportional_items) <= 0:
            raise ValueError("We need at least 1 item to plot a ItemCloud, "
                             "got %d." % len(proportional_items))
        
        reservations = Reservations(self._logger, ObjectCloud_size, self._total_threads)
        search_properties = SearchProperties.start(reservations.reservation_area, self._search_pattern)

        layout_items: list[LayoutItem] = list()

        if max_item_size is None:
            # if not provided use default max_size
            max_item_size = self._max_item_size

        if max_item_size is None:
            sizes: list[Size] = []
            # figure out a good image_size by trying the 1st two inages
            if len(proportional_items) == 1:
                # we only have one word. We make it big!
                sizes = [self._size]
            else:
                layout = self._generate(
                    proportional_items[:2],
                    ObjectCloud_size,
                    self._size
                )
                # find image sizes
                sizes = [x.placement_box.size for x in layout.items]
            
            if 0 == len(sizes):
                raise ValueError(
                    "Couldn't find space to paste. Either the ItemCloud size"
                    " is too small or too much of the image is masked "
                    "out.")
            if 1 < len(sizes):
                max_item_size = Size(
                    int(2 * sizes[0].width * sizes[1].width / (sizes[0].width + sizes[1].width)),
                    int(2 * sizes[0].height * sizes[1].height / (sizes[0].height + sizes[1].height))
                )
            else:
                max_item_size = sizes[0]

        generation_measure = TimeMeasure()
        # find best location for each image
        total = len(proportional_items)
        generation_measure.start()
        for index in range(total):
            weight = proportional_items[index].weight
            item_size: Size = proportional_items[index]
            name = proportional_items[index].name
            measure = TimeMeasure()
            measure.start()
            self._logger.push_indent('image-{0}[{1}/{2}]'.format(name, index + 1, total))

            if weight == 0:
                self._logger.info('Dropping 0 weight'.format(
                    index+1, total, name
                ))
                self._logger.pop_indent()
                continue

            self._logger.info('Finding position in ItemCloud')
            
            sampled_result: SampledUnreservedOpening = reservations.sample_to_find_unreserved_opening(
                item_size,
                self._min_item_size,
                self._margin,
                self._resize_type,
                self._item_step,
                self._item_rotation_increment,
                search_properties
            )
            measure.stop()
            if sampled_result.found:
                self._logger.info('Found position: samplings({0}), rotated_degrees ({1}), resize({2}->{3}) ({4})'.format(
                    sampled_result.sampling_total,
                    sampled_result.rotated_degrees,
                    item_size.size_to_string(),
                    sampled_result.new_size.size_to_string(),
                    measure.latency_str()
                ))
                reservation_no = index + 1
                if reservations.reserve_opening(name, reservation_no, sampled_result.opening_box):
                    layout_items.append(proportional_items[index].to_layout_item(
                        sampled_result.actual_box,
                        sampled_result.rotated_degrees,
                        sampled_result.opening_box,
                        reservation_no,
                        measure.latency_str()
                    ))
                    search_properties = search_properties.next(sampled_result.opening_box)
                else:
                    reservation_no = index
                    self._logger.error('Dropping item: samplings({0}). Failed to reserve position. rotated_degrees ({1}), resize({2} -> {3}) ({4})'.format(
                        sampled_result.sampling_total,
                        item_size.size_to_string(),
                        sampled_result.new_size.size_to_string(),
                        measure.latency_str()
                    ))

            else:
                self._logger.info('Dropping item: samplings({0}). {1} resize({2} -> {3}) ({4})'.format(
                    sampled_result.sampling_total,
                    'Item resized too small' if sampled_result.new_size.is_less_than(self._min_item_size) else '',
                    item_size.size_to_string(),
                    sampled_result.new_size.size_to_string(),
                    measure.latency_str()
                ))
                
                    
            self._logger.pop_indent()

        generation_measure.stop()
        self.layout_ = Layout(
            LayoutCanvas(
                ObjectCloud_size,
                self._mode,
                self._background_color,
                reservations.reservation_map,
                self._name
            ),
            LayoutContour(
                self._get_boolean_mask(self._mask) * 255 if self._mask is not None else None,
                self._contour_width,
                self._contour_color
            ),
            layout_items,
            self._max_items,
            self._min_item_size,
            self._item_step,
            self._item_rotation_increment,
            self._resize_type,
            self._scale,
            self._margin,
            self._name + '.layout',
            self._total_threads,
            generation_measure.latency_str(),
            self._search_pattern
        )
        return self.layout_

    def _check_generated(self) -> None:
        """Check if ``layout_`` was computed, otherwise raise error."""
        if not hasattr(self, "layout_"):
            raise ValueError("ItemCloud has not been calculated, call generate"
                             " first.")
    
    def _get_boolean_mask(self, mask: np.ndarray) -> bool | np.ndarray:
        """Cast to two dimensional boolean mask."""
        if mask.dtype.kind == 'f':
            warnings.warn("mask image should be unsigned byte between 0"
                          " and 255. Got a float array")
        if mask.ndim == 2:
            boolean_mask = mask == 255
        elif mask.ndim == 3:
            # if all channels are white, mask out
            boolean_mask = np.all(mask[:, :, :3] == 255, axis=-1)
        else:
            raise ValueError("Got mask of invalid shape: %s" % f'mask({mask.shape[0]},{mask.shape[1]},{mask.shape[2]})')
        return boolean_mask