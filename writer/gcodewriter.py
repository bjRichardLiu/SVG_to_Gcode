"""
Handles common G-code operations for a Bambu Lab Printers

First Version: 09/06/2024

Author: Richard (Ruichen Liu)
Last Modified: 03/17/2025
"""
import os
import json
import math

pen_up_z = 0
x_offset = 0
y_offset = 0
z_offset = 0
x_max = 0
y_max = 0
x_min = 0
y_min = 0
z_speed = 10
nozzle_size = 0.4
layer_height = 0.2
filament_diameter = 1.75
filament_flow_rate = 1.0
filament_temprature = 200
bed_temperature = 50

with open('config/config.json') as f:
    config = json.load(f)
    x_offset = config['X_OFFSET']
    y_offset = config['Y_OFFSET']
    z_offset = config['Z_OFFSET']
    x_max = config['X_MAX']
    y_max = config['Y_MAX']
    x_min = config['X_MIN']
    y_min = config['Y_MIN']
    z_speed = config['Z_SPEED']
    G0_speed = config['G0_SPEED']
    G1_speed = config['G1_SPEED']
    start_gcode = config['START_GCODE']
    end_gcode = config['END_GCODE']
    nozzle_size = config['NOZZLE_SIZE']
    layer_height = config['LAYER_HEIGHT']
    filament_diameter = config['FILAMENT_DIAMETER']
    filament_flow_rate = config['FILAMENT_FLOW_RATE']
    filament_temprature = config['FILAMENT_TEMPERATURE']
    bed_temperature = config['BED_TEMPERATURE']
    

def startGcode():
    """
    Returns the start G-code.

    Returns:
        str: The start G-code.
    """
    return start_gcode

def endGcode():
    """
    Returns the end G-code.

    Returns:
        str: The end G-code.
    """
    return end_gcode

def setNozzleTemp(temp=filament_temprature):
    """
    Returns the G-code to set the nozzle temperature.

    Args:
        temp (int): The temperature to set the nozzle to.

    Returns:
        str: The G-code to set the nozzle temperature.
    """
    return "M104 S" + str(temp) + "\n"

def setBedTemp(temp=bed_temperature):
    """
    Returns the G-code to set the bed temperature.

    Args:
        temp (int): The temperature to set the bed to.

    Returns:
        str: The G-code to set the bed temperature.
    """
    return "M140 S" + str(temp) + "\n"

def fanOff():
    """
    Returns the G-code to turn the fan off.

    Returns:
        str: The G-code to turn the fan off.
    """
    return "M106 P1 S0\n"

def fanOn():
    """
    Returns the G-code to turn the fan on.

    Returns:
        str: The G-code to turn the fan on.
    """
    return "M106 P1 S255\n"

def progressGcode(percentage, time):
    """
    Returns the G-code to update the progress.

    Args:
        percentage (int): The percentage of the progress.
        time (int): The remaining time.

    Returns:
        str: The G-code to update the progress.
    """
    return "M73 P" + str(percentage) + " R" + str(time) + "\n\n"

def G0_Z(z):
    """
    Returns the G-code to move the machine to a given z-coordinate.

    Args:
        z (float): The z-coordinate of the position.

    Returns:
        str: The G-code to move the machine to the given z-coordinate.
    """
    z += z_offset
    return "G0 Z" + str(z) + "\n"

def G0(x, y, z=0, speed=G0_speed, e=0):
    """
    Returns the G-code to move the machine to a given position.

    Args:
        x (float): The x-coordinate of the position.
        y (float): The y-coordinate of the position.
        z (float): The z-coordinate of the position.
        speed (int): The speed of the movement.
        e (float): The E value for the movement, default is retracted by 0mm.

    Returns:
        str: The G-code to move the machine to the given position.
    """
    x += x_offset
    y += y_offset
    # if z != 0:
    #     z += z_offset
    #     return "G0 X" + str(x) + " Y" + str(y) + " Z" + str(z) + " E" + str(e) + " F" + str(speed) + "\n"
    # else:
    #     return "\n" + "G1 X" + str(x) + " Y" + str(y) + " E" + str(e) + " F" + str(speed)
    if e != 0:
        return "G0 X" + str(x) + " Y" + str(y) + " E" + str(e) + " F" + str(speed) + "\n"
    return "G0 X" + str(x) + " Y" + str(y) + " F" + str(speed) + "\n"

