import math
import os

def generate_header():
    return [
        "; GCODE Generated by Python Script",
        "G21 ; mm-mode"
    ]

def initialize_plotter():
    return [
        "G0 F250 X0.0000 Y0.0000"
    ]

def move_to(x, y, feed_rate):
    return [f"G1 F{feed_rate} X{x} Y{y}"]

def generate_swirl_path_vertical(width, height, loops, speed,initial_height):
    gcode = []

    gcode.append(f"G0 F1000 X{initial_height:.4f} Y0.0000")
    gcode.append("G4 P30 ; Pause for 30 seconds for tool loading")


    # Adjust step_y to ensure full coverage across the width
    step_y = width / (loops - 1)  # Adjusted to account for spaces between loops
    
    current_x = initial_height
    current_y = 0
    move_up = True

    # Loop through each swirl
    for i in range(loops):
        # Move vertically (up or down)
        if i > 0:  # Skip the first iteration for vertical movement to start correctly
            current_y += step_y
            # Ensure current_y does not exceed the width boundary
            current_y = min(current_y, width)
            gcode.extend(move_to(current_x, current_y, speed))

        # Alternate between moving up and down
        if move_up:
            current_x = height  # Moving up
            move_up = False
        else:
            current_x = initial_height  # Moving down
            move_up = True
        gcode.extend(move_to(current_x, current_y, speed))

    return gcode


def validate_position_vertical(y, x, max_y=800, max_x=300):
    if x < 0 or x > max_x or y < 0 or y > max_y:
        raise ValueError(f"Path exceeds boundary limits at X:{x}, Y:{y}. Max X:{max_x}, Max Y:{max_y}")

def move_to(x, y, feed_rate):
    validate_position_vertical(x, y)
    return [f"G1 F{feed_rate} X{x:.4f} Y{y:.4f}"]

def main(width, height, speed, loops,initial_height ):
    try:
        gcode = []
        gcode.extend(generate_swirl_path_vertical(width, height, loops, speed,initial_height))

        # Define the output path and filename
        OUTPUT_PATH = 'G-code generator'
        filename = 'gcode trial 1.gcode'

        # Ensure the directory exists
        if not os.path.exists(OUTPUT_PATH):
            os.makedirs(OUTPUT_PATH)

        full_path = os.path.join(OUTPUT_PATH, filename)

        with open(full_path, "w") as file:
            for line in gcode:
                file.write(line + "\n")

        print(f"G-code successfully written to {full_path}")

    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    width = 290
    height = 635
    speed = 250
    loops = 7
    Height_start_point = 70
    main(width, height, speed, loops, Height_start_point)  # Example parameters