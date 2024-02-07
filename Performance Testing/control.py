import psychrolib
import pandas as pd
from helper_functions import U_config_or_not
import numpy as np
import matplotlib.pyplot as plt
import Steady_state as ss
# Constants
TIME_THRESHOLD_SECONDS = 10
INPUT_PATH = 'Performance Testing/Input csv/'
OUTPUT_PATH = 'Performance Testing/Output excel files/'

# Setting unit system for psychrolib
psychrolib.SetUnitSystem(psychrolib.SI)
Pressure = 101325
#Pressure = float(ambient_pressure_entry.get())  # Make sure this value is passed from the GUI

# Function to parse and clean data
def prepare_dataframe(file_path, time_format='%H:%M:%S', num_cols=None):
    """Prepares and cleans the dataframe from the given file."""
    usecols = list(range(num_cols)) if num_cols else None
    df = pd.read_csv(file_path, delimiter='\t', usecols=usecols, header=None)
    df.iloc[:, 2:] = df.iloc[:, 2:].apply(pd.to_numeric, errors='coerce')
    df['valid_times'] = pd.to_datetime(df.iloc[:, 1], format=time_format, errors='coerce').dt.time
    return df

def calculate_airflow(fan_speed, coefficient=0.8, intercept=165):
    return fan_speed * coefficient + intercept


# Read and prepare the first dataframe

df = prepare_dataframe(INPUT_PATH + 'new.txt', '%H:%M:%S', num_cols=38)
print(df['valid_times'])

# Read and prepare the second dataframe
new_df = prepare_dataframe(INPUT_PATH + 'new_log.txt', '%m/%d/%Y %I:%M:%S %p')
print(new_df['valid_times'])

# Renaming columns
rename_columns = {
    new_df.columns[i]: name for i, name in enumerate([
        'Superheat', 'Subcool', 'Num_Cycles', 'Compressor_En', 'Compressor',
        'Fan_En', 'Process_Fan', 'Regen_Fan', 'EEV', 'Left_Right', 
        'Cooling_Heating', 'Automode_En'], 24)
}
new_df = new_df.rename(columns=rename_columns)

# Converting specific columns to numeric
columns_to_merge = list(rename_columns.values())
new_df[columns_to_merge] = new_df[columns_to_merge].apply(pd.to_numeric, errors='coerce')

# Merging dataframes based on time difference
def merge_dataframes(df1, df2, time_threshold):
    merged_dfs = []

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

# Perform the merge
df = merge_dataframes(df, new_df, TIME_THRESHOLD_SECONDS)
df = df.iloc[1:, :] 


### after merging control log
# Assign columns for different variables
columns_to_process_at = df.columns[2:11]  # Assuming 'C' is the third column (index 2)
columns_to_process_lt = df.columns[12:17]  # Assuming 'M' is the 13th column (index 12)
columns_to_process_rh = df.columns[20:27]  # Assuming 'U' is the 21st column (index 20)
columns_to_process_w = df.columns[28:35]  # Assuming 'AC' is the 29th column (index 28)

# Rename columns for clarity
new_AT_column_names = {i: f'AT{i-1}' for i in range(2, 12)}
df = df.rename(columns=new_AT_column_names)

new_LT_column_names = {i: f'LT{i-11}' for i in range(12, 18)}
df = df.rename(columns=new_LT_column_names)

P1 = df[df.columns[18]]
df = df.rename(columns={18: 'P1'})
P2 = df[df.columns[19]]
df = df.rename(columns={19: 'P2'})

new_column_names_rh = {i: f'RH{i-19}' for i in range(20, 28)}
df = df.rename(columns=new_column_names_rh)

new_column_names_w = {i: f'W{i-27}' for i in range(28, 36)}
df = df.rename(columns=new_column_names_w)

KWh = df[df.columns[36]]
Watt = df[df.columns[37]]
df.rename(columns={df.columns[36]: 'kWh', df.columns[37]: 'Watt'}, inplace=True)

start_time = df['valid_times'].dropna().iloc[0]
# Create a new column for time differences
df['TimeDifference'] = 0.0
# Iterate over each row and calculate the time difference
for index, row in df.iterrows():
    current_time = row['valid_times']
    time_difference = (current_time.hour * 3600 + current_time.minute * 60 + current_time.second) - (start_time.hour * 3600 + start_time.minute * 60 + start_time.second)
    df.at[index, 'TimeDifference'] = time_difference / 60

df['Total_Power'] = Watt
df['Total_Power'] = pd.to_numeric(df['Total_Power'], errors='coerce')

# Apply the calculate_airflow function to these columns
df['Regen_Fan_Airflow'] = df['Regen_Fan'].apply(calculate_airflow)
df['Process_Fan_Airflow_1'] = df['Process_Fan'].apply(calculate_airflow)
df['Process_Fan_Airflow_2'] = df['Process_Fan'].apply(calculate_airflow)

temp_df = df.copy()
supply_temp = temp_df.columns[5:11]

df['T_supply'] = temp_df[supply_temp].mean(axis=1)
#print(df['T_supply'] )
df['T_return'] = np.where(df['Left_Right'] == 1, df.iloc[:, 4], df.iloc[:, 2])

