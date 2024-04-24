import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel, Label
import pandas as pd
import numpy as np
import psychrolib
import matplotlib.pyplot as plt
import math
import os
from PIL import Image, ImageTk


# Setting the unit system for psychrolib
# Must set this before run code!
psychrolib.SetUnitSystem(psychrolib.SI)

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Transaera Testing Data Calculation Tool")
        self.prototypes = {
            "Gentoo P1": {"regen": (0.8, 165), "process_s": (0.6, 189),"process_u": (0.7, 189)},
            "Gentoo P2": {"regen": (0.9, 150), "process_s": (0.7, 175),"process_u": (0.8, 189)},
            # Add more prototypes as needed
        }
        self.create_widgets()
        self.load_last_selections()
    
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
        self.prototype_dropdown['values'] = list(self.prototypes.keys())  
        self.prototype_dropdown.current(0)  # Default to first prototype

        # Binding the selection event
        self.prototype_dropdown.bind("<<ComboboxSelected>>", self.prototype_selected)

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

        tk.Label(self, text="Select Plots:").grid(row=9, column=0)
        self.plot_selection_listbox = tk.Listbox(self, selectmode='multiple', height=10)
        self.plot_selection_listbox.grid(row=9, column=1, columnspan=2, sticky='ew')
    
        # Populate the Listbox with plot options
        
        plot_options = ["Plot of Time Difference vs AT3", "Plot of Time vs Power", 
                    "Plot of Time vs Total Cooling", "Plot of Time vs EER", 
                    "Plot of Time vs Latent Capacity", "Plot of Time vs Sensible Capacity","Plot of Time vs COP"]
        for option in plot_options:
            self.plot_selection_listbox.insert(tk.END, option)
    
        # Adjust the Calculate button row
        tk.Button(self, text="Calculate", command=self.on_calculate_clicked).grid(row=10, column=1)

        tk.Label(self, text="Replot Start Time (Minute):").grid(row=11, column=0)
        self.replot_start_time_entry = tk.Entry(self)
        self.replot_start_time_entry.grid(row=11, column=1)

        tk.Label(self, text="Replot End Time (Minute):").grid(row=12, column=0)
        self.replot_end_time_entry = tk.Entry(self)
        self.replot_end_time_entry.grid(row=12, column=1)

        # Add a Plot button
        tk.Button(self, text="Re-generate Plots", command=self.replot_selected_period).grid(row=13, column=1)


    def replot_selected_period(self):
        try:
            start_time = float(self.replot_start_time_entry.get())
            end_time = float(self.replot_end_time_entry.get())
        except ValueError:
            messagebox.showinfo("Error", "Invalid start or end time. Please enter numeric values.")
            return

        if start_time >= end_time:
            messagebox.showinfo("Error", "Start time must be less than end time.")
            return

        # Call generate_selected_plots with the specified time period for replotting
        self.generate_selected_plots(self.df,start_time=start_time, end_time=end_time)

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
        self.save_last_selections()

    def select_control_log_input_file(self):
        file_path = filedialog.askopenfilename()
        self.control_log_input_file_entry.delete(0, tk.END)
        self.control_log_input_file_entry.insert(0, file_path)
        self.save_last_selections()

    def select_output_folder(self):
        folder_path = filedialog.askdirectory()
        self.output_folder_entry.delete(0, tk.END)
        self.output_folder_entry.insert(0, folder_path)
        self.save_last_selections()

    def prototype_selected(self,event=None):
        selected_prototype = self.prototype_var.get()
        self.show_pid_image(selected_prototype)

    #main function of this GUI that handles all the calculations
    def on_calculate_clicked(self):
        input_file = self.datasheet_entry.get()
        control_log_input_file = self.control_log_input_file_entry.get()
        output_folder = self.output_folder_entry.get()
        ambient_pressure = float(self.ambient_pressure_entry.get())
        current_prototype = self.prototype_var.get()
    
        saved_file_name = self.saved_file_name_entry.get().strip()

        if not output_folder or not os.path.isdir(output_folder):
            messagebox.showwarning("Warning","Output folder is not specified or does not exist.")
            return
        elif not saved_file_name:
            messagebox.showwarning("Warning", "Invalid or no file name provided.")
        
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

        df['Total_Power'] = df['Watt']
        df['Total_Power'] = pd.to_numeric(df['Total_Power'], errors='coerce')
        # apply airflow
        #df['Regen_Fan_Airflow'] = df['Regen_Fan'].apply(self.calculate_airflow(fan_speed=100,coefficient=0.8, intercept=5))
        #df['Regen_Fan_Airflow'] = df['Regen_Fan'].apply(lambda x: self.calculate_airflow(fan_speed=x, coefficient=0.8, intercept=5))
        df['Regen_Fan_Airflow'] = df['Regen_Fan'].apply(lambda x: self.calculate_airflow(fan_speed=x, prototype=current_prototype, fan_type='regen'))
        df['Process_Fan_Airflow_U'] = df['Process_Fan'].apply(lambda x: self.calculate_airflow(fan_speed=x, prototype=current_prototype, fan_type='process_u'))
        df['Process_Fan_Airflow_S'] = df['Process_Fan'].apply(lambda x: self.calculate_airflow(fan_speed=x, prototype=current_prototype, fan_type='process_s'))
        temp_df = df.copy()
        supply_temp = temp_df.columns[5:11]
        df['T_supply'] = temp_df[supply_temp].mean(axis=1)
        df['T_return'] = np.where(df['Left_Right'] == 1, df['AT3'], df['AT1'])
        df['dT[C]'] = df['T_return'] - df['T_supply']

        w_u_inlet_values = []
        message_printed_w_u = False  # Flag to track if the message has been printed
        for index, row in df.iterrows():
            TDryBulb = row['AT3']
            if row['RH1'] == 0 or row['RH1'] > 100:
                RelHum = row['RH4'] / 100
                if not message_printed_w_u:
                    print("Original RH1 is malfunctioning, so the system automatically uses RH4.")
                    message_printed_w_u = True
            else:
                RelHum = row['RH1'] / 100

            w_u_inlet = psychrolib.GetHumRatioFromRelHum(TDryBulb, RelHum, ambient_pressure)*1000
            w_u_inlet_values.append(w_u_inlet)

        # Assign the list of calculated values to the 'HR_U_Inlet' column
        df['W_U_Inlet'] = w_u_inlet_values

        w_s_inlet_values = []
        message_printed_w_s = False  # Flag to track if the message has been printed
        for index, row in df.iterrows():
            TDryBulb = row['AT1']
            if row['RH2'] == 0 or row['RH2'] > 100:
                RelHum = row['RH5'] / 100
                if not message_printed_w_s:
                    print("Original RH2 is malfunctioning, so the system automatically uses RH5.")
                    message_printed_w_s = True
            else:
                RelHum = row['RH2'] / 100
            w_s_inlet = psychrolib.GetHumRatioFromRelHum(TDryBulb, RelHum, ambient_pressure)*1000
            w_s_inlet_values.append(w_s_inlet)

        # Assign the list of calculated values to the 'HR_U_Inlet' column
        df['W_S_Inlet'] = w_s_inlet_values

        w_exhaust_list = [] 
        message_printed_w_exhaust = False  # Flag to track if the message has been printed
        for index, row in df.iterrows():
            TDryBulb = row['AT2']
            if row['RH3'] == 0 or row['RH3'] > 100:
                RelHum = row['RH6'] / 100
                if not message_printed_w_exhaust:
                    print("Original RH3 is malfunctioning, so the system automatically uses RH6.")
                    message_printed_w_exhaust = True
            else:
                RelHum = row['RH3'] / 100
            w_exhaust = psychrolib.GetHumRatioFromRelHum(TDryBulb, RelHum, ambient_pressure) * 1000
            w_exhaust_list.append(w_exhaust)  # Append to the list

        df['W_exhaust'] = w_exhaust_list
        RH_average = temp_df.columns[23:25]
        df['RH_avg'] = temp_df[RH_average].mean(axis=1)

        w_supply_list = [] 

        for index, row in df.iterrows():
            TDryBulb = row['T_supply']  # Use the 'T_supply' column
            RelHum = row['RH_avg'] / 100  # Use the calculated 'RH_avg' column
            w_supply = psychrolib.GetHumRatioFromRelHum(TDryBulb, RelHum, ambient_pressure) * 1000
            w_supply_list.append(w_supply)  # Append to the list

        df['W_supply'] = w_supply_list

        average_W_U_Inlet = df['W_U_Inlet'].mean()
        average_W_S_Inlet = df['W_S_Inlet'].mean()

        df['Exhaust Humidity Delta (Standard)'] = np.where(df['Left_Right'] == 1, df['W_exhaust'] - df['W_U_Inlet'], df['W_exhaust'] - df['W_S_Inlet'])


        df['Exhaust Humidity Delta (Averaged Inlet)'] = np.where(df['Left_Right'] == 1,
                                                                df['W_exhaust'] - average_W_U_Inlet,
                                                                df['W_exhaust'] - average_W_S_Inlet)

        df['Exhaust Humidity Delta (Averaged Inlet)'] = np.where(df['Left_Right'] == 1, df['W_exhaust'] - average_W_U_Inlet, df['W_exhaust'] - average_W_S_Inlet)
        df['Supply Humidity Delta (Standard) [g/kg]'] = np.where(df['Left_Right'] == 1,
                                                                df['W_U_Inlet'] - df['W_supply'],
                                                                df['W_S_Inlet'] - df['W_supply'])

        df['Supply Humidity Delta (Standard) [g/kg]'] = np.where(df['Left_Right'] == 1, df['W_U_Inlet'] - df['W_supply'], df['W_S_Inlet'] - df['W_supply'])

        df['Supply Humidity Delta (Averaged Inlet)'] = np.where(df['Left_Right'] == 1,
                                                                average_W_U_Inlet - df['W_supply'],
                                                                average_W_S_Inlet - df['W_supply'])
        df['Supply Humidity Delta (Averaged Inlet)'] = np.where(df['Left_Right'] == 1, average_W_U_Inlet - df['W_supply'], average_W_S_Inlet - df['W_supply'])
        df['Process_airflow'] = np.where(df['Left_Right'] == 1,
                                        df['Process_Fan_Airflow_U'],
                                        df['Process_Fan_Airflow_S'])
        df['Process V_dot'] = df['Process_airflow']/2118.88
        df['Process M_dot [kg/s]'] = df['Process V_dot']*1.18
        df['Regen V_dot'] = df['Regen_Fan_Airflow']/2118.88
        df['Regen M_dot [kg/s]'] = df['Regen V_dot']*1.18
        df['Q_lat_Supply [W]'] = df['Process M_dot [kg/s]']*(df['Supply Humidity Delta (Standard) [g/kg]']/1000)*2260*1000
        df['Q_lat_Supply Filtered[W]']=df['Process M_dot [kg/s]']*(df['Supply Humidity Delta (Averaged Inlet)']/1000)*2260*1000
        df['Q_lat_Supply [BTU/hr]'] = df['Q_lat_Supply [W]']*3.41
        df['Q_lat_Supply Filtered[BTU/hr]'] = df['Q_lat_Supply Filtered[W]']*3.41

        df['Q_sens [W]'] = df['Process M_dot [kg/s]']*1006*df['dT[C]']
        df['Q_sens [BTU/hr]'] = df['Q_sens [W]']*3.41
        df['Q_lat_Exhaust [W]'] = df['Regen M_dot [kg/s]']*(df['Exhaust Humidity Delta (Standard)']/1000)*2260*1000
        df['Q_lat_Exhaust Filtered[W]'] = df['Regen M_dot [kg/s]']*(df['Exhaust Humidity Delta (Averaged Inlet)']/1000)*2260*1000
        df['Q_lat_Exhaust [BTU/hr]'] = df['Q_lat_Exhaust [W]']*3.41
        df['Q_lat_Exhaust Filtered[BTU/hr]'] = df['Q_lat_Exhaust Filtered[W]']*3.41

        df['Q_tot (Exhaust Latent) [BTU/hr]'] = df['Q_sens [BTU/hr]']+df['Q_lat_Exhaust [BTU/hr]']
        df['Q_tot (Supply Latent) [BTU/hr]'] = df['Q_sens [BTU/hr]'] + df['Q_lat_Supply Filtered[BTU/hr]']

        df['EER (Exhaust Latent) [BTU/Wh]'] = df['Q_tot (Exhaust Latent) [BTU/hr]']/df['Total_Power']
        df['EER (Supply Latent) [BTU/Wh]'] = df['Q_tot (Supply Latent) [BTU/hr]']/df['Total_Power']

        df['Capacity'] = df['Q_sens [BTU/hr]']+ df['Q_lat_Exhaust [BTU/hr]']
        df['COP'] = df['Capacity']/df['Total_Power']

        df['CEER']=df['Capacity']/df['Total_Power']

        df['Average_Power_5min'] = df.groupby((df['TimeDifference'] // 5) * 5)['Total_Power'].transform('mean')
        df['Average_Q_tot_5min'] = df.groupby((df['TimeDifference'] // 5) * 5)['Q_tot (Exhaust Latent) [BTU/hr]'].transform('mean')
        df['EER_5min'] = df.groupby((df['TimeDifference'] // 5) * 5)['EER (Exhaust Latent) [BTU/Wh]'].transform('mean')
        df['Q_lat_5min'] = df.groupby((df['TimeDifference'] // 5) * 5)['Q_lat_Exhaust [BTU/hr]'].transform('mean')
        window_size = 5
        # Calculate the moving average for 'Total_Power'
        df['Average_Power_5min'] = df['Total_Power'].rolling(window=window_size).mean()
        df['Average_Q_tot_5min'] = df['Q_tot (Exhaust Latent) [BTU/hr]'].rolling(window=window_size).mean()
        df['EER_5min'] = df['EER (Exhaust Latent) [BTU/Wh]'].rolling(window=window_size).mean()
        df['Q_lat_5min'] = df['Q_lat_Exhaust [BTU/hr]'].rolling(window=window_size).mean()
        df['Q_sens_5min']=df['Q_sens [BTU/hr]'].rolling(window=window_size).mean()
        df['Capacity_5min']=df['Capacity'].rolling(window=window_size).mean()
        df['COP_5min']=df['COP'].rolling(window=window_size).mean()
        df['CEER_5min']=df['CEER'].rolling(window=window_size).mean()

        # Save results to output folder
        self.df = df
        df.to_excel(output_file_path, index=False)
        self.generate_selected_plots(df)
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
    
    def generate_selected_plots(self,df,start_time=None, end_time=None):
        output_folder = self.output_folder_entry.get()
        base_file_name = self.saved_file_name_entry.get().strip()

        if base_file_name.endswith('.png'):
            base_file_name = base_file_name[:-4]

        if not base_file_name.endswith('.png'):
            base_file_name += '.png'
        base_file_name = base_file_name[:-5] 

        if start_time is not None and end_time is not None:
            df = df[(df['TimeDifference'] >= start_time) & (df['TimeDifference'] <= end_time)]
            if df.empty:
                messagebox.showinfo("Error", "No data available for the selected time period.")
                return
        selected_indices = self.plot_selection_listbox.curselection()
        selected_plots = [self.plot_selection_listbox.get(i) for i in selected_indices]

        if not selected_plots:
            messagebox.showinfo("Info", "Please select at least one plot to generate.")
            return
        
        num_plots = len(selected_plots)
        cols = 2  
        rows = math.ceil(num_plots / cols)

        # Create a figure for the plots
        fig, axs = plt.subplots(rows, cols, figsize=(20, 5 * rows),squeeze=False)
        plt.suptitle('Performance Plotting', fontsize=20, fontweight='bold')

        # Flatten axs for easy indexing
        axs = axs.flatten()

        # A dictionary to map plot titles to plotting functions
        plot_functions = {
            "Plot of Time Difference vs AT3": lambda df, ax: self.plot_time_difference_vs_AT3(df, ax),
            "Plot of Time vs Power": lambda df, ax:self.plot_time_difference_vs_Total_Power(df, ax),
            "Plot of Time vs Total Cooling":lambda df, ax:self.plot_time_difference_vs_Total_Cooling(df, ax),
            "Plot of Time vs EER":lambda df, ax:self.plot_time_difference_vs_EER(df, ax),
            "Plot of Time vs Latent Capacity":lambda df, ax:self.plot_time_difference_vs_Q_lat_Exhaust(df, ax),
            "Plot of Time vs Sensible Capacity":lambda df, ax:self.plot_time_difference_vs_Q_sens(df, ax),
            "Plot of Time vs COP":lambda df, ax:self.plot_time_difference_vs_COP(df, ax)
        }
        # Iterate over selected plots and assign them to subplots dynamically
        for i, plot_title in enumerate(selected_plots):
            if plot_title in plot_functions and i < len(axs):
                plot_functions[plot_title](df, axs[i])
    
        # Hide any unused axes if there are fewer plots than subplots
        for j in range(num_plots, len(axs)):
            fig.delaxes(axs[j])
        # Adjust layout to prevent clipping of titles and labels
        plt.tight_layout()
        plt.subplots_adjust(hspace=0.4, wspace=0.1)
        # Finding a unique filename by incrementing a number suffix if needed
        sequence_number = 1
        while True:
            if sequence_number == 1:
                filename = f"{base_file_name}.png"
            else:
                filename = f"{base_file_name}_{sequence_number}.png"
            plot_path = os.path.join(output_folder, filename)
        
            # Break the loop if the filename does not exist yet
            if not os.path.exists(plot_path):
                break
            sequence_number += 1
    
        plt.savefig(plot_path)
        plt.show()

    def plot_time_difference_vs_AT3(self, df, ax):
        required_columns = ['TimeDifference', 'AT3']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns for plotting: {', '.join(missing_columns)}")
        ax.plot(df['TimeDifference'], df['AT3'])
        ax.set_xlabel('Time Difference (Minute)')
        ax.set_ylabel('AT3')
        ax.set_title('Plot of Time Difference vs AT3')
        ax.grid(True)
    
    def plot_time_difference_vs_Total_Power(self, df, ax):
        # Check for the existence of required columns in DataFrame
        required_columns = ['TimeDifference', 'Total_Power', 'Average_Power_5min']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns for plotting: {', '.join(missing_columns)}")

        # Plotting Total Power and its 5-minute average
        ax.plot(df['TimeDifference'], df['Total_Power'], label='Total Power', marker='o', linestyle='-', markersize=4)
        ax.plot(df['TimeDifference'], df['Average_Power_5min'], label='Average Power (5min)', marker='', linestyle='--')
    
        # Setting the labels, title, and grid
        ax.set_xlabel('Time Difference (Minute)')
        ax.set_ylabel('Power')
        ax.set_title('Plot of Time vs Power')
        ax.grid(True)
    
        # Displaying the legend
        ax.legend()

    def plot_time_difference_vs_Total_Cooling(self, df, ax):
        # Check for the existence of required columns in DataFrame
        required_columns = ['TimeDifference', 'Q_tot (Exhaust Latent) [BTU/hr]', 'Average_Q_tot_5min']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns for plotting: {', '.join(missing_columns)}")

        # Plotting Total Power and its 5-minute average
        ax.plot(df['TimeDifference'], df['Q_tot (Exhaust Latent) [BTU/hr]'], label='Total Cooling', marker='o', linestyle='-', markersize=4)
        ax.plot(df['TimeDifference'], df['Average_Q_tot_5min'], label='Average Cooling (5min)', marker='', linestyle='--')
    
        # Setting the labels, title, and grid
        ax.set_xlabel('Time Difference (Minute)')
        ax.set_ylabel('Total Cooling')
        ax.set_title('Plot of Time vs Total Cooling')
        ax.grid(True)
    
        # Displaying the legend
        ax.legend()

    def plot_time_difference_vs_EER(self, df, ax):
        # Check for the existence of required columns in DataFrame
        required_columns = ['TimeDifference', 'EER (Exhaust Latent) [BTU/Wh]', 'EER_5min']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns for plotting: {', '.join(missing_columns)}")

        # Plotting Total Power and its 5-minute average
        ax.plot(df['TimeDifference'], df['EER (Exhaust Latent) [BTU/Wh]'], label='EER', marker='o', linestyle='-', markersize=4)
        ax.plot(df['TimeDifference'], df['EER_5min'], label='Average EER (5min)', marker='', linestyle='--')
    
        # Setting the labels, title, and grid
        ax.set_xlabel('Time Difference (Minute)')
        ax.set_ylabel('EER')
        ax.set_title('Plot of Time vs EER')
        ax.grid(True)
    
        # Displaying the legend
        ax.legend()

    def plot_time_difference_vs_Q_lat_Exhaust(self, df, ax):
        # Check for the existence of required columns in DataFrame
        required_columns = ['TimeDifference', 'Q_lat_Exhaust [BTU/hr]', 'Q_lat_5min']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns for plotting: {', '.join(missing_columns)}")

        # Plotting Total Power and its 5-minute average
        ax.plot(df['TimeDifference'], df['Q_lat_Exhaust [BTU/hr]'], label='Q_lat', marker='o', linestyle='-', markersize=4)
        ax.plot(df['TimeDifference'], df['Q_lat_5min'], label='Average Q_lat (5min)', marker='', linestyle='--')
    
        # Setting the labels, title, and grid
        ax.set_xlabel('Time Difference (Minute)')
        ax.set_ylabel('Q_lat_Exhaust')
        ax.set_title('Plot of Time vs Q_lat_Exhaust')
        ax.grid(True)
    
        # Displaying the legend
        ax.legend()

    def plot_time_difference_vs_Q_sens(self, df, ax):
        # Check for the existence of required columns in DataFrame
        required_columns = ['TimeDifference', 'Q_sens [BTU/hr]', 'Q_sens_5min']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns for plotting: {', '.join(missing_columns)}")

        # Plotting Total Power and its 5-minute average
        ax.plot(df['TimeDifference'], df['Q_sens [BTU/hr]'], label='Q_sens', marker='o', linestyle='-', markersize=4)
        ax.plot(df['TimeDifference'], df['Q_sens_5min'], label='Average Q_sens (5min)', marker='', linestyle='--')
    
        # Setting the labels, title, and grid
        ax.set_xlabel('Time Difference (Minute)')
        ax.set_ylabel('Q_snes')
        ax.set_title('Plot of Time vs Q_sens')
        ax.grid(True)
    
        # Displaying the legend
        ax.legend()

    def plot_time_difference_vs_COP(self, df, ax):
        # Check for the existence of required columns in DataFrame
        required_columns = ['TimeDifference', 'COP', 'COP_5min']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns for plotting: {', '.join(missing_columns)}")

        # Plotting Total Power and its 5-minute average
        ax.plot(df['TimeDifference'], df['COP'], label='COP', marker='o', linestyle='-', markersize=4)
        ax.plot(df['TimeDifference'], df['COP_5min'], label='COP (5min)', marker='', linestyle='--')
    
        # Setting the labels, title, and grid
        ax.set_xlabel('Time Difference (Minute)')
        ax.set_ylabel('COP')
        ax.set_title('Plot of Time vs COP')
        ax.grid(True)
    
        # Displaying the legend
        ax.legend()


    def save_last_selections(self):
        paths = {
        'datasheet_path': self.datasheet_entry.get(),
        'control_log_path': self.control_log_input_file_entry.get(),
        'output_folder_path': self.output_folder_entry.get()
        }
        with open('last_selections.txt', 'w') as file:
            for path in paths.values():
                file.write(f"{path}\n")

    def load_last_selections(self):
        try:
            with open('last_selections.txt', 'r') as file:
                paths = file.readlines()
                paths = [path.strip() for path in paths]
                if len(paths) == 3:
                    self.datasheet_entry.insert(0, paths[0])
                    self.control_log_input_file_entry.insert(0, paths[1])
                    self.output_folder_entry.insert(0, paths[2])
        except FileNotFoundError:
            # It's okay if the file doesn't exist; it means the program has never been run before.
            pass

    def calculate_airflow(self, fan_speed, prototype, fan_type):
        if prototype in self.prototypes and fan_type in self.prototypes[prototype]:
            coefficient, intercept = self.prototypes[prototype][fan_type]
        else:
            raise ValueError(f"Prototype {prototype} or fan type {fan_type} not found.")
        return fan_speed * coefficient + intercept
    
    def show_pid_image(self, prototype_name):
        image_path = f"Performance Testing/PID/{prototype_name.replace(' ', '_')}.png"
        try:
            img = Image.open(image_path)
            imgtk = ImageTk.PhotoImage(image=img)
            pid_window = Toplevel(self)
            pid_window.title(f"P&ID for {prototype_name}")
            Label(pid_window, image=imgtk).pack()
            pid_window.imgtk = imgtk  # Keep a reference to avoid garbage collection
        except FileNotFoundError:
            print(f"Image file not found: {image_path}")

if __name__ == "__main__":
    psychrolib.SetUnitSystem(psychrolib.SI)
    TIME_THRESHOLD_SECONDS = 10
    app = Application()
    app.mainloop()
