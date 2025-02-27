# TextCloud
A concrete implementation of ItemCloud that constructs an ItemCloud where items are text.
weighted texts are used to construct a single collage textcloud (similar to wordcloud)


### CLI Usage: 
Once installed you will be able to execute scripts defined in the `myproject.toml`

#### generate_textcloud
```
usage: generate_textcloud [-h] -i <csv_filepath> [-output_directory <output-directory-path>]
                          [-output_image_format blp|bmp|dds|dib|eps|gif|icns|ico|im|jpeg|mpo|msp|pcx|pfm|png|ppm|sgi|webp|xbm]
                          [-show_itemcloud] [-no-show_itemcloud]
                          [-show_itemcloud_reservation_chart]
                          [-no-show_itemcloud_reservation_chart] [-maximize_empty_space]
                          [-no-maximize_empty_space] [-verbose] [-no-verbose]
                          [-log_filepath <log-filepath>] [-cloud_size "<width>,<height>"]
                          [-cloud_expansion_step_size <int>] [-margin <number>]
                          [-min_item_size "<width>,<height>"] [-step_size <int>]
                          [-rotation_increment <int>]
                          [-resize_type NO_RESIZE_TYPE|MAINTAIN_ASPECT_RATIO|MAINTAIN_PERCENTAGE_CHANGE]
                          [-max_item_size "<width>,<height>"]
                          [-mode 1|L|P|RGB|RGBA|CMYK|YCbCr|LAB|HSV|I|F|LA|PA|RGBX|RGBa|La|I;16|I;16L|I;16B|I;16N]
                          [-background_color <color-name>] [-mask <image_file_path>]
                          [-contour_width <float>] [-contour_color <color-name>]
                          [-total_threads <int>]

            Generate an 'ImageCloud' from a csv file indicating image filepath and weight for image.
            

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

  #### CSV to import
csv file for weighted text with following format:
```csv
"name","text","weight","font_name_path","min_font_size","max_font_size","text_layout","text_stroke_width","text_anchor","text_align","foreground_color","background_color"
<name>,text|phrase|prose,<float>,<path-to-your-font>|<name-of-font>|empty(random),<float>|empty(random),<float>|empty(random),empty(0)|0(BASIC)|1(RAQM),empty|<integer>,empty(ma)|<l|m|r><t|m|b|a>,empty(center)|center|right|left,<color-name>|#RRGGBB|empty|random,<color-name>|#RRGGBB|empty|random
```
#### Sample generate script
`sample-generate-text` is an example of how the `generate_textcloud` could be used
