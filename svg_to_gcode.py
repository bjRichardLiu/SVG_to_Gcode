from xml.dom import minidom
import re
from writer.gcodewriter import *


def parse_svg_path(path_data):
    """
    Parse SVG path data and return a list of (x, y) coordinates.
    Supports M (moveto), L (lineto), H (horizontal), V (vertical), C (cubic bezier), 
    Q (quadratic bezier), A (arc), and Z (closepath) commands.
    """
    print(f"\n=== Parsing path data ===")
    print(f"Raw path data: {path_data[:200]}...")  # Print first 200 chars
    
    points = []
    # Better regex to handle commands with optional whitespace and commas
    commands = re.findall(r'[MLHVZCSQTAmlhvzcsqta][^MLHVZCSQTAmlhvzcsqta]*', path_data)
    
    print(f"Found {len(commands)} commands: {[c[0] for c in commands]}")
    
    current_x = 0
    current_y = 0
    path_start_x = 0
    path_start_y = 0
    
    for cmd_idx, cmd in enumerate(commands):
        cmd_type = cmd[0]
        # Better number extraction - handles scientific notation and negative numbers
        params_str = cmd[1:].strip()
        params = re.findall(r'-?\d*\.?\d+(?:[eE][+-]?\d+)?', params_str)
        params = [float(p) for p in params if p]
        
        print(f"Command {cmd_idx}: '{cmd_type}' with params: {params}")
        
        if cmd_type == 'M':  # Absolute moveto
            if len(params) >= 2:
                current_x = params[0]
                current_y = params[1]
                path_start_x = current_x
                path_start_y = current_y
                points.append(('move', current_x, current_y))
                # Subsequent coordinate pairs are treated as lineto
                for i in range(2, len(params), 2):
                    if i + 1 < len(params):
                        current_x = params[i]
                        current_y = params[i + 1]
                        points.append(('line', current_x, current_y))
            
        elif cmd_type == 'm':  # Relative moveto
            if len(params) >= 2:
                current_x += params[0]
                current_y += params[1]
                path_start_x = current_x
                path_start_y = current_y
                points.append(('move', current_x, current_y))
                # Subsequent coordinate pairs are treated as relative lineto
                for i in range(2, len(params), 2):
                    if i + 1 < len(params):
                        current_x += params[i]
                        current_y += params[i + 1]
                        points.append(('line', current_x, current_y))
            
        elif cmd_type == 'L':  # Absolute lineto
            for i in range(0, len(params), 2):
                if i + 1 < len(params):
                    current_x = params[i]
                    current_y = params[i + 1]
                    points.append(('line', current_x, current_y))
                
        elif cmd_type == 'l':  # Relative lineto
            for i in range(0, len(params), 2):
                if i + 1 < len(params):
                    current_x += params[i]
                    current_y += params[i + 1]
                    points.append(('line', current_x, current_y))
                
        elif cmd_type == 'H':  # Absolute horizontal lineto
            for param in params:
                current_x = param
                points.append(('line', current_x, current_y))
                
        elif cmd_type == 'h':  # Relative horizontal lineto
            for param in params:
                current_x += param
                points.append(('line', current_x, current_y))
                
        elif cmd_type == 'V':  # Absolute vertical lineto
            for param in params:
                current_y = param
                points.append(('line', current_x, current_y))
                
        elif cmd_type == 'v':  # Relative vertical lineto
            for param in params:
                current_y += param
                points.append(('line', current_x, current_y))
        
        elif cmd_type == 'C':  # Absolute cubic Bezier curve
            # C x1 y1, x2 y2, x y - we'll just use the endpoint for now
            for i in range(0, len(params), 6):
                if i + 5 < len(params):
                    current_x = params[i + 4]
                    current_y = params[i + 5]
                    points.append(('line', current_x, current_y))
        
        elif cmd_type == 'c':  # Relative cubic Bezier curve
            for i in range(0, len(params), 6):
                if i + 5 < len(params):
                    current_x += params[i + 4]
                    current_y += params[i + 5]
                    points.append(('line', current_x, current_y))
        
        elif cmd_type == 'S':  # Absolute smooth cubic Bezier
            for i in range(0, len(params), 4):
                if i + 3 < len(params):
                    current_x = params[i + 2]
                    current_y = params[i + 3]
                    points.append(('line', current_x, current_y))
        
        elif cmd_type == 's':  # Relative smooth cubic Bezier
            for i in range(0, len(params), 4):
                if i + 3 < len(params):
                    current_x += params[i + 2]
                    current_y += params[i + 3]
                    points.append(('line', current_x, current_y))
        
        elif cmd_type == 'Q':  # Absolute quadratic Bezier
            for i in range(0, len(params), 4):
                if i + 3 < len(params):
                    current_x = params[i + 2]
                    current_y = params[i + 3]
                    points.append(('line', current_x, current_y))
        
        elif cmd_type == 'q':  # Relative quadratic Bezier
            for i in range(0, len(params), 4):
                if i + 3 < len(params):
                    current_x += params[i + 2]
                    current_y += params[i + 3]
                    points.append(('line', current_x, current_y))
        
        elif cmd_type == 'A' or cmd_type == 'a':  # Arc (simplified to just use endpoint)
            # A rx ry x-axis-rotation large-arc-flag sweep-flag x y
            for i in range(0, len(params), 7):
                if i + 6 < len(params):
                    if cmd_type == 'A':
                        current_x = params[i + 5]
                        current_y = params[i + 6]
                    else:
                        current_x += params[i + 5]
                        current_y += params[i + 6]
                    points.append(('line', current_x, current_y))
                
        elif cmd_type in ['Z', 'z']:  # Close path
            if (current_x, current_y) != (path_start_x, path_start_y):
                points.append(('line', path_start_x, path_start_y))
    
    print(f"Parsed {len(points)} points")
    return points