df['dT[C]'] = df['T_return'] - df['T_supply']

# Create an empty list to store calculated values
w_u_inlet_values = []

for index, row in df.iterrows():
    TDryBulb = row.iloc[4]
    RelHum = row.iloc[20] / 100
    #Pressure = 101325
    w_u_inlet = psychrolib.GetHumRatioFromRelHum(TDryBulb, RelHum, Pressure)*1000
    w_u_inlet_values.append(w_u_inlet)

# Assign the list of calculated values to the 'HR_U_Inlet' column
df['W_U_Inlet'] = w_u_inlet_values

w_s_inlet_values = []

for index, row in df.iterrows():
    TDryBulb = row.iloc[2]
    RelHum = row.iloc[21] / 100
    #Pressure = 101325
    w_s_inlet = psychrolib.GetHumRatioFromRelHum(TDryBulb, RelHum, Pressure)*1000
    w_s_inlet_values.append(w_s_inlet)

# Assign the list of calculated values to the 'HR_U_Inlet' column
df['W_S_Inlet'] = w_s_inlet_values

w_exhaust_list = [] 

for index, row in df.iterrows():
    TDryBulb = row.iloc[3]
    RelHum = row.iloc[22] / 100
    #Pressure = 101325
    w_exhaust = psychrolib.GetHumRatioFromRelHum(TDryBulb, RelHum, Pressure) * 1000
    w_exhaust_list.append(w_exhaust)  # Append to the list

df['W_exhaust'] = w_exhaust_list

RH_average = temp_df.columns[23:25]
df['RH_avg'] = temp_df[RH_average].mean(axis=1)

w_supply_list = [] 

for index, row in df.iterrows():
    TDryBulb = row['T_supply']  # Use the 'T_supply' column
    RelHum = row['RH_avg'] / 100  # Use the calculated 'RH_avg' column
    #Pressure = 101325
    w_supply = psychrolib.GetHumRatioFromRelHum(TDryBulb, RelHum, Pressure) * 1000
    w_supply_list.append(w_supply)  # Append to the list

df['W_supply'] = w_supply_list

average_W_U_Inlet = df['W_U_Inlet'].mean()
average_W_S_Inlet = df['W_S_Inlet'].mean()

average_ss_exhaust_humidity = ss.df['Exhaust Humidity Delta (Averaged Inlet)'].mean()
average_ss_supply_humidity = ss.df['Supply Humidity Delta (Standard) [g/kg]'].mean()

# Use np.where to apply the condition and calculate the new column
df['Exhaust Humidity Delta (Standard)'] = np.maximum(
    np.where(df['Left_Right'] == 1, df['W_exhaust'] - df['W_U_Inlet'], df['W_exhaust'] - df['W_S_Inlet']) - average_ss_exhaust_humidity,
    0
)

df['Exhaust Humidity Delta (Averaged Inlet)'] = np.where(df['Left_Right'] == 1,
                                                         df['W_exhaust'] - average_W_U_Inlet,
                                                         df['W_exhaust'] - average_W_S_Inlet)

df['Exhaust Humidity Delta (Averaged Inlet)'] = np.maximum(
    np.where(df['Left_Right'] == 1, df['W_exhaust'] - average_W_U_Inlet, df['W_exhaust'] - average_W_S_Inlet) - average_ss_exhaust_humidity,
    0
)
df['Supply Humidity Delta (Standard) [g/kg]'] = np.where(df['Left_Right'] == 1,
                                                         df['W_U_Inlet'] - df['W_supply'],
                                                         df['W_S_Inlet'] - df['W_supply'])

df['Supply Humidity Delta (Standard) [g/kg]'] = np.maximum(
    np.where(df['Left_Right'] == 1, df['W_U_Inlet'] - df['W_supply'], df['W_S_Inlet'] - df['W_supply']) - average_ss_supply_humidity,
    0
)

df['Supply Humidity Delta (Averaged Inlet)'] = np.where(df['Left_Right'] == 1,
                                                        average_W_U_Inlet - df['W_supply'],
                                                        average_W_S_Inlet - df['W_supply'])
df['Supply Humidity Delta (Averaged Inlet)'] = np.maximum(
    np.where(df['Left_Right'] == 1, average_W_U_Inlet - df['W_supply'], average_W_S_Inlet - df['W_supply']) - average_ss_supply_humidity,
    0
)
df['Process_airflow'] = np.where(df['Left_Right'] == 1,
                                 df['Process_Fan_Airflow_1'],
                                 df['Process_Fan_Airflow_2'])
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
###################
# Save the merged dataframe to a new Excel file
output_file = OUTPUT_PATH + 'updated_data_with_merged_columns.xlsx'
df.to_excel(output_file, index=False)

# Save the merged dataframe to a new Excel file
try:
    output_file = OUTPUT_PATH + 'updated.xlsx'
    df.to_excel(output_file, index=False)
    print("Data merged and saved to", output_file)
except Exception as e:
    print(f"Error saving to {output_file}: {e}")
