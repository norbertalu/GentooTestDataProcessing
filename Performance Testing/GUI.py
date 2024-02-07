import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox

root = tk.Tk()
root.title("Airflow Calculation Tool")

# Dictionary of prototypes
prototypes = {
    "Gentoo P1": (0.8, 165),
    "Gentoo P3": (0.9, 150),
    # ... add more prototypes as needed
}

# Function to handle the airflow calculation
def calculate_airflow(fan_speed, prototype_name):
    coefficient, intercept = prototypes[prototype_name]
    return fan_speed * coefficient + intercept
def select_input_file():
    file_path = filedialog.askopenfilename()
    input_file_entry.delete(0, tk.END)
    input_file_entry.insert(0, file_path)

def select_output_folder():
    folder_path = filedialog.askdirectory()
    output_folder_entry.delete(0, tk.END)
    output_folder_entry.insert(0, folder_path)

# Input file selection
tk.Label(root, text="Select Input File:").grid(row=0, column=0)
input_file_entry = tk.Entry(root, width=50)
input_file_entry.grid(row=0, column=1)
tk.Button(root, text="Browse", command=select_input_file).grid(row=0, column=2)

# Output folder selection
tk.Label(root, text="Select Output Folder:").grid(row=1, column=0)
output_folder_entry = tk.Entry(root, width=50)
output_folder_entry.grid(row=1, column=1)
tk.Button(root, text="Browse", command=select_output_folder).grid(row=1, column=2)

# Output file name
tk.Label(root, text="Output File Name:").grid(row=2, column=0)
output_file_name_entry = tk.Entry(root)
output_file_name_entry.grid(row=2, column=1)

# Dropdown for Regen_Fan
regen_prototype_var = tk.StringVar()
regen_prototype_dropdown = ttk.Combobox(root, textvariable=regen_prototype_var, values=list(prototypes.keys()))
regen_prototype_dropdown.grid(row=3, column=1)
regen_prototype_dropdown.current(0)  # Default selection
tk.Label(root, text="Prototype:").grid(row=3, column=0)
# ambient pressure
tk.Label(root, text="Ambient Pressure (Pa):").grid(row=4, column=0)
ambient_pressure_entry = tk.Entry(root)
ambient_pressure_entry.grid(row=4, column=1)
ambient_pressure_entry.insert(0, "101325")  # Default value for standard atmospheric pressure


def on_calculate_clicked():
    # Implement the logic to read data, perform calculations, and save output
    # This should include reading the input file, applying the calculate_airflow function
    # and writing the results to the output file in the selected output folder
    ambient_pressure = float(ambient_pressure_entry.get())
    messagebox.showinfo("Info", "Calculation completed.")

# Calculate button
calculate_button = tk.Button(root, text="Get resule", command=on_calculate_clicked)
calculate_button.grid(row=5, column=1)

root.mainloop()
