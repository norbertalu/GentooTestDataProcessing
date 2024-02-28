import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
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
        self.prototype_dropdown = ttk.Combobox(self, textvariable=self.prototype_var)
        self.prototype_dropdown.grid(row=3, column=1)
        # Assuming self.prototypes is defined elsewhere
        self.prototype_dropdown['values'] = list(self.prototypes.keys())  
        self.prototype_dropdown.current(0)  # Default to first prototype
        
        # Ambient Pressure Entry
        tk.Label(self, text="Ambient Pressure (Pa):").grid(row=4, column=0)
        self.ambient_pressure_entry = tk.Entry(self)
        self.ambient_pressure_entry.grid(row=4, column=1)
        self.ambient_pressure_entry.insert(0, "101325")  # Default value
        
        # Saved File Name Entry
        tk.Label(self, text="Saved File Name:").grid(row=5, column=0)
        self.saved_file_name_entry  = tk.Entry(self, width=50)
        self.saved_file_name_entry.grid(row=5, column=1)
        self.saved_file_name_entry.insert(0, "")  # Default file name

        # RH Sensor Table
        self.rh_station_positions = ["Process Outlet", "Process Inlet"]  # Add more positions as needed
        self.rh_sensor_names = [f"RH{i}" for i in range(1, 9)]  # RH1 to RH8

        # Create Labels and Dropdowns for each station position
        self.rh_selection_widgets = []
        for i, position in enumerate(self.rh_station_positions, start=6):  # Adjust start index as needed
            tk.Label(self, text=position).grid(row=i, column=0)
            rh_var = tk.StringVar()
            rh_dropdown = ttk.Combobox(self, textvariable=rh_var, values=self.rh_sensor_names)
            rh_dropdown.grid(row=i, column=1)
            # Set default values for the first two positions
            rh_dropdown.current(0 if i == 6 else 1 if i == 7 else 0)
            self.rh_selection_widgets.append((position, rh_var))

        # Calculate Button - Adjusted to be at the bottom
        tk.Button(self, text="Calculate", command=self.on_calculate_clicked).grid(row=8, column=1)  # Adjust row as needed based on your layout


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
    
        saved_file_name = self.saved_file_name_entry.get().strip()
        # Ensure the file name ends with .xlsx
        if not saved_file_name.endswith('.xlsx'):
            saved_file_name += '.xlsx'
        output_file_path = f"{output_folder}/{saved_file_name}"

    
        # Preparing and analyzing data
        df = self.prepare_dataframe(input_file,'%H:%M:%S', num_cols=38)
        new_df = self.prepare_dataframe(control_log_input_file,'%m/%d/%Y %I:%M:%S %p')

        rename_columns = {
            new_df.columns[i]: name for i, name in enumerate([
            'Superheat', 'Subcool', 'Num_Cycles', 'Compressor_En', 'Compressor',
            'Fan_En', 'Process_Fan', 'Regen_Fan', 'EEV', 'Left_Right', 
            'Cooling_Heating', 'Automode_En'], start=24)  # Ensure this starts at the correct index
        }
        new_df = new_df.rename(columns=rename_columns)

        # Ensure columns_to_merge is correctly populated
        columns_to_merge = list(rename_columns.values())
        new_df[columns_to_merge] = new_df[columns_to_merge].apply(pd.to_numeric, errors='coerce')
        # Pass columns_to_merge as an argument
        df = self.merge_dataframes(df, new_df, TIME_THRESHOLD_SECONDS, columns_to_merge)
        df = df.iloc[1:, :] 
        # Creating a single dictionary that includes all new column names
        new_column_names = {**{i: f'AT{i-1}' for i in range(2, 12)},
                            **{i: f'LT{i-11}' for i in range(12, 18)},
                            **{18: 'P1', 19: 'P2'},
                            **{i: f'RH{i-19}' for i in range(20, 28)},
                            **{i: f'W{i-27}' for i in range(28, 36)},
                            **{36: 'kWh', 37: 'Watt'}}

        # Applying all renaming in one operation
        df.rename(columns=new_column_names, inplace=True)
        start_time = df['valid_times'].dropna().iloc[0]
        # Create a new column for time differences
        df['TimeDifference'] = 0.0
        # Iterate over each row and calculate the time difference
        for index, row in df.iterrows():
            current_time = row['valid_times']
            time_difference = (current_time.hour * 3600 + current_time.minute * 60 + current_time.second) - (start_time.hour * 3600 + start_time.minute * 60 + start_time.second)
            df.at[index, 'TimeDifference'] = time_difference / 60

        """
        df['Total_Power'] = df['Watt']
        df['Total_Power'] = pd.to_numeric(df['Total_Power'], errors='coerce')
        # apply airflow
        df['Regen_Fan_Airflow'] = df['Regan_Fan'].apply(self.calculate_airflow(fan_speed=100,coefficient=0.8, intercept=5))
        df['Process_Fan_Airflow_U'] = df['Process_Fan'].apply(self.calculate_airflow)
        df['Process_Fan_Airflow_S'] = df['Process_Fan'].apply(self.calculate_airflow)
        temp_df = df.copy()
        supply_temp = temp_df.columns[5:11]
        df['T_supply'] = temp_df[supply_temp].mean(axis=1)
        df['T_return'] = np.where(df['Left_Right'] == 1, df['AT3'], df['AT1'])
        df['dT[C]'] = df['T_return'] - df['T_supply']
        """
        
        # Save results to output folder
        df.to_excel(output_file_path, index=False)
        messagebox.showinfo("Info", "Calculation completed and results saved.")

    def merge_dataframes(self, df1, df2, time_threshold, columns_to_merge):

        for index, row in df1.iterrows():
            # Calculate time difference in seconds
            time_difference = (df2['valid_times'].apply(lambda x: x.hour * 3600 + x.minute * 60 + x.second) -
                            row['valid_times'].hour * 3600 -
                            row['valid_times'].minute * 60 -
                            row['valid_times'].second)
    
            close_rows = df2[abs(time_difference) <= time_threshold]
    
            if not close_rows.empty:
                selected_columns = close_rows[columns_to_merge]
                for col in columns_to_merge:
                    df1.at[index, col] = selected_columns.iloc[0][col]

        return df1


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
    TIME_THRESHOLD_SECONDS = 10
    app = Application()
    app.mainloop()
