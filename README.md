# Happy-Clouds
This is a set of python modules to be used to load and create different types of displayable data-based clouds. WordClouds, ImageClouds, <other>Clouds are good for conveying a collection of weighted data(words/images, other) into a visible representation of that data and its importance relative to other data.

### Approach
We define a single 'generic' ItemCloud module containing some abstract classes and functionality for fitting weighted bounding boxes (which could contain image/text/whatever) into a single image.

Different 'types' of data can then inherit from this ItemCloud and implement concrete classes to inherit from the abstract ones. 

## Build/Install

The following bash scripts may be used to clean/build/install (edit locally) this package
- `clean`  deletes all side-effect files from `build`
- `build`  calls `clean` and compiles cython and python code into installable packages
- `install`  calls `build` and does `pip install` of package 
- `uninstall`  does `pip uninstall` of package and then `clean`

## sample cli scripts
- `sample-generate` provides parameter values for cli command to generate an ImageCloud from csv file of weighted images
- `sample-layout` provides parameter values for cli command to layout an existing generated ImageCloud from its written layout.

## Modules

### ItemCloud
This is the generic module containing abstract classes. This does all the work of making the cloud from data.
[ItemCloud readme](src/itemcloud/readme.md)

### ImageCloud
This is a data cloud to render weighted images in a single 'Image' based cloud.
[ImageCloud readme](src/imagecloud/readme.md)

### Future other clouds
* WordCloud (just for fun)
* need to think of others that would actually be useful. :)

## References / acknowledgements
- [amueller's wordcloud](https://github.com/amueller/word_cloud)
    - [`wordcloud/wordcloud.py`](https://github.com/amueller/word_cloud/blob/main/wordcloud/wordcloud.py) object implementation especially `generate_from_frequencies()` were used to build this ImageCloud
    - [`wordcloud/query_integral_image.pyx`](https://github.com/amueller/word_cloud/blob/main/wordcloud/query_integral_image.pyx) was copied verbatim and used by this ImageCloud's `IntegratedOccupancyMap` object.