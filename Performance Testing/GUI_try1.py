import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import psychrolib

# Setting the unit system for psychrolib
psychrolib.SetUnitSystem(psychrolib.SI)

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Transaera Testing Data Calculation Tool")
        self.prototypes = {
            "Gentoo P1": (0.8, 165),
            "Gentoo P3": (0.9, 150)
            # Add more prototypes as needed
        }
        self.create_widgets()
    
    def create_widgets(self):
        # Main Input File Selection
        tk.Label(self, text="Select Datasheet:").grid(row=0, column=0)
        self.datasheet_entry = tk.Entry(self, width=50)
        self.datasheet_entry.grid(row=0, column=1)
        tk.Button(self, text="Browse", command=self.select_datasheet).grid(row=0, column=2)

        # Control Log Input File Selection
        tk.Label(self, text="Select Control Log Input File:").grid(row=1, column=0)
        self.control_log_input_file_entry = tk.Entry(self, width=50)
        self.control_log_input_file_entry.grid(row=1, column=1)
        tk.Button(self, text="Browse", command=self.select_control_log_input_file).grid(row=1, column=2)
        
        # Output Folder Selection
        tk.Label(self, text="Select Output Folder:").grid(row=2, column=0)
        self.output_folder_entry = tk.Entry(self, width=50)
        self.output_folder_entry.grid(row=2, column=1)
        tk.Button(self, text="Browse", command=self.select_output_folder).grid(row=2, column=2)
        
        # Prototype Selection
        tk.Label(self, text="Prototype:").grid(row=3, column=0)
        self.prototype_var = tk.StringVar()
        self.prototype_dropdown = ttk.Combobox(self, textvariable=self.prototype_var, values=list(self.prototypes.keys()))
        self.prototype_dropdown.grid(row=3, column=1)
        self.prototype_dropdown.current(0)  # Default to first prototype
        
        # Ambient Pressure Entry
        tk.Label(self, text="Ambient Pressure (Pa):").grid(row=4, column=0)
        self.ambient_pressure_entry = tk.Entry(self)
        self.ambient_pressure_entry.grid(row=4, column=1)
        self.ambient_pressure_entry.insert(0, "101325")  # Default value
        
        # Calculate Button
        tk.Button(self, text="Calculate", command=self.on_calculate_clicked).grid(row=5, column=1)

    def prepare_dataframe(self, file_path, time_format='%H:%M:%S', num_cols=None):
        """Prepares and cleans the dataframe from the given file."""
        usecols = list(range(num_cols)) if num_cols else None
        df = pd.read_csv(file_path, delimiter='\t', usecols=usecols, header=None)
        df.iloc[:, 2:] = df.iloc[:, 2:].apply(pd.to_numeric, errors='coerce')
        df['valid_times'] = pd.to_datetime(df.iloc[:, 1], format=time_format, errors='coerce').dt.time
        return df
    
    def select_datasheet(self):
        file_path = filedialog.askopenfilename()
        self.datasheet_entry.delete(0, tk.END)
        self.datasheet_entry.insert(0, file_path)

    def select_control_log_input_file(self):
        file_path = filedialog.askopenfilename()
        self.control_log_input_file_entry.delete(0, tk.END)
        self.control_log_input_file_entry.insert(0, file_path)

    def select_output_folder(self):
        folder_path = filedialog.askdirectory()
        self.output_folder_entry.delete(0, tk.END)
        self.output_folder_entry.insert(0, folder_path)

    def on_calculate_clicked(self):
        input_file = self.datasheet_entry.get()
        control_log_input_file = self.control_log_input_file_entry.get()
        output_folder = self.output_folder_entry.get()
        ambient_pressure = float(self.ambient_pressure_entry.get())
        
        # Preparing and analyzing data
        df = self.prepare_dataframe(input_file)
        
        # Perform additional calculations
        self.perform_calculations(df, ambient_pressure)

        # Save results to output folder
        output_file_path = f"{output_folder}/calculated_results.xlsx"
        df.to_excel(output_file_path, index=False)
        messagebox.showinfo("Info", "Calculation completed and results saved.")

    def prepare_and_analyze_data(self, file_path, ambient_pressure):
        # Placeholder for data preparation and analysis logic
        # Use psychrolib and pandas as needed for your calculations
        # Example: Read CSV, perform calculations, and return the DataFrame
        df = pd.read_csv(file_path)  # Simplified example
        # Perform calculations here using ambient_pressure, psychrolib, etc.
        return df  # This should be your calculated DataFrame


    def perform_calculations(self, df, ambient_pressure):
        # Example: Calculate 'dT[C]'
        df['dT[C]'] = df['T_return'] - df['T_supply']
        # Add further analysis and manipulations here
        
        # Example: Calculate humidity ratios using psychrolib
        psychrolib.SetUnitSystem(psychrolib.SI)
        df['W_U_Inlet'] = df.apply(lambda row: psychrolib.GetHumRatioFromRelHum(row['T_supply'], row['RH_avg'] / 100, ambient_pressure)*1000, axis=1)
        # Continue with other calculations as per your provided logic

    @staticmethod
    def calculate_airflow(fan_speed, coefficient=0.8, intercept=165):
        return fan_speed * coefficient + intercept

if __name__ == "__main__":
    psychrolib.SetUnitSystem(psychrolib.SI)
    app = Application()
    app.mainloop()