def extract_paths_from_svg(svg_file):
    """
    Extract all path elements from an SVG file.
    Returns a list of parsed path data.
    """
    doc = minidom.parse(svg_file)
    path_elements = doc.getElementsByTagName('path')
    
    all_paths = []
    for path in path_elements:
        path_data = path.getAttribute('d')
        if path_data:
            points = parse_svg_path(path_data)
            all_paths.append(points)
    
    return all_paths


def normalize_svg_coordinates(paths, target_size=60):
    """
    Normalize SVG coordinates to fit within target_size.
    SVG coordinates often start from 0,0 and can be in various scales.
    """
    if not paths or not any(paths):
        return paths
    
    # Find bounding box
    all_x = []
    all_y = []
    for path in paths:
        for point in path:
            all_x.append(point[1])
            all_y.append(point[2])
    
    min_x = min(all_x)
    max_x = max(all_x)
    min_y = min(all_y)
    max_y = max(all_y)
    
    svg_width = max_x - min_x
    svg_height = max_y - min_y
    
    if svg_width == 0 or svg_height == 0:
        return paths
    
    # Calculate scale to fit within target_size
    scale = target_size / max(svg_width, svg_height)
    
    # Normalize paths
    normalized_paths = []
    for path in paths:
        normalized_path = []
        for point in path:
            cmd_type = point[0]
            x = (point[1] - min_x) * scale
            y = (point[2] - min_y) * scale
            normalized_path.append((cmd_type, x, y))
        normalized_paths.append(normalized_path)
    
    return normalized_paths


def layer_change_block_full(layer_idx, z_height, total_layers, layer_height,
                            wipe=False, object_id=0,
                            retract_e=0.8, prime_e=0.8):
    """
    Full-featured layer-change block with wipe, arc move, object ID, etc.
    layer_idx: 0-based
    """
    one_based = layer_idx + 1
    lines = []
    lines.append("; CHANGE_LAYER")
    lines.append(f"; Z_HEIGHT: {z_height:.3f}")
    lines.append(f"; LAYER_HEIGHT: {layer_height:.3f}")

    if wipe:
        lines.append("; WIPE_START")
        lines.append("G1 X-13.5 Y0 Z10 F10000")
        lines.append("; WIPE_END")
        lines.append("G1 E-.04 F1800")
    else:
        lines.append(f"G1 E-{retract_e} F1800")

    lines.append(f"; layer num/total_layer_count: {one_based}/{total_layers}")
    lines.append("; update layer progress")
    lines.append(f"M73 L{one_based}")
    lines.append(f"M991 S0 P{layer_idx} ;notify layer change")

    lines.append(f"; OBJECT_ID: {object_id}")
    lines.append("M204 S10000")
    lines.append("G17")
    lines.append("G1 Z" + str(z_height) + " F300")
    lines.append(f"G1 E{prime_e} F1800")

    lines.append("; FEATURE: Inner wall")
    lines.append("; LINE_WIDTH: 0.45")

    return "\n".join(lines) + "\n"


