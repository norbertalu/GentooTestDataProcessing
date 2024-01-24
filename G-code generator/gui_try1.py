import tkinter as tk
from tkinter import messagebox
import os
from gcode import generate_swirl_path

def generate_gcode():
    try:
        width = float(width_entry.get())
        height = float(height_entry.get())
        speed = 250
        loops = int(loops_entry.get())
        x_start_threshold = float(x_start_threshold_entry.get())

        # Generate G-code
        gcode = generate_swirl_path(width, height, loops, speed, x_start_threshold)

        # Define the output path and filename
        OUTPUT_PATH = 'G-code generator'
        filename = 'gcode_trial_1.gcode'

        # Ensure the directory exists
        if not os.path.exists(OUTPUT_PATH):
            os.makedirs(OUTPUT_PATH)

        full_path = os.path.join(OUTPUT_PATH, filename)

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
root.title("G-code Generator")

# Create and place labels and entry widgets
tk.Label(root, text="Width:").grid(row=0, column=0)
width_entry = tk.Entry(root)
width_entry.grid(row=0, column=1)

tk.Label(root, text="Height:").grid(row=1, column=0)
height_entry = tk.Entry(root)
height_entry.grid(row=1, column=1)

# Speed is fixed, so just display it
tk.Label(root, text="Speed:").grid(row=2, column=0)
tk.Label(root, text="250 (fixed)").grid(row=2, column=1)


tk.Label(root, text="Loops:").grid(row=3, column=0)
loops_entry = tk.Entry(root)
loops_entry.grid(row=3, column=1)

tk.Label(root, text="X-axis Start Threshold:").grid(row=4, column=0)
x_start_threshold_entry = tk.Entry(root)
x_start_threshold_entry.grid(row=4, column=1)

# Create and place the generate button
generate_button = tk.Button(root, text="Generate G-code", command=generate_gcode)
generate_button.grid(row=5, column=0, columnspan=2)

# Start the GUI event loop
root.mainloop()