def G1(x, y, prev_x=None, prev_y=None, travel=False, z=0, prev_z=0, speed=G1_speed):
    """
    Returns the G-code to draw a line to a given position.

    Args:
        x (float): The x-coordinate of the position.
        y (float): The y-coordinate of the position.
        prev_x (float): The previous x-coordinate.
        prev_y (float): The previous y-coordinate.
        travel (bool): Whether the movement is a travel move (no extrusion).
        z (float): The z-coordinate of the position.
        prev_z (float): The previous z-coordinate.
        speed (int): The speed of the movement.

    Returns:
        str: The G-code to draw a line to the given position.
    """
    if prev_x is None or prev_y is None:
        travel = True
    
    if travel:
        if z != 0:
            z += z_offset
            return "G1" + " X" + str(x) + " Y" + str(y) + " Z" + str(z) + " F" + str(speed) + "\n"
        else:
            return "G1" + " X" + str(x) + " Y" + str(y) + " F" + str(speed) + "\n"
    
    distance = ((x - prev_x)**2 + (y - prev_y)**2)**0.5
    if z != 0:
        distance = ((x - prev_x)**2 + (y - prev_y)**2 + (z - prev_z)**2)**0.5
    # Calculate the E value based on the distance and filament flow rate
    volume = distance * layer_height * nozzle_size
    e = volume / (3.14159 * (filament_diameter / 2)**2) * filament_flow_rate
    
    x += x_offset
    y += y_offset
    
    if z != 0:
        z += z_offset
        return "G1" + " X" + str(x) + " Y" + str(y) + " Z" + str(z) + " E" + str(e) + " F" + str(speed) + "\n"
    else:
        return "G1" + " X" + str(x) + " Y" + str(y) + " E" + str(e) + " F" + str(speed) + "\n"


# TODO: Able to calculate distance for these
def G2(x, y, prev_x, prev_y, x_offset_I, y_offset_J, speed=G1_speed):
    """
    Returns the G-code to draw a clockwise arc to a given position.
    
    Args:
        x (float): The x-coordinate of the end position.
        y (float): The y-coordinate of the end position.
        prev_x (float): The previous x-coordinate.
        prev_y (float): The previous y-coordinate.
        x_offset_I (float): The x offset of the arc.
        y_offset_J (float): The y offset of the arc.
        radius (float): The radius of the arc.
        speed (int): The speed of the movement.
    Returns:
        str: The G-code to draw a clockwise arc to the given position.
    """
    # Calculate arc center
    center_x = prev_x + x_offset_I
    center_y = prev_y + y_offset_J
    
    # Calculate radius based on the offset values
    radius = math.sqrt(x_offset_I**2 + y_offset_J**2)
    
    # Calculate angles between center and points
    start_angle = math.atan2(prev_y - center_y, prev_x - center_x)
    end_angle = math.atan2(y - center_y, x - center_x)
    
    # Adjust for clockwise motion (G2)
    if end_angle > start_angle:
        end_angle -= 2 * math.pi
    
    # Calculate the angle difference (negative for clockwise)
    angle_diff = end_angle - start_angle
    
    # Calculate arc length
    arc_length = abs(angle_diff) * radius
    
    # Calculate extrusion amount based on arc length
    extrusion = arc_length * e_per_mm
    
    x += x_offset
    y += y_offset
    x_offset_I += x_offset
    y_offset_J += y_offset
    return "F" + str(speed) + "\n" + "G2" + " X" + str(x) + " Y" + str(y) + " I" + str(x_offset_I) + " J" + str(y_offset_J) + " E" + str(e) + "\n"

def G3(x, y, x_offset_I, y_offset_J, speed=G1_speed, e=0):
    """
    Returns the G-code to draw a counterclockwise arc to a given position.
    
    Args:
        x (float): The x-coordinate of the end position.
        y (float): The y-coordinate of the end position.
        x_offset_I (float): The x offset of the arc.
        y_offset_J (float): The y offset of the arc.
        radius (float): The radius of the arc.
        speed (int): The speed of the movement.
    Returns:
        str: The G-code to draw a clockwise arc to the given position.
    """
    x += x_offset
    y += y_offset
    x_offset_I += x_offset
    y_offset_J += y_offset
    return "F" + str(speed) + "\n" + "G3" + " X" + str(x) + " Y" + str(y) + " I" + str(x_offset_I) + " J" + str(y_offset_J) + " E" + str(e) + "\n"

def G5(x, y, x_offset_1, y_offset_1, x_offset_2, y_offset_2, speed=G1_speed, e=0):
    """
    Returns the G-code to draw a cubic Bezier curve to a given position.
    
    Args:
        x (float): The x-coordinate of the end position.
        y (float): The y-coordinate of the end position.
        x_offset_1 (float): The x offset of the first control point.
        y_offset_1 (float): The y offset of the first control point.
        x_offset_2 (float): The x offset of the second control point.
        y_offset_2 (float): The y offset of the second control point.
        speed (int): The speed of the movement.
    Returns:
        str: The G-code to draw a cubic Bezier curve to the given position.
    """
    x += x_offset
    y += y_offset
    x_offset_1 += x_offset
    y_offset_1 += y_offset
    x_offset_2 += x_offset
    y_offset_2 += y_offset
    return "F" + str(speed) + "\n" + "G5" + " X" + str(x) + " Y" + str(y) + " I" + str(x_offset_1) + " J" + str(y_offset_1) + " P" + str(x_offset_2) + " Q" + str(y_offset_2) + " E" + str(e) + "\n"


def wait(wait_time):
    """
    Returns the G-code to wait for a given amount of time.

    Args:
        wait_time (int): The amount of time to wait.

    Returns:
        str: The G-code to wait for the given amount of time.
    """
    return "G4 S" + str(wait_time) + "\n"

def pauseGcode():
    """
    Returns the G-code to pause the machine.

    Returns:
        str: The G-code to pause the machine.
    """
    return "M400 U1\n"