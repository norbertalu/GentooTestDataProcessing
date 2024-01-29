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

def generate_swirl_path(width, height, loops, speed,initial_height):
    gcode = []

    gcode.append(f"G0 F1000 X{initial_height:.4f} Y0.0000")
    gcode.append("G4 P30 ; Pause for 30 seconds for tool loading")

    step_x = height / (loops)
    current_x = initial_height
    current_y = 0
    move_right = True

    first_iteration = True

    for i in range(loops):
        # Move vertically (up or down)
        #direction = 1 if i % 2 == 0 else -1
        if not first_iteration:
            current_x += step_x
            gcode.extend(move_to(current_x, current_y, speed))
        
        if first_iteration:
            gcode.extend(move_to(current_x, current_y, speed))

        # If moving right, go all the way to the maximum Y value
        if move_right:
            current_y = width
            gcode.extend(move_to(current_x, current_y, speed))
            move_right = False
        else:
            current_y = 0
            gcode.extend(move_to(current_x, current_y, speed))
            move_right = True
        first_iteration = False
    # After the last loop, return to home position (0,0)
    #gcode.extend(move_to(initial_height, 0, speed))

    return gcode


def validate_position(x, y, max_x=800, max_y=300):
    if x < 0 or x > max_x or y < 0 or y > max_y:
        raise ValueError(f"Path exceeds boundary limits at X:{x}, Y:{y}. Max X:{max_x}, Max Y:{max_y}")

def move_to(x, y, feed_rate):
    validate_position(x, y)
    return [f"G1 F{feed_rate} X{x:.4f} Y{y:.4f}"]

def main(width, height, speed, loops,initial_height ):
    try:
        gcode = []
        gcode.extend(generate_swirl_path(width, height, loops, speed,initial_height))

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
    width = 300
    height = 420
    speed = 250
    loops = 10
    Height_start_point = 30
    main(width, height, speed, loops, Height_start_point)  # Example parameters