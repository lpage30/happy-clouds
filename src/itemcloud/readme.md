# ItemCloud
A generic item intended to be used to create an image or text/word or 'other' cloud image based on weights

## script usage
### `generate_imagecloud`
```
usage: generate_imagecloud [-h] -i <csv_filepath> [-output_directory <output-directory-path>]
                           [-output_image_format blp|bmp|dds|dib|eps|gif|icns|ico|im|jpeg|mpo|msp|pcx|pfm|png|ppm|sgi|webp|xbm]
                           [-show_itemcloud] [-no-show_itemcloud] [-show_itemcloud_reservation_chart]
                           [-no-show_itemcloud_reservation_chart] [-maximize_empty_space] [-no-maximize_empty_space]
                           [-verbose] [-no-verbose] [-log_filepath <log-filepath>] [-cloud_size "<width>,<height>"]
                           [-placement_search_pattern NONE|RANDOM|LINEAR|RAY|SPIRAL] [-cloud_expansion_step_size <int>]
                           [-margin <number>] [-min_item_size "<width>,<height>"] [-step_size <int>]
                           [-rotation_increment <int>]
                           [-resize_type NO_RESIZE_TYPE|MAINTAIN_ASPECT_RATIO|MAINTAIN_PERCENTAGE_CHANGE]
                           [-max_item_size "<width>,<height>"]
                           [-mode 1|L|P|RGB|RGBA|CMYK|YCbCr|LAB|HSV|I|F|LA|PA|RGBX|RGBa|La|I;16|I;16L|I;16B|I;16N]
                           [-background_color <color-name>] [-mask <image_file_path>] [-contour_width <float>]
                           [-contour_color <color-name>] [-total_threads <int>]

            Generate an 'imagecloud' from a csv file indicating weight, and image
            

options:
  -h, --help            show this help message and exit
  -i, --input <csv_filepath>
                        Required, csv file for weighted images with following format:
                        "weight","image_filepath"
                        <float>,<image-filepath>
  -output_directory <output-directory-path>
                        Optional, output directory for all output
  -output_image_format blp|bmp|dds|dib|eps|gif|icns|ico|im|jpeg|mpo|msp|pcx|pfm|png|ppm|sgi|webp|xbm
                        Optional,(default png) image format: [blp,bmp,dds,dib,eps,gif,icns,ico,im,jpeg,mpo,msp,pcx,pfm,png,ppm,sgi,webp,xbm]
  -show_itemcloud       Optional, (default) show itemcloud.
  -no-show_itemcloud    Optional, do not show mage itemcloud.
  -show_itemcloud_reservation_chart
                        Optional, show reservation_chart for itemcloud.
  -no-show_itemcloud_reservation_chart
                        Optional, (default) do not show reservation_chart for itemcloud.
  -maximize_empty_space
                        Optional maximize items, after generation, to fill surrounding empty space.
  -no-maximize_empty_space
                        Optional (default) maximize items, after generation, to fill surrounding empty space.
  -verbose              Optional, report progress as constructing itemcloud
  -no-verbose           Optional, (default) report progress as constructing itemcloud
  -log_filepath <log-filepath>
                        Optional, all output logging will also be written to this logfile
  -cloud_size "<width>,<height>"
                        Optional, (default 400,200) width and height of canvas
  -placement_search_pattern NONE|RANDOM|LINEAR|RAY|SPIRAL
                        Optional,(default NONE) Search for openings using a pattern: https://i.ytimg.com/vi/8rXv-0gg-ZY/maxresdefault.jpg
                        NONE|RANDOM|LINEAR|RAY|SPIRAL
  -cloud_expansion_step_size <int>
                        Optional, (default 0) Step size for expanding cloud to fit more images
                        images will be proportionally fit to the original cloud size but may still not get placed to fit in cloud.
                        step > 0 the cloud will expand by this amount in a loop until all images fit into it.
                        step > 1 might speed up computation but give a worse fit.
  -margin <number>      Optional, (default 1) The gap to allow between items.
  -min_item_size "<width>,<height>"
                        Optional, (default 4,4) Smallest item size to use.
                        Will stop when there is no more room in this size.
  -step_size <int>      Optional, (default 1) Step size for the item. 
                        step > 1 might speed up computation
                        but give a worse fit.
  -rotation_increment <int>
                        Optional, (default 90) Degrees rotation increment for fitting the item in cloud. 
                        small rotation_increments may result in longer runtimes to fit item.
                        Images are 1st rotated, until the sum rotation is 360, and then shrunk and rotated again.
  -resize_type NO_RESIZE_TYPE|MAINTAIN_ASPECT_RATIO|MAINTAIN_PERCENTAGE_CHANGE
                        Optional, (default MAINTAIN_ASPECT_RATIO) Image resizing can be done by maintaining aspect ratio (MAINTAIN_ASPECT_RATIO), step/width percent change evenly applied (MAINTAIN_PERCENTAGE_CHANGE), or simply step change (NO_RESIZE_TYPE)
  -max_item_size "<width>,<height>"
                        Optional, (default None) Maximum item size for the largest item.
                        If None, height of the item is used.
  -mode 1|L|P|RGB|RGBA|CMYK|YCbCr|LAB|HSV|I|F|LA|PA|RGBX|RGBa|La|I;16|I;16L|I;16B|I;16N
                        Optional, (default RGBA) Transparent background will be generated when mode is "RGBA" and background_color is None.
  -background_color <color-name>
                        Optional, (default None) Background color for the cloud image.
  -mask <image_file_path>
                        Optional, (default None) Image file
                        If not None, gives a binary mask on where to draw words.
                        If mask is not None, width and height will be ignored
                        and the shape of mask will be used instead. 
                        All white (#FF or #FFFFFF) entries will be considered "masked out"
                        while other entries will be free to draw on.
  -contour_width <float>
                        Optional, (default 0) If mask is not None and contour_width > 0, draw the mask contour.
  -contour_color <color-name>
                        Optional, (default black) Mask contour color.
  -total_threads <int>  Optional, (default $(default)s) Experimental, using parallel algorithms with thread-allocations to accomplish image-cloud generation.  Value is the number of threads-of-execution to commit to generation.  A value of 1 will execute sequentially (not experimental); uses no parallel algorithms.

```
#### input CSV format
```csv
"weight","image_filepath"
<float>,<image-filepath>
```
### `layout_imagecloud`
```
usage: layout_imagecloud [-h] -i <csv_filepath> [-output_directory <output-directory-path>]
                         [-output_image_format blp|bmp|dds|dib|eps|gif|icns|ico|im|jpeg|mpo|msp|pcx|pfm|png|ppm|sgi|webp|xbm]
                         [-show_itemcloud] [-no-show_itemcloud] [-show_itemcloud_reservation_chart]
                         [-no-show_itemcloud_reservation_chart] [-maximize_empty_space] [-no-maximize_empty_space]
                         [-verbose] [-no-verbose] [-log_filepath <log-filepath>] [-scale <float>]

             Layout and show a generated 'imagecloud' from its layout csv file
            

options:
  -h, --help            show this help message and exit
  -i, --input <csv_filepath>
                        Required, csv file representing 1 Layout Contour, 1 Layout Canvas and N Layout Items:
                        "layout_max_items","layout_min_item_size_width","layout_min_item_size_height","layout_item_step","layout_item_rotation_increment","layout_resize_type","layout_scale","layout_margin","layout_name","layout_total_threads","layout_latency","layout_search_pattern","layout_canvas_name","layout_canvas_mode","layout_canvas_background_color","layout_canvas_size_width","layout_canvas_size_height","layout_canvas_reservation_map_csv_filepath","layout_contour_mask_image_filepath","layout_contour_width","layout_contour_color","layout_item_filepath","layout_item_position_x","layout_item_position_y","layout_item_size_width","layout_item_size_height","layout_item_rotated_degrees","layout_item_reserved_position_x","layout_item_reserved_position_y","layout_item_reserved_size_width","layout_item_reserved_size_height","layout_item_reservation_no","layout_item_latency","layout_item_type"
                        <integer>,<width>,<height>,<integer>,<integer>,NO_RESIZE_TYPE|MAINTAIN_ASPECT_RATIO|MAINTAIN_PERCENTAGE_CHANGE,<float>,<image-margin>,<name>,<integer>,<string>,NONE|RANDOM|LINEAR|RAY|SPIRAL,<name>,1|L|P|RGB|RGBA|CMYK|YCbCr|LAB|HSV|I|F|LA|PA|RGBX|RGBa|La|I;16|I;16L|I;16B|I;16N,<empty>|<any-color-name>,<width>,<height>,<csv-filepath-of-reservation_map>,<empty>|<filepath-of-image-used-as-mask>,<float>,<any-color-name>,<filepath-of-item-to-render>,<x>,<y>,<width>,<height>,<degrees-rotation>,<x>,<y>,<width>,<height>,<empty>|<reservation_no_in_reservation_map>,<string>,<name-of-subclassed-layout-type>
  -output_directory <output-directory-path>
                        Optional, output directory for all output
  -output_image_format blp|bmp|dds|dib|eps|gif|icns|ico|im|jpeg|mpo|msp|pcx|pfm|png|ppm|sgi|webp|xbm
                        Optional,(default png) image format: [blp,bmp,dds,dib,eps,gif,icns,ico,im,jpeg,mpo,msp,pcx,pfm,png,ppm,sgi,webp,xbm]
  -show_itemcloud       Optional, show itemcloud.
  -no-show_itemcloud    Optional, (default) do not show mage itemcloud.
  -show_itemcloud_reservation_chart
                        Optional, show reservation_chart for itemcloud.
  -no-show_itemcloud_reservation_chart
                        Optional, (default) do not show reservation_chart for itemcloud.
  -maximize_empty_space
                        Optional maximize items, after generation, to fill surrounding empty space.
  -no-maximize_empty_space
                        Optional (default) maximize items, after generation, to fill surrounding empty space.
  -verbose              Optional, report progress as constructing itemcloud
  -no-verbose           Optional, (default) report progress as constructing itemcloud
  -log_filepath <log-filepath>
                        Optional, all output logging will also be written to this logfile
  -scale <float>        Optional, (default 1.0) scale up/down all images

```
#### input CSV format
```csv
"layout_max_items","layout_min_item_size_width","layout_min_item_size_height","layout_item_step","layout_item_rotation_increment","layout_resize_type","layout_scale","layout_margin","layout_name","layout_total_threads","layout_latency","layout_search_pattern","layout_canvas_name","layout_canvas_mode","layout_canvas_background_color","layout_canvas_size_width","layout_canvas_size_height","layout_canvas_reservation_map_csv_filepath","layout_contour_mask_image_filepath","layout_contour_width","layout_contour_color","layout_item_filepath","layout_item_position_x","layout_item_position_y","layout_item_size_width","layout_item_size_height","layout_item_rotated_degrees","layout_item_reserved_position_x","layout_item_reserved_position_y","layout_item_reserved_size_width","layout_item_reserved_size_height","layout_item_reservation_no","layout_item_latency","layout_item_type"
<integer>,<width>,<height>,<integer>,<integer>,NO_RESIZE_TYPE|MAINTAIN_ASPECT_RATIO|MAINTAIN_PERCENTAGE_CHANGE,<float>,<image-margin>,<name>,<integer>,<string>,NONE|RANDOM|LINEAR|RAY|SPIRAL,<name>,1|L|P|RGB|RGBA|CMYK|YCbCr|LAB|HSV|I|F|LA|PA|RGBX|RGBa|La|I;16|I;16L|I;16B|I;16N,<empty>|<any-color-name>,<width>,<height>,<csv-filepath-of-reservation_map>,<empty>|<filepath-of-image-used-as-mask>,<float>,<any-color-name>,<filepath-of-item-to-render>,<x>,<y>,<width>,<height>,<degrees-rotation>,<x>,<y>,<width>,<height>,<empty>|<reservation_no_in_reservation_map>,<string>,<name-of-subclassed-layout-type>
```
### `generate_textcloud`
```
usage: generate_textcloud [-h] -i <csv_filepath> [-output_directory <output-directory-path>]
                          [-output_image_format blp|bmp|dds|dib|eps|gif|icns|ico|im|jpeg|mpo|msp|pcx|pfm|png|ppm|sgi|webp|xbm]
                          [-show_itemcloud] [-no-show_itemcloud] [-show_itemcloud_reservation_chart]
                          [-no-show_itemcloud_reservation_chart] [-maximize_empty_space] [-no-maximize_empty_space]
                          [-verbose] [-no-verbose] [-log_filepath <log-filepath>] [-cloud_size "<width>,<height>"]
                          [-placement_search_pattern NONE|RANDOM|LINEAR|RAY|SPIRAL] [-cloud_expansion_step_size <int>]
                          [-margin <number>] [-min_item_size "<width>,<height>"] [-step_size <int>]
                          [-rotation_increment <int>]
                          [-resize_type NO_RESIZE_TYPE|MAINTAIN_ASPECT_RATIO|MAINTAIN_PERCENTAGE_CHANGE]
                          [-max_item_size "<width>,<height>"]
                          [-mode 1|L|P|RGB|RGBA|CMYK|YCbCr|LAB|HSV|I|F|LA|PA|RGBX|RGBa|La|I;16|I;16L|I;16B|I;16N]
                          [-background_color <color-name>] [-mask <image_file_path>] [-contour_width <float>]
                          [-contour_color <color-name>] [-total_threads <int>]

            Generate an 'textcloud' from a csv file indicating weight, and text
            

options:
  -h, --help            show this help message and exit
  -i, --input <csv_filepath>
                        Required, csv file for weighted text with following format:
                        "name","text","weight","font_name_path","min_font_size","max_font_size","text_layout","text_stroke_width","text_anchor","text_align","foreground_color","background_color"
                        <name>,text|phrase|prose,<float>,<path-to-your-font>|<name-of-font>|empty(random),<float>|empty(random),<float>|empty(random),empty(0)|0(BASIC)|1(RAQM),empty|<integer>,empty(ma)|<l|m|r><t|m|b|a>,empty(center)|center|right|left,<color-name>|#RRGGBB|empty|random,<color-name>|#RRGGBB|empty|random
  -output_directory <output-directory-path>
                        Optional, output directory for all output
  -output_image_format blp|bmp|dds|dib|eps|gif|icns|ico|im|jpeg|mpo|msp|pcx|pfm|png|ppm|sgi|webp|xbm
                        Optional,(default png) image format: [blp,bmp,dds,dib,eps,gif,icns,ico,im,jpeg,mpo,msp,pcx,pfm,png,ppm,sgi,webp,xbm]
  -show_itemcloud       Optional, (default) show itemcloud.
  -no-show_itemcloud    Optional, do not show mage itemcloud.
  -show_itemcloud_reservation_chart
                        Optional, show reservation_chart for itemcloud.
  -no-show_itemcloud_reservation_chart
                        Optional, (default) do not show reservation_chart for itemcloud.
  -maximize_empty_space
                        Optional maximize items, after generation, to fill surrounding empty space.
  -no-maximize_empty_space
                        Optional (default) maximize items, after generation, to fill surrounding empty space.
  -verbose              Optional, report progress as constructing itemcloud
  -no-verbose           Optional, (default) report progress as constructing itemcloud
  -log_filepath <log-filepath>
                        Optional, all output logging will also be written to this logfile
  -cloud_size "<width>,<height>"
                        Optional, (default 400,200) width and height of canvas
  -placement_search_pattern NONE|RANDOM|LINEAR|RAY|SPIRAL
                        Optional,(default NONE) Search for openings using a pattern: https://i.ytimg.com/vi/8rXv-0gg-ZY/maxresdefault.jpg
                        NONE|RANDOM|LINEAR|RAY|SPIRAL
  -cloud_expansion_step_size <int>
                        Optional, (default 0) Step size for expanding cloud to fit more images
                        images will be proportionally fit to the original cloud size but may still not get placed to fit in cloud.
                        step > 0 the cloud will expand by this amount in a loop until all images fit into it.
                        step > 1 might speed up computation but give a worse fit.
  -margin <number>      Optional, (default 1) The gap to allow between items.
  -min_item_size "<width>,<height>"
                        Optional, (default 4,4) Smallest item size to use.
                        Will stop when there is no more room in this size.
  -step_size <int>      Optional, (default 1) Step size for the item. 
                        step > 1 might speed up computation
                        but give a worse fit.
  -rotation_increment <int>
                        Optional, (default 90) Degrees rotation increment for fitting the item in cloud. 
                        small rotation_increments may result in longer runtimes to fit item.
                        Images are 1st rotated, until the sum rotation is 360, and then shrunk and rotated again.
  -resize_type NO_RESIZE_TYPE|MAINTAIN_ASPECT_RATIO|MAINTAIN_PERCENTAGE_CHANGE
                        Optional, (default MAINTAIN_ASPECT_RATIO) Image resizing can be done by maintaining aspect ratio (MAINTAIN_ASPECT_RATIO), step/width percent change evenly applied (MAINTAIN_PERCENTAGE_CHANGE), or simply step change (NO_RESIZE_TYPE)
  -max_item_size "<width>,<height>"
                        Optional, (default None) Maximum item size for the largest item.
                        If None, height of the item is used.
  -mode 1|L|P|RGB|RGBA|CMYK|YCbCr|LAB|HSV|I|F|LA|PA|RGBX|RGBa|La|I;16|I;16L|I;16B|I;16N
                        Optional, (default RGBA) Transparent background will be generated when mode is "RGBA" and background_color is None.
  -background_color <color-name>
                        Optional, (default None) Background color for the cloud image.
  -mask <image_file_path>
                        Optional, (default None) Image file
                        If not None, gives a binary mask on where to draw words.
                        If mask is not None, width and height will be ignored
                        and the shape of mask will be used instead. 
                        All white (#FF or #FFFFFF) entries will be considered "masked out"
                        while other entries will be free to draw on.
  -contour_width <float>
                        Optional, (default 0) If mask is not None and contour_width > 0, draw the mask contour.
  -contour_color <color-name>
                        Optional, (default black) Mask contour color.
  -total_threads <int>  Optional, (default $(default)s) Experimental, using parallel algorithms with thread-allocations to accomplish image-cloud generation.  Value is the number of threads-of-execution to commit to generation.  A value of 1 will execute sequentially (not experimental); uses no parallel algorithms.

```
#### input CSV format
```csv
"name","text","weight","font_name_path","min_font_size","max_font_size","text_layout","text_stroke_width","text_anchor","text_align","foreground_color","background_color"
<name>,text|phrase|prose,<float>,<path-to-your-font>|<name-of-font>|empty(random),<float>|empty(random),<float>|empty(random),empty(0)|0(BASIC)|1(RAQM),empty|<integer>,empty(ma)|<l|m|r><t|m|b|a>,empty(center)|center|right|left,<color-name>|#RRGGBB|empty|random,<color-name>|#RRGGBB|empty|random
```
### `layout_textcloud`
```
usage: layout_textcloud [-h] -i <csv_filepath> [-output_directory <output-directory-path>]
                        [-output_image_format blp|bmp|dds|dib|eps|gif|icns|ico|im|jpeg|mpo|msp|pcx|pfm|png|ppm|sgi|webp|xbm]
                        [-show_itemcloud] [-no-show_itemcloud] [-show_itemcloud_reservation_chart]
                        [-no-show_itemcloud_reservation_chart] [-maximize_empty_space] [-no-maximize_empty_space]
                        [-verbose] [-no-verbose] [-log_filepath <log-filepath>] [-scale <float>]

             Layout and show a generated 'textcloud' from its layout csv file
            

options:
  -h, --help            show this help message and exit
  -i, --input <csv_filepath>
                        Required, csv file representing 1 Layout Contour, 1 Layout Canvas and N Layout Items:
                        "layout_max_items","layout_min_item_size_width","layout_min_item_size_height","layout_item_step","layout_item_rotation_increment","layout_resize_type","layout_scale","layout_margin","layout_name","layout_total_threads","layout_latency","layout_search_pattern","layout_canvas_name","layout_canvas_mode","layout_canvas_background_color","layout_canvas_size_width","layout_canvas_size_height","layout_canvas_reservation_map_csv_filepath","layout_contour_mask_image_filepath","layout_contour_width","layout_contour_color","layout_item_filepath","layout_item_position_x","layout_item_position_y","layout_item_size_width","layout_item_size_height","layout_item_rotated_degrees","layout_item_reserved_position_x","layout_item_reserved_position_y","layout_item_reserved_size_width","layout_item_reserved_size_height","layout_item_reservation_no","layout_item_latency","layout_item_type"
                        <integer>,<width>,<height>,<integer>,<integer>,NO_RESIZE_TYPE|MAINTAIN_ASPECT_RATIO|MAINTAIN_PERCENTAGE_CHANGE,<float>,<image-margin>,<name>,<integer>,<string>,NONE|RANDOM|LINEAR|RAY|SPIRAL,<name>,1|L|P|RGB|RGBA|CMYK|YCbCr|LAB|HSV|I|F|LA|PA|RGBX|RGBa|La|I;16|I;16L|I;16B|I;16N,<empty>|<any-color-name>,<width>,<height>,<csv-filepath-of-reservation_map>,<empty>|<filepath-of-image-used-as-mask>,<float>,<any-color-name>,<filepath-of-item-to-render>,<x>,<y>,<width>,<height>,<degrees-rotation>,<x>,<y>,<width>,<height>,<empty>|<reservation_no_in_reservation_map>,<string>,<name-of-subclassed-layout-type>
  -output_directory <output-directory-path>
                        Optional, output directory for all output
  -output_image_format blp|bmp|dds|dib|eps|gif|icns|ico|im|jpeg|mpo|msp|pcx|pfm|png|ppm|sgi|webp|xbm
                        Optional,(default png) image format: [blp,bmp,dds,dib,eps,gif,icns,ico,im,jpeg,mpo,msp,pcx,pfm,png,ppm,sgi,webp,xbm]
  -show_itemcloud       Optional, show itemcloud.
  -no-show_itemcloud    Optional, (default) do not show mage itemcloud.
  -show_itemcloud_reservation_chart
                        Optional, show reservation_chart for itemcloud.
  -no-show_itemcloud_reservation_chart
                        Optional, (default) do not show reservation_chart for itemcloud.
  -maximize_empty_space
                        Optional maximize items, after generation, to fill surrounding empty space.
  -no-maximize_empty_space
                        Optional (default) maximize items, after generation, to fill surrounding empty space.
  -verbose              Optional, report progress as constructing itemcloud
  -no-verbose           Optional, (default) report progress as constructing itemcloud
  -log_filepath <log-filepath>
                        Optional, all output logging will also be written to this logfile
  -scale <float>        Optional, (default 1.0) scale up/down all images

```
#### input CSV format
```csv
"layout_max_items","layout_min_item_size_width","layout_min_item_size_height","layout_item_step","layout_item_rotation_increment","layout_resize_type","layout_scale","layout_margin","layout_name","layout_total_threads","layout_latency","layout_search_pattern","layout_canvas_name","layout_canvas_mode","layout_canvas_background_color","layout_canvas_size_width","layout_canvas_size_height","layout_canvas_reservation_map_csv_filepath","layout_contour_mask_image_filepath","layout_contour_width","layout_contour_color","layout_item_filepath","layout_item_position_x","layout_item_position_y","layout_item_size_width","layout_item_size_height","layout_item_rotated_degrees","layout_item_reserved_position_x","layout_item_reserved_position_y","layout_item_reserved_size_width","layout_item_reserved_size_height","layout_item_reservation_no","layout_item_latency","layout_item_type"
<integer>,<width>,<height>,<integer>,<integer>,NO_RESIZE_TYPE|MAINTAIN_ASPECT_RATIO|MAINTAIN_PERCENTAGE_CHANGE,<float>,<image-margin>,<name>,<integer>,<string>,NONE|RANDOM|LINEAR|RAY|SPIRAL,<name>,1|L|P|RGB|RGBA|CMYK|YCbCr|LAB|HSV|I|F|LA|PA|RGBX|RGBa|La|I;16|I;16L|I;16B|I;16N,<empty>|<any-color-name>,<width>,<height>,<csv-filepath-of-reservation_map>,<empty>|<filepath-of-image-used-as-mask>,<float>,<any-color-name>,<filepath-of-item-to-render>,<x>,<y>,<width>,<height>,<degrees-rotation>,<x>,<y>,<width>,<height>,<empty>|<reservation_no_in_reservation_map>,<string>,<name-of-subclassed-layout-type>
```
### `generate_textimagecloud`
```
usage: generate_textimagecloud [-h] -i <csv_filepath> [-output_directory <output-directory-path>]
                               [-output_image_format blp|bmp|dds|dib|eps|gif|icns|ico|im|jpeg|mpo|msp|pcx|pfm|png|ppm|sgi|webp|xbm]
                               [-show_itemcloud] [-no-show_itemcloud] [-show_itemcloud_reservation_chart]
                               [-no-show_itemcloud_reservation_chart] [-maximize_empty_space]
                               [-no-maximize_empty_space] [-verbose] [-no-verbose] [-log_filepath <log-filepath>]
                               [-cloud_size "<width>,<height>"]
                               [-placement_search_pattern NONE|RANDOM|LINEAR|RAY|SPIRAL]
                               [-cloud_expansion_step_size <int>] [-margin <number>]
                               [-min_item_size "<width>,<height>"] [-step_size <int>] [-rotation_increment <int>]
                               [-resize_type NO_RESIZE_TYPE|MAINTAIN_ASPECT_RATIO|MAINTAIN_PERCENTAGE_CHANGE]
                               [-max_item_size "<width>,<height>"]
                               [-mode 1|L|P|RGB|RGBA|CMYK|YCbCr|LAB|HSV|I|F|LA|PA|RGBX|RGBa|La|I;16|I;16L|I;16B|I;16N]
                               [-background_color <color-name>] [-mask <image_file_path>] [-contour_width <float>]
                               [-contour_color <color-name>] [-total_threads <int>]

            Generate an 'textimagecloud' from a csv file indicating weight, and text-on-image
            

options:
  -h, --help            show this help message and exit
  -i, --input <csv_filepath>
                        Required, csv file for weighted text-images with following format:
                        "name","text","weight","font_name_path","min_font_size","max_font_size","text_layout","text_stroke_width","text_anchor","text_align","foreground_color","background_color","transparency_percent","image_filepath"
                        <name>,text|phrase|prose,<float>,<path-to-your-font>|<name-of-font>|empty(random),<float>|empty(random),<float>|empty(random),empty(0)|0(BASIC)|1(RAQM),empty|<integer>,empty(ma)|<l|m|r><t|m|b|a>,empty(center)|center|right|left,<color-name>|#RRGGBB|empty|random,<color-name>|#RRGGBB|empty|random,<float>,<image-filepath>
  -output_directory <output-directory-path>
                        Optional, output directory for all output
  -output_image_format blp|bmp|dds|dib|eps|gif|icns|ico|im|jpeg|mpo|msp|pcx|pfm|png|ppm|sgi|webp|xbm
                        Optional,(default png) image format: [blp,bmp,dds,dib,eps,gif,icns,ico,im,jpeg,mpo,msp,pcx,pfm,png,ppm,sgi,webp,xbm]
  -show_itemcloud       Optional, (default) show itemcloud.
  -no-show_itemcloud    Optional, do not show mage itemcloud.
  -show_itemcloud_reservation_chart
                        Optional, show reservation_chart for itemcloud.
  -no-show_itemcloud_reservation_chart
                        Optional, (default) do not show reservation_chart for itemcloud.
  -maximize_empty_space
                        Optional maximize items, after generation, to fill surrounding empty space.
  -no-maximize_empty_space
                        Optional (default) maximize items, after generation, to fill surrounding empty space.
  -verbose              Optional, report progress as constructing itemcloud
  -no-verbose           Optional, (default) report progress as constructing itemcloud
  -log_filepath <log-filepath>
                        Optional, all output logging will also be written to this logfile
  -cloud_size "<width>,<height>"
                        Optional, (default 400,200) width and height of canvas
  -placement_search_pattern NONE|RANDOM|LINEAR|RAY|SPIRAL
                        Optional,(default NONE) Search for openings using a pattern: https://i.ytimg.com/vi/8rXv-0gg-ZY/maxresdefault.jpg
                        NONE|RANDOM|LINEAR|RAY|SPIRAL
  -cloud_expansion_step_size <int>
                        Optional, (default 0) Step size for expanding cloud to fit more images
                        images will be proportionally fit to the original cloud size but may still not get placed to fit in cloud.
                        step > 0 the cloud will expand by this amount in a loop until all images fit into it.
                        step > 1 might speed up computation but give a worse fit.
  -margin <number>      Optional, (default 1) The gap to allow between items.
  -min_item_size "<width>,<height>"
                        Optional, (default 4,4) Smallest item size to use.
                        Will stop when there is no more room in this size.
  -step_size <int>      Optional, (default 1) Step size for the item. 
                        step > 1 might speed up computation
                        but give a worse fit.
  -rotation_increment <int>
                        Optional, (default 90) Degrees rotation increment for fitting the item in cloud. 
                        small rotation_increments may result in longer runtimes to fit item.
                        Images are 1st rotated, until the sum rotation is 360, and then shrunk and rotated again.
  -resize_type NO_RESIZE_TYPE|MAINTAIN_ASPECT_RATIO|MAINTAIN_PERCENTAGE_CHANGE
                        Optional, (default MAINTAIN_ASPECT_RATIO) Image resizing can be done by maintaining aspect ratio (MAINTAIN_ASPECT_RATIO), step/width percent change evenly applied (MAINTAIN_PERCENTAGE_CHANGE), or simply step change (NO_RESIZE_TYPE)
  -max_item_size "<width>,<height>"
                        Optional, (default None) Maximum item size for the largest item.
                        If None, height of the item is used.
  -mode 1|L|P|RGB|RGBA|CMYK|YCbCr|LAB|HSV|I|F|LA|PA|RGBX|RGBa|La|I;16|I;16L|I;16B|I;16N
                        Optional, (default RGBA) Transparent background will be generated when mode is "RGBA" and background_color is None.
  -background_color <color-name>
                        Optional, (default None) Background color for the cloud image.
  -mask <image_file_path>
                        Optional, (default None) Image file
                        If not None, gives a binary mask on where to draw words.
                        If mask is not None, width and height will be ignored
                        and the shape of mask will be used instead. 
                        All white (#FF or #FFFFFF) entries will be considered "masked out"
                        while other entries will be free to draw on.
  -contour_width <float>
                        Optional, (default 0) If mask is not None and contour_width > 0, draw the mask contour.
  -contour_color <color-name>
                        Optional, (default black) Mask contour color.
  -total_threads <int>  Optional, (default $(default)s) Experimental, using parallel algorithms with thread-allocations to accomplish image-cloud generation.  Value is the number of threads-of-execution to commit to generation.  A value of 1 will execute sequentially (not experimental); uses no parallel algorithms.

```
#### input CSV format
```csv
"name","text","weight","font_name_path","min_font_size","max_font_size","text_layout","text_stroke_width","text_anchor","text_align","foreground_color","background_color","transparency_percent","image_filepath"
<name>,text|phrase|prose,<float>,<path-to-your-font>|<name-of-font>|empty(random),<float>|empty(random),<float>|empty(random),empty(0)|0(BASIC)|1(RAQM),empty|<integer>,empty(ma)|<l|m|r><t|m|b|a>,empty(center)|center|right|left,<color-name>|#RRGGBB|empty|random,<color-name>|#RRGGBB|empty|random,<float>,<image-filepath>
```
### `layout_textimagecloud`
```
usage: layout_textimagecloud [-h] -i <csv_filepath> [-output_directory <output-directory-path>]
                             [-output_image_format blp|bmp|dds|dib|eps|gif|icns|ico|im|jpeg|mpo|msp|pcx|pfm|png|ppm|sgi|webp|xbm]
                             [-show_itemcloud] [-no-show_itemcloud] [-show_itemcloud_reservation_chart]
                             [-no-show_itemcloud_reservation_chart] [-maximize_empty_space] [-no-maximize_empty_space]
                             [-verbose] [-no-verbose] [-log_filepath <log-filepath>] [-scale <float>]

             Layout and show a generated 'textimagecloud' from its layout csv file
            

options:
  -h, --help            show this help message and exit
  -i, --input <csv_filepath>
                        Required, csv file representing 1 Layout Contour, 1 Layout Canvas and N Layout Items:
                        "layout_max_items","layout_min_item_size_width","layout_min_item_size_height","layout_item_step","layout_item_rotation_increment","layout_resize_type","layout_scale","layout_margin","layout_name","layout_total_threads","layout_latency","layout_search_pattern","layout_canvas_name","layout_canvas_mode","layout_canvas_background_color","layout_canvas_size_width","layout_canvas_size_height","layout_canvas_reservation_map_csv_filepath","layout_contour_mask_image_filepath","layout_contour_width","layout_contour_color","layout_item_filepath","layout_item_position_x","layout_item_position_y","layout_item_size_width","layout_item_size_height","layout_item_rotated_degrees","layout_item_reserved_position_x","layout_item_reserved_position_y","layout_item_reserved_size_width","layout_item_reserved_size_height","layout_item_reservation_no","layout_item_latency","layout_item_type"
                        <integer>,<width>,<height>,<integer>,<integer>,NO_RESIZE_TYPE|MAINTAIN_ASPECT_RATIO|MAINTAIN_PERCENTAGE_CHANGE,<float>,<image-margin>,<name>,<integer>,<string>,NONE|RANDOM|LINEAR|RAY|SPIRAL,<name>,1|L|P|RGB|RGBA|CMYK|YCbCr|LAB|HSV|I|F|LA|PA|RGBX|RGBa|La|I;16|I;16L|I;16B|I;16N,<empty>|<any-color-name>,<width>,<height>,<csv-filepath-of-reservation_map>,<empty>|<filepath-of-image-used-as-mask>,<float>,<any-color-name>,<filepath-of-item-to-render>,<x>,<y>,<width>,<height>,<degrees-rotation>,<x>,<y>,<width>,<height>,<empty>|<reservation_no_in_reservation_map>,<string>,<name-of-subclassed-layout-type>
  -output_directory <output-directory-path>
                        Optional, output directory for all output
  -output_image_format blp|bmp|dds|dib|eps|gif|icns|ico|im|jpeg|mpo|msp|pcx|pfm|png|ppm|sgi|webp|xbm
                        Optional,(default png) image format: [blp,bmp,dds,dib,eps,gif,icns,ico,im,jpeg,mpo,msp,pcx,pfm,png,ppm,sgi,webp,xbm]
  -show_itemcloud       Optional, show itemcloud.
  -no-show_itemcloud    Optional, (default) do not show mage itemcloud.
  -show_itemcloud_reservation_chart
                        Optional, show reservation_chart for itemcloud.
  -no-show_itemcloud_reservation_chart
                        Optional, (default) do not show reservation_chart for itemcloud.
  -maximize_empty_space
                        Optional maximize items, after generation, to fill surrounding empty space.
  -no-maximize_empty_space
                        Optional (default) maximize items, after generation, to fill surrounding empty space.
  -verbose              Optional, report progress as constructing itemcloud
  -no-verbose           Optional, (default) report progress as constructing itemcloud
  -log_filepath <log-filepath>
                        Optional, all output logging will also be written to this logfile
  -scale <float>        Optional, (default 1.0) scale up/down all images

```
#### input CSV format
```csv
"layout_max_items","layout_min_item_size_width","layout_min_item_size_height","layout_item_step","layout_item_rotation_increment","layout_resize_type","layout_scale","layout_margin","layout_name","layout_total_threads","layout_latency","layout_search_pattern","layout_canvas_name","layout_canvas_mode","layout_canvas_background_color","layout_canvas_size_width","layout_canvas_size_height","layout_canvas_reservation_map_csv_filepath","layout_contour_mask_image_filepath","layout_contour_width","layout_contour_color","layout_item_filepath","layout_item_position_x","layout_item_position_y","layout_item_size_width","layout_item_size_height","layout_item_rotated_degrees","layout_item_reserved_position_x","layout_item_reserved_position_y","layout_item_reserved_size_width","layout_item_reserved_size_height","layout_item_reservation_no","layout_item_latency","layout_item_type"
<integer>,<width>,<height>,<integer>,<integer>,NO_RESIZE_TYPE|MAINTAIN_ASPECT_RATIO|MAINTAIN_PERCENTAGE_CHANGE,<float>,<image-margin>,<name>,<integer>,<string>,NONE|RANDOM|LINEAR|RAY|SPIRAL,<name>,1|L|P|RGB|RGBA|CMYK|YCbCr|LAB|HSV|I|F|LA|PA|RGBX|RGBa|La|I;16|I;16L|I;16B|I;16N,<empty>|<any-color-name>,<width>,<height>,<csv-filepath-of-reservation_map>,<empty>|<filepath-of-image-used-as-mask>,<float>,<any-color-name>,<filepath-of-item-to-render>,<x>,<y>,<width>,<height>,<degrees-rotation>,<x>,<y>,<width>,<height>,<empty>|<reservation_no_in_reservation_map>,<string>,<name-of-subclassed-layout-type>
```
### `generate_mixeditemcloud`
```
usage: generate_mixeditemcloud [-h] -i <csv_filepath> [-output_directory <output-directory-path>]
                               [-output_image_format blp|bmp|dds|dib|eps|gif|icns|ico|im|jpeg|mpo|msp|pcx|pfm|png|ppm|sgi|webp|xbm]
                               [-show_itemcloud] [-no-show_itemcloud] [-show_itemcloud_reservation_chart]
                               [-no-show_itemcloud_reservation_chart] [-maximize_empty_space]
                               [-no-maximize_empty_space] [-verbose] [-no-verbose] [-log_filepath <log-filepath>]
                               [-cloud_size "<width>,<height>"]
                               [-placement_search_pattern NONE|RANDOM|LINEAR|RAY|SPIRAL]
                               [-cloud_expansion_step_size <int>] [-margin <number>]
                               [-min_item_size "<width>,<height>"] [-step_size <int>] [-rotation_increment <int>]
                               [-resize_type NO_RESIZE_TYPE|MAINTAIN_ASPECT_RATIO|MAINTAIN_PERCENTAGE_CHANGE]
                               [-max_item_size "<width>,<height>"]
                               [-mode 1|L|P|RGB|RGBA|CMYK|YCbCr|LAB|HSV|I|F|LA|PA|RGBX|RGBa|La|I;16|I;16L|I;16B|I;16N]
                               [-background_color <color-name>] [-mask <image_file_path>] [-contour_width <float>]
                               [-contour_color <color-name>] [-total_threads <int>]

            Generate an 'mixeditemcloud' from a csv file indicating weight, and image, text, text-on-image
            

options:
  -h, --help            show this help message and exit
  -i, --input <csv_filepath>
                        Required, csv file for weighted mix of images/text/text-images with following format:
                        "weight","image_filepath","name","text","font_name_path","min_font_size","max_font_size","text_layout","text_stroke_width","text_anchor","text_align","foreground_color","background_color","transparency_percent"
                        <float>,<image-filepath>,<name>,text|phrase|prose,<path-to-your-font>|<name-of-font>|empty(random),<float>|empty(random),<float>|empty(random),empty(0)|0(BASIC)|1(RAQM),empty|<integer>,empty(ma)|<l|m|r><t|m|b|a>,empty(center)|center|right|left,<color-name>|#RRGGBB|empty|random,<color-name>|#RRGGBB|empty|random,<float>
  -output_directory <output-directory-path>
                        Optional, output directory for all output
  -output_image_format blp|bmp|dds|dib|eps|gif|icns|ico|im|jpeg|mpo|msp|pcx|pfm|png|ppm|sgi|webp|xbm
                        Optional,(default png) image format: [blp,bmp,dds,dib,eps,gif,icns,ico,im,jpeg,mpo,msp,pcx,pfm,png,ppm,sgi,webp,xbm]
  -show_itemcloud       Optional, (default) show itemcloud.
  -no-show_itemcloud    Optional, do not show mage itemcloud.
  -show_itemcloud_reservation_chart
                        Optional, show reservation_chart for itemcloud.
  -no-show_itemcloud_reservation_chart
                        Optional, (default) do not show reservation_chart for itemcloud.
  -maximize_empty_space
                        Optional maximize items, after generation, to fill surrounding empty space.
  -no-maximize_empty_space
                        Optional (default) maximize items, after generation, to fill surrounding empty space.
  -verbose              Optional, report progress as constructing itemcloud
  -no-verbose           Optional, (default) report progress as constructing itemcloud
  -log_filepath <log-filepath>
                        Optional, all output logging will also be written to this logfile
  -cloud_size "<width>,<height>"
                        Optional, (default 400,200) width and height of canvas
  -placement_search_pattern NONE|RANDOM|LINEAR|RAY|SPIRAL
                        Optional,(default NONE) Search for openings using a pattern: https://i.ytimg.com/vi/8rXv-0gg-ZY/maxresdefault.jpg
                        NONE|RANDOM|LINEAR|RAY|SPIRAL
  -cloud_expansion_step_size <int>
                        Optional, (default 0) Step size for expanding cloud to fit more images
                        images will be proportionally fit to the original cloud size but may still not get placed to fit in cloud.
                        step > 0 the cloud will expand by this amount in a loop until all images fit into it.
                        step > 1 might speed up computation but give a worse fit.
  -margin <number>      Optional, (default 1) The gap to allow between items.
  -min_item_size "<width>,<height>"
                        Optional, (default 4,4) Smallest item size to use.
                        Will stop when there is no more room in this size.
  -step_size <int>      Optional, (default 1) Step size for the item. 
                        step > 1 might speed up computation
                        but give a worse fit.
  -rotation_increment <int>
                        Optional, (default 90) Degrees rotation increment for fitting the item in cloud. 
                        small rotation_increments may result in longer runtimes to fit item.
                        Images are 1st rotated, until the sum rotation is 360, and then shrunk and rotated again.
  -resize_type NO_RESIZE_TYPE|MAINTAIN_ASPECT_RATIO|MAINTAIN_PERCENTAGE_CHANGE
                        Optional, (default MAINTAIN_ASPECT_RATIO) Image resizing can be done by maintaining aspect ratio (MAINTAIN_ASPECT_RATIO), step/width percent change evenly applied (MAINTAIN_PERCENTAGE_CHANGE), or simply step change (NO_RESIZE_TYPE)
  -max_item_size "<width>,<height>"
                        Optional, (default None) Maximum item size for the largest item.
                        If None, height of the item is used.
  -mode 1|L|P|RGB|RGBA|CMYK|YCbCr|LAB|HSV|I|F|LA|PA|RGBX|RGBa|La|I;16|I;16L|I;16B|I;16N
                        Optional, (default RGBA) Transparent background will be generated when mode is "RGBA" and background_color is None.
  -background_color <color-name>
                        Optional, (default None) Background color for the cloud image.
  -mask <image_file_path>
                        Optional, (default None) Image file
                        If not None, gives a binary mask on where to draw words.
                        If mask is not None, width and height will be ignored
                        and the shape of mask will be used instead. 
                        All white (#FF or #FFFFFF) entries will be considered "masked out"
                        while other entries will be free to draw on.
  -contour_width <float>
                        Optional, (default 0) If mask is not None and contour_width > 0, draw the mask contour.
  -contour_color <color-name>
                        Optional, (default black) Mask contour color.
  -total_threads <int>  Optional, (default $(default)s) Experimental, using parallel algorithms with thread-allocations to accomplish image-cloud generation.  Value is the number of threads-of-execution to commit to generation.  A value of 1 will execute sequentially (not experimental); uses no parallel algorithms.

```
#### input CSV format
```csv
"weight","image_filepath","name","text","font_name_path","min_font_size","max_font_size","text_layout","text_stroke_width","text_anchor","text_align","foreground_color","background_color","transparency_percent"
<float>,<image-filepath>,<name>,text|phrase|prose,<path-to-your-font>|<name-of-font>|empty(random),<float>|empty(random),<float>|empty(random),empty(0)|0(BASIC)|1(RAQM),empty|<integer>,empty(ma)|<l|m|r><t|m|b|a>,empty(center)|center|right|left,<color-name>|#RRGGBB|empty|random,<color-name>|#RRGGBB|empty|random,<float>
```
### `layout_mixeditemcloud`
```
usage: layout_mixeditemcloud [-h] -i <csv_filepath> [-output_directory <output-directory-path>]
                             [-output_image_format blp|bmp|dds|dib|eps|gif|icns|ico|im|jpeg|mpo|msp|pcx|pfm|png|ppm|sgi|webp|xbm]
                             [-show_itemcloud] [-no-show_itemcloud] [-show_itemcloud_reservation_chart]
                             [-no-show_itemcloud_reservation_chart] [-maximize_empty_space] [-no-maximize_empty_space]
                             [-verbose] [-no-verbose] [-log_filepath <log-filepath>] [-scale <float>]

             Layout and show a generated 'mixeditemcloud' from its layout csv file
            

options:
  -h, --help            show this help message and exit
  -i, --input <csv_filepath>
                        Required, csv file representing 1 Layout Contour, 1 Layout Canvas and N Layout Items:
                        "layout_max_items","layout_min_item_size_width","layout_min_item_size_height","layout_item_step","layout_item_rotation_increment","layout_resize_type","layout_scale","layout_margin","layout_name","layout_total_threads","layout_latency","layout_search_pattern","layout_canvas_name","layout_canvas_mode","layout_canvas_background_color","layout_canvas_size_width","layout_canvas_size_height","layout_canvas_reservation_map_csv_filepath","layout_contour_mask_image_filepath","layout_contour_width","layout_contour_color","layout_item_filepath","layout_item_position_x","layout_item_position_y","layout_item_size_width","layout_item_size_height","layout_item_rotated_degrees","layout_item_reserved_position_x","layout_item_reserved_position_y","layout_item_reserved_size_width","layout_item_reserved_size_height","layout_item_reservation_no","layout_item_latency","layout_item_type"
                        <integer>,<width>,<height>,<integer>,<integer>,NO_RESIZE_TYPE|MAINTAIN_ASPECT_RATIO|MAINTAIN_PERCENTAGE_CHANGE,<float>,<image-margin>,<name>,<integer>,<string>,NONE|RANDOM|LINEAR|RAY|SPIRAL,<name>,1|L|P|RGB|RGBA|CMYK|YCbCr|LAB|HSV|I|F|LA|PA|RGBX|RGBa|La|I;16|I;16L|I;16B|I;16N,<empty>|<any-color-name>,<width>,<height>,<csv-filepath-of-reservation_map>,<empty>|<filepath-of-image-used-as-mask>,<float>,<any-color-name>,<filepath-of-item-to-render>,<x>,<y>,<width>,<height>,<degrees-rotation>,<x>,<y>,<width>,<height>,<empty>|<reservation_no_in_reservation_map>,<string>,<name-of-subclassed-layout-type>
  -output_directory <output-directory-path>
                        Optional, output directory for all output
  -output_image_format blp|bmp|dds|dib|eps|gif|icns|ico|im|jpeg|mpo|msp|pcx|pfm|png|ppm|sgi|webp|xbm
                        Optional,(default png) image format: [blp,bmp,dds,dib,eps,gif,icns,ico,im,jpeg,mpo,msp,pcx,pfm,png,ppm,sgi,webp,xbm]
  -show_itemcloud       Optional, show itemcloud.
  -no-show_itemcloud    Optional, (default) do not show mage itemcloud.
  -show_itemcloud_reservation_chart
                        Optional, show reservation_chart for itemcloud.
  -no-show_itemcloud_reservation_chart
                        Optional, (default) do not show reservation_chart for itemcloud.
  -maximize_empty_space
                        Optional maximize items, after generation, to fill surrounding empty space.
  -no-maximize_empty_space
                        Optional (default) maximize items, after generation, to fill surrounding empty space.
  -verbose              Optional, report progress as constructing itemcloud
  -no-verbose           Optional, (default) report progress as constructing itemcloud
  -log_filepath <log-filepath>
                        Optional, all output logging will also be written to this logfile
  -scale <float>        Optional, (default 1.0) scale up/down all images

```
#### input CSV format
```csv
"layout_max_items","layout_min_item_size_width","layout_min_item_size_height","layout_item_step","layout_item_rotation_increment","layout_resize_type","layout_scale","layout_margin","layout_name","layout_total_threads","layout_latency","layout_search_pattern","layout_canvas_name","layout_canvas_mode","layout_canvas_background_color","layout_canvas_size_width","layout_canvas_size_height","layout_canvas_reservation_map_csv_filepath","layout_contour_mask_image_filepath","layout_contour_width","layout_contour_color","layout_item_filepath","layout_item_position_x","layout_item_position_y","layout_item_size_width","layout_item_size_height","layout_item_rotated_degrees","layout_item_reserved_position_x","layout_item_reserved_position_y","layout_item_reserved_size_width","layout_item_reserved_size_height","layout_item_reservation_no","layout_item_latency","layout_item_type"
<integer>,<width>,<height>,<integer>,<integer>,NO_RESIZE_TYPE|MAINTAIN_ASPECT_RATIO|MAINTAIN_PERCENTAGE_CHANGE,<float>,<image-margin>,<name>,<integer>,<string>,NONE|RANDOM|LINEAR|RAY|SPIRAL,<name>,1|L|P|RGB|RGBA|CMYK|YCbCr|LAB|HSV|I|F|LA|PA|RGBX|RGBa|La|I;16|I;16L|I;16B|I;16N,<empty>|<any-color-name>,<width>,<height>,<csv-filepath-of-reservation_map>,<empty>|<filepath-of-image-used-as-mask>,<float>,<any-color-name>,<filepath-of-item-to-render>,<x>,<y>,<width>,<height>,<degrees-rotation>,<x>,<y>,<width>,<height>,<empty>|<reservation_no_in_reservation_map>,<string>,<name-of-subclassed-layout-type>
```
### `generate_weighted_text`
```
usage: generate_weighted_text [-h] -c <total-words-randomly-picked> --words WORDS [WORDS ...] [-output-filepath-csv <output-filepath>]
                                         [-log-filepath <log-filepath>]

        Generate randomly weighted text csv file from provided list of text arguments.
        csv file for weighted text with following format:
"name","text","weight","font_name_path","min_font_size","max_font_size","text_layout","text_stroke_width","text_anchor","text_align","foreground_color","background_color"
<name>,text|phrase|prose,<float>,<path-to-your-font>|<name-of-font>|empty(random),<float>|empty(random),<float>|empty(random),empty(0)|0(BASIC)|1(RAQM),empty|<integer>,empty(ma)|<l|m|r><t|m|b|a>,empty(center)|center|right|left,<color-name>|#RRGGBB|empty|random,<color-name>|#RRGGBB|empty|random

        

options:
  -h, --help            show this help message and exit
  -c, --count <total-words-randomly-picked>
                        
                                Required, Program will loop this many times, randomly picking 1 word from provided base array of text.
                                Weights created are number of occurrences of each word in randomly generated list.
                                
  --words WORDS [WORDS ...]
                        
                                Required, list of words|numbers|phrases (in quotes) making up base array of text.
                                This array is iteratively randomly picked from to produce weighted word list.
                                
  -output-filepath-csv <output-filepath>
                        Optional, weighted text csv filepath to create with output (default: stdout)
  -log-filepath <log-filepath>
                        Optional, all output logging will also be written to this logfile
```
#### output CSV format
```csv
"name","text","weight","font_name_path","min_font_size","max_font_size","text_layout","text_stroke_width","text_anchor","text_align","foreground_color","background_color"
<name>,text|phrase|prose,<float>,<path-to-your-font>|<name-of-font>|empty(random),<float>|empty(random),<float>|empty(random),empty(0)|0(BASIC)|1(RAQM),empty|<integer>,empty(ma)|<l|m|r><t|m|b|a>,empty(center)|center|right|left,<color-name>|#RRGGBB|empty|random,<color-name>|#RRGGBB|empty|random
```

