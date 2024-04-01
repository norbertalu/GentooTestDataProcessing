import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

def generate_gcode(feedrate, initial_x, hold_up, hold_down, loops, output_path, filename):
    # Generate the G-code
    gcode = []
    try:
        feedrate = float(feedrate)
        initial_x = float(initial_x)
        loops = int(loops)
        hold_up = float(hold_up)
        hold_down = float(hold_down)
    except ValueError:
        messagebox.showerror("Input Error", "Please ensure all inputs are numeric.")
        return
    
    shake_feedrate = feedrate*10
    shake_distance = 5
    shake_up = 146+shake_distance
    shake_down = 146-shake_distance*2

    

    for i in range(loops):
        #gcode.append(f"G1 X{(initial_x + 1)} F{feedrate}")
        #gcode.append(f"G4 P{hold_up}")
        gcode.append(f"G1 X{initial_x} F{feedrate}")  # Initial positioning on the X-axis
        gcode.append(f"G4 P{hold_down}")
        gcode.append(f"G1 X146 F{feedrate}")
        gcode.append(f"G4 P{hold_up}")
        #gcode.append(f"G1 X{initial_x} F{feedrate}")
        #gcode.append(f"G4 P{hold_up}")

        for _ in range(50):
            gcode.append(f"G1 X{shake_up} F{feedrate}")
            gcode.append(f"G1 X{shake_down} F{shake_feedrate}")
            gcode.append(f"G1 Y15 F{shake_feedrate}")
            gcode.append(f"G1 Y0 F{shake_feedrate}")
        

    # Handle the filename and path
    if not filename:
        filename = "gcode_output.gcode"
    else:
        if not filename.endswith('.gcode'):
            filename += '.gcode'
    full_path = os.path.join(output_path, filename)

    # Write G-code to the file
    try:
        with open(full_path, 'w') as file:
            for line in gcode:
                file.write(f"{line}\n")
        messagebox.showinfo("Success", f"G-code generated successfully and saved to {full_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save the file: {e}")

def ask_output_path():
    output_path = filedialog.askdirectory()
    if output_path:
        output_path_var.set(output_path)

def on_start_clicked():
    feedrate = feedrate_entry.get()
    initial_x = initial_x_entry.get()
    hold_up = hold_up_entry.get()
    hold_down = hold_down_entry.get()
    loops = loops_entry.get()
    output_path = output_path_var.get()
    filename = filename_entry.get().strip()

    try:
        initial_x_val = float(initial_x)
        if initial_x_val < 45:
            messagebox.showerror("Input Error", "Initial Height must be at least 45.")
            return
    except ValueError:
        messagebox.showerror("Input Error", "Please ensure all inputs are numeric.")
        return

    generate_gcode(feedrate, initial_x, hold_up, hold_down, loops, output_path, filename)

root = tk.Tk()
root.title("G-code Generator for Motor Control")

output_path_var = tk.StringVar()

# Define and arrange widgets
widgets = [
    ("Feedrate(mm/min):", ttk.Entry(root)),
    ("Initial Height(mm):", ttk.Entry(root)),
    ("Hold Up Time (s):", ttk.Entry(root)),
    ("Hold Down Time (s):", ttk.Entry(root)),
    ("Number of Loops:", ttk.Entry(root)),
    ("Output Path:", ttk.Entry(root, textvariable=output_path_var, state="readonly")),
    ("Filename:", ttk.Entry(root)),
]

for i, (label, widget) in enumerate(widgets):
    ttk.Label(root, text=label).grid(row=i, column=0, pady=(10, 0), sticky="e")
    widget.grid(row=i, column=1, pady=(10, 0), sticky="ew")
    if label == "Output Path:":
        ttk.Button(root, text="Browse", command=ask_output_path).grid(row=i, column=2, pady=(10, 0), padx=(5, 0))

feedrate_entry, initial_x_entry, hold_up_entry, hold_down_entry, loops_entry, _, filename_entry = (widget for _, widget in widgets)
feedrate_entry.insert(0, "255")  # Insert the default feedrate value
initial_x_entry.insert(0, "45")
# Start button
start_button = ttk.Button(root, text="Start", command=on_start_clicked)
start_button.grid(row=len(widgets), column=0, columnspan=3, pady=(10, 0))

root.mainloop()
