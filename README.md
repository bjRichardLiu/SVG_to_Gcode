# SVG_to_Gcode
A script to convert a SVG to Gcode for 3D Printing

# How to use
1. Place your SVG file in the same directory as `svg_to_gcode.py`.
2. Modify the `svg_file` variable in the script to point to your SVG file.
3. Run the script using Python 3: `python svg_to_gcode.py`.
4. The generated Gcode will be saved in the same directory with a `.gcode` extension.

Note: The default start and finish Gcode and config are set for Bambu Lab A1 mini, for other printers, just slice a model in the default slicer, export the Gcode, and copy the start and finish Gcode to replace the default ones in the script.

# Parameters
- svg_file: Path to the input SVG file.
- layer_num: Number of layers to print.
- size: Size of the output in mm.
- start_x: Starting X coordinate offset.
- start_y: Starting Y coordinate offset.
- layer_height: Height of each layer.
- debug: Enable debug mode for visualization and more detailed output.
