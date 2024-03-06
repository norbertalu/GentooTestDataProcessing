import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
import os
import math
from gcode import generate_swirl_path_horizontal
from gcode import validate_position_horizontal
from gcode_vertical import generate_swirl_path_vertical
from gcode_vertical import validate_position_vertical

def select_output_path():
    directory = filedialog.askdirectory()
    if directory:
        output_path_var.set(directory)

def generate_gcode():
    try:
        width = float(width_entry.get())
        height = float(height_entry.get())
        loops = int(loops_entry.get())
        initial_height = float(initial_height_entry.get())

        # Fixed speed
        speed = 250

        path_direction = path_direction_var.get()

        # Choose the correct validation and generation functions
        if path_direction == "Horizontal":
            validate_position = validate_position_horizontal
            generate_swirl_path = generate_swirl_path_horizontal
        else:  # Vertical
            validate_position = validate_position_vertical
            generate_swirl_path = generate_swirl_path_vertical

        # Validate position
        validate_position(initial_height, 0, max_x=width, max_y=height)  # Validate start position

        # Generate G-code
        gcode = generate_swirl_path(width, height, loops, speed, initial_height)

        # Use the selected output path and entered filename
        output_path = output_path_var.get()
        filename = filename_entry.get().strip()
        if not filename:
            filename = "gcode_output.gcode"
        else:
            if not filename.endswith('.gcode'):
                filename += '.gcode'
        full_path = os.path.join(output_path, filename)

        # Write the G-code to a file
        with open(full_path, "w") as file:
            for line in gcode:
                file.write(line + "\n")

        messagebox.showinfo("Success", f"G-code generated successfully and saved to {full_path}")

    except ValueError as e:
        messagebox.showerror("Error", f"Invalid input: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

# Create the main window
root = tk.Tk()
root.title("Transaera G-code Generator")

# Create and place labels and entry widgets
tk.Label(root, text="Width (mm):").grid(row=0, column=0)
width_entry = tk.Entry(root)
width_entry.grid(row=0, column=1)

tk.Label(root, text="Height (mm):").grid(row=1, column=0)
height_entry = tk.Entry(root)
height_entry.grid(row=1, column=1)

# Speed is fixed, so just display it
tk.Label(root, text="Feed Speed (mm/min):").grid(row=2, column=0)
tk.Label(root, text="250 (fixed speed)").grid(row=2, column=1)

tk.Label(root, text="Number of paths:").grid(row=3, column=0)
loops_entry = tk.Entry(root)
loops_entry.grid(row=3, column=1)

# Initial Height
tk.Label(root, text="Initial Height (mm):").grid(row=4, column=0)
initial_height_entry = tk.Entry(root)
initial_height_entry.grid(row=4, column=1)

# Path direction selection placed next to Initial Height on the same row
tk.Label(root, text="Path Direction:").grid(row=5, column=0)
path_direction_var = tk.StringVar()
path_direction_combobox = ttk.Combobox(root, textvariable=path_direction_var, values=["Horizontal", "Vertical"], width=15)
path_direction_combobox.grid(row=5, column=1)
path_direction_combobox.current(0)  # Default to Horizontal

# Output path selection
output_path_var = tk.StringVar()
tk.Button(root, text="Select Output Path", command=select_output_path).grid(row=6, column=0)
output_path_label = tk.Label(root, textvariable=output_path_var)
output_path_label.grid(row=6, column=1, sticky='ew')

# Filename Entry
tk.Label(root, text="Filename:").grid(row=7, column=0)
filename_entry = tk.Entry(root)
filename_entry.grid(row=7, column=1)

# Generate G-code Button
generate_button = tk.Button(root, text="Generate G-code", command=generate_gcode)
generate_button.grid(row=8, column=0, columnspan=4, sticky='ew')

# Start the GUI event loop
root.mainloop()
