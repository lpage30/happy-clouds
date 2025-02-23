# ItemCloud
A generic item intended to be used to create an image or text/word or 'other' cloud image based on weights

### Motivation
In constructing an ImageCloud based on WordCloud functionality it was clear most of the functionality could be abstracted out and operated on without knowing the data that is to be rendered.   

- all data has a concept of a bounding box
- all data has a concept of a weight associated with it
- ignoring the data type, and you have to fit/place weighted bounding boxes in a single image
- ItemCloud basically creates a single image collage of weighted bounding boxes or weighted items

## Abstract classes:
- itemcloud.layout.layout_item
    - see example implementation of this at imagecloud.layout.layout_image.py
- itemcloud.containers.named_item
    - example implementation of this at objectcloud.containers.named_image.py
- itemcloud.containers.weighted_item
    - example implementation of this at imagecloud.containers.weighted_image.py

## Usage
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