## Notes
### Motivation
In constructing an ImageCloud based on WordCloud functionality it was clear most of the functionality could be abstracted out and operated on without knowing the data that is to be rendered.   

- all data has a concept of a bounding box
- all data has a concept of a weight associated with it
- ignoring the data type, and you have to fit/place weighted bounding boxes in a single image
- ItemCloud basically creates a single image collage of weighted bounding boxes or weighted items


### Abstract classes:
- itemcloud.layout.layout_item
    - see example implementation of this at imagecloud.layout.layout_image.py
- itemcloud.containers.named_item
    - example implementation of this at objectcloud.containers.named_image.py
- itemcloud.containers.weighted_item
    - example implementation of this at imagecloud.containers.weighted_image.py

### Extending
1. determine what data you want to present in your cloud.
2. Create a `Weighted<YourData>` class inheriting from `itemcloud.containers.weighted_item`
	- implement abstract methods: 
		- `to_layout_item`
		- `to_fitted_weighted_item`
	- Example: `imagecloud.containers.weighted_image`
3. Create a `Layout<YourData>` class inheriting from `itemcloud.layout.layout_item`
	- implement abstract methods:
		- `get_item_as_image`
		- `write_item`
		- `load_item`
		- `to_reserved_item`
	- Example: `imagecloud.layout.layout_image`
4. Create a `<YourData>Cloud` class inheriting from `itemcloud.itemcloud`  
   Example: `imagecloud.image_cloud`
   
5. Create your CLI (command-line-interface) functions with argparser. `itemcloud.clis.cli_base_arguments`.  
	Examples:
	- `imagecloud.clis.