def visualize_svg_paths(svg_paths, title="SVG Paths Visualization"):
    """
    Visualize parsed SVG paths using matplotlib.
    """
    import matplotlib.pyplot as plt
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    
    # Plot raw parsed paths
    for i, path in enumerate(svg_paths):
        x_coords = []
        y_coords = []
        
        for point in path:
            x_coords.append(point[1])
            y_coords.append(point[2])
        
        if x_coords and y_coords:
            ax1.plot(x_coords, y_coords, marker='o', markersize=3, linewidth=1.5, label=f'Path {i+1}')
            # Mark start point
            ax1.plot(x_coords[0], y_coords[0], 'go', markersize=8, label=f'Start {i+1}' if i == 0 else '')
    
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_title('Raw Parsed Paths')
    ax1.grid(True, alpha=0.3)
    ax1.axis('equal')
    ax1.legend()
    ax1.invert_yaxis()  # SVG has Y increasing downward
    
    # Plot normalized paths
    normalized = normalize_svg_coordinates(svg_paths, target_size=60)
    for i, path in enumerate(normalized):
        x_coords = []
        y_coords = []
        
        for point in path:
            x_coords.append(point[1])
            y_coords.append(point[2])
        
        if x_coords and y_coords:
            ax2.plot(x_coords, y_coords, marker='o', markersize=3, linewidth=1.5, label=f'Path {i+1}')
            # Mark start point
            ax2.plot(x_coords[0], y_coords[0], 'go', markersize=8)
    
    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    ax2.set_title('Normalized Paths (60mm)')
    ax2.grid(True, alpha=0.3)
    ax2.axis('equal')
    ax2.legend()
    ax2.invert_yaxis()  # Keep Y inverted for SVG convention
    
    plt.tight_layout()
    plt.savefig('svg_debug_visualization.png', dpi=150)
    print("Visualization saved as 'svg_debug_visualization.png'")
    plt.show()


def main():
    # Configuration
    svg_file = "bakery.svg"  # Change to your SVG file path
    layer_num = 20  # Number of layers
    size = 60  # Size of the output in mm
    start_x = 40  # Starting X coordinate offset
    start_y = 40  # Starting Y coordinate offset
    layer_height = 0.2  # Height of each layer
    
    # Parse SVG
    print(f"Parsing SVG file: {svg_file}")
    svg_paths = extract_paths_from_svg(svg_file)
    
    print(f"Found {len(svg_paths)} paths in SVG")
    
    # Debug: Print first few points of each path
    for i, path in enumerate(svg_paths):
        print(f"\nPath {i+1}: {len(path)} points")
        print(f"  First 5 points: {path[:5]}")
    
    # Visualize the paths
    visualize_svg_paths(svg_paths)
    
    # Ask user if they want to continue to G-code generation
    response = input("\nDoes the visualization look correct? Continue to G-code generation? (y/n): ")
    if response.lower() != 'y':
        print("Stopping. Please fix the SVG parsing first.")
        return
    
    gcode = ""
    
    # Read start gcode
    try:
        with open("config/a1m_start.gcode", "r") as file:
            start_gcode = file.read()
            gcode += start_gcode
    except FileNotFoundError:
        print("Warning: Start gcode file not found, skipping...")
        gcode += "; Start GCode\n"
        gcode += "G28 ; Home all axes\n"
        gcode += "G90 ; Absolute positioning\n"
    
    # Normalize coordinates
    svg_paths = normalize_svg_coordinates(svg_paths, target_size=size)
    
    prev_x = 0
    prev_y = 0
    gcode += G0(0, 0)  # Initial position
    gcode += "\n; Begin SVG Print\n"
    gcode += "; ==================\n"
    # Generate G-code for each layer
    for layer in range(layer_num):
        z_height = layer * layer_height + layer_height
        
        # Add layer change block
        gcode += layer_change_block_full(
            layer_idx=layer,
            z_height=z_height,
            total_layers=layer_num,
            layer_height=layer_height,
            wipe=False
        )
        
        # Process each path in the SVG
        for path in svg_paths:
            
            for point in path:
                cmd_type, x, y = point
                # Apply offset
                x += start_x
                y += start_y
                
                if cmd_type == 'move':
                    # Move without extrusion (travel move)
                    gcode += G0(x, y)
                    prev_x = x
                    prev_y = y
                    
                elif cmd_type == 'line':
                    # Draw line with extrusion
                    gcode += G1(x, y, prev_x=prev_x, prev_y=prev_y)
                    prev_x = x
                    prev_y = y
        
        gcode += "\n"
    
    # Read end gcode
    try:
        with open("config/a1m_end.gcode", "r") as file:
            end_gcode = file.read()
            gcode += end_gcode
    except FileNotFoundError:
        print("Warning: End gcode file not found, using default...")
        gcode += "; End GCode\n"
        gcode += "G28 X Y ; Home X and Y\n"
        gcode += "M104 S0 ; Turn off extruder\n"
        gcode += "M140 S0 ; Turn off bed\n"
        gcode += "M84 ; Disable motors\n"
    
    # Write the G-code to a file
    with open("output.gcode", "w") as file:
        file.write(gcode)
    
    print(f"G-code successfully written to output.gcode")
    print(f"Total layers: {layer_num}")


if __name__ == "__main__":
    main()