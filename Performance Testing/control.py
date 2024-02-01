import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import psychrolib
import Steady_state as ss
import datetime as dt

# Constants
TIME_THRESHOLD_SECONDS = 5
INPUT_PATH = 'Performance Testing/Input csv/'
OUTPUT_PATH = 'Performance Testing/Output excel files/'

# Setting unit system for psychrolib
psychrolib.SetUnitSystem(psychrolib.SI)
#test Psychro
TDewPoint = psychrolib.GetTDewPointFromRelHum(25.0, 0.80)
print(TDewPoint)

# Function to parse and clean data
def prepare_dataframe(file_path, time_format, timestamp_col_index=1):
    try:
        df = pd.read_csv(file_path, delimiter='\t')
        df.iloc[:, 2:] = df.iloc[:, 2:].apply(pd.to_numeric, errors='coerce')
        df['valid_times'] = pd.to_datetime(df.iloc[:, timestamp_col_index], format=time_format, errors='coerce')
        df['valid_seconds'] = df['valid_times'].dt.hour * 3600 + df['valid_times'].dt.minute * 60 + df['valid_times'].dt.second
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None
    return df

# Function to merge dataframes based on time difference
def merge_dataframes(df1, df2, time_threshold):
    for index, row in df1.iterrows():
        time_difference = abs(df2['valid_seconds'] - row['valid_seconds'])
        close_rows = df2[time_difference <= time_threshold]

        if not close_rows.empty:
            for col in columns_to_merge:
                df1.at[index, col] = close_rows.iloc[0][col]
    return df1

# Read and prepare the first dataframe
df = prepare_dataframe(INPUT_PATH + 'gui_test.txt', '%H:%M:%S')
if df is None:
    exit()

# Read and prepare the second dataframe
new_df = prepare_dataframe(INPUT_PATH + 'gui_log.txt', '%m/%d/%Y %I:%M:%S %p')
if new_df is None:
    exit()

# Renaming columns
rename_columns = {
    new_df.columns[i]: name for i, name in enumerate([
        'Superheat', 'Subcool', 'Num_Cycles', 'Compressor_En', 'Compressor',
        'Fan_En', 'Process_Fan', 'Regen_Fan', 'EEV', 'U_Config', 
        'Cooling_Heating', 'Automode_En'], 24)
}
new_df = new_df.rename(columns=rename_columns)

# Converting specific columns to numeric
columns_to_merge = list(rename_columns.values())
new_df[columns_to_merge] = new_df[columns_to_merge].apply(pd.to_numeric, errors='coerce')

# Perform the merge
df = merge_dataframes(df, new_df, TIME_THRESHOLD_SECONDS)
print(df)
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

df = df.iloc[1:]

    
df['Total_Power'] = Watt
### read airflow from file
def calculate_airflow(fan_speed, coefficient=0.8, intercept=165):
    """
    Calculate the airflow based on the fan speed using the regression formula.
    Note: need further follow-up on this regrssion function and that function need to be
    changed on different prototype 
    """
    return fan_speed * coefficient + intercept

# Apply the calculate_airflow function to these columns
df['Regen_Fan_Airflow'] = df['Regen Fan Speed'].apply(calculate_airflow)
df['Process_Fan_Airflow_1'] = df['Process Fan Speed'].apply(calculate_airflow)
df['Process_Fan_Airflow_2'] = df['Process Fan Speed'].apply(calculate_airflow)

#df['U_Config'] = df.apply(lambda row: U_config_or_not(row[df.columns[13]], row[df.columns[15]]), axis=1)
#df['Super_Heat'] = 0.0
#df['Sub_Cool'] = 0.0
#df['Compressor Power'] = 250
#df['Fan Power'] = 143
#df['Standby_power'] = 0

temp_df = df.copy()
supply_temp = temp_df.columns[5:11]

df['T_supply'] = temp_df[supply_temp].mean(axis=1)
print(df['T_supply'] )
df['T_return'] = np.where(df['U_Config'] == 1, df.iloc[:, 4], df.iloc[:, 2])

df['dT[C]'] = df['T_return'] - df['T_supply']

# Create an empty list to store calculated values
w_u_inlet_values = []

for index, row in df.iterrows():
    TDryBulb = row.iloc[4]
    RelHum = row.iloc[20] / 100
    Pressure = 101325
    w_u_inlet = psychrolib.GetHumRatioFromRelHum(TDryBulb, RelHum, Pressure)*1000
    w_u_inlet_values.append(w_u_inlet)

# Assign the list of calculated values to the 'HR_U_Inlet' column
df['W_U_Inlet'] = w_u_inlet_values

w_s_inlet_values = []

for index, row in df.iterrows():
    TDryBulb = row.iloc[2]
    RelHum = row.iloc[21] / 100
    Pressure = 101325
    w_s_inlet = psychrolib.GetHumRatioFromRelHum(TDryBulb, RelHum, Pressure)*1000
    w_s_inlet_values.append(w_s_inlet)

# Assign the list of calculated values to the 'HR_U_Inlet' column
df['W_S_Inlet'] = w_s_inlet_values

w_exhaust_list = [] 

for index, row in df.iterrows():
    TDryBulb = row.iloc[3]
    RelHum = row.iloc[22] / 100
    Pressure = 101325
    w_exhaust = psychrolib.GetHumRatioFromRelHum(TDryBulb, RelHum, Pressure) * 1000
    w_exhaust_list.append(w_exhaust)  # Append to the list

df['W_exhaust'] = w_exhaust_list

RH_average = temp_df.columns[23:25]
df['RH_avg'] = temp_df[RH_average].mean(axis=1)

w_supply_list = [] 

for index, row in df.iterrows():
    TDryBulb = row['T_supply']  # Use the 'T_supply' column
    RelHum = row['RH_avg'] / 100  # Use the calculated 'RH_avg' column
    Pressure = 101325
    w_supply = psychrolib.GetHumRatioFromRelHum(TDryBulb, RelHum, Pressure) * 1000
    w_supply_list.append(w_supply)  # Append to the list

df['W_supply'] = w_supply_list

average_W_U_Inlet = df['W_U_Inlet'].mean()
#average_W_U_Inlet = df.loc[steady_state_line:, 'W_U_Inlet'].mean()
average_W_S_Inlet = df['W_S_Inlet'].mean()
#average_W_S_Inlet = df.loc[steady_state_line:,'W_S_Inlet'].mean()

average_ss_exhaust_humidity = ss.df['Exhaust Humidity Delta (Averaged Inlet)'].mean()
average_ss_supply_humidity = ss.df['Supply Humidity Delta (Standard) [g/kg]'].mean()

# Use np.where to apply the condition and calculate the new column
df['Exhaust Humidity Delta (Standard)'] = np.maximum(
    np.where(df['U_Config'] == 1, df['W_exhaust'] - df['W_U_Inlet'], df['W_exhaust'] - df['W_S_Inlet']) - average_ss_exhaust_humidity,
    0
)

df['Exhaust Humidity Delta (Averaged Inlet)'] = np.where(df['U_Config'] == 1,
                                                         df['W_exhaust'] - average_W_U_Inlet,
                                                         df['W_exhaust'] - average_W_S_Inlet)

df['Exhaust Humidity Delta (Averaged Inlet)'] = np.maximum(
    np.where(df['U_Config'] == 1, df['W_exhaust'] - average_W_U_Inlet, df['W_exhaust'] - average_W_S_Inlet) - average_ss_exhaust_humidity,
    0
)
df['Supply Humidity Delta (Standard) [g/kg]'] = np.where(df['U_Config'] == 1,
                                                         df['W_U_Inlet'] - df['W_supply'],
                                                         df['W_S_Inlet'] - df['W_supply'])

df['Supply Humidity Delta (Standard) [g/kg]'] = np.maximum(
    np.where(df['U_Config'] == 1, df['W_U_Inlet'] - df['W_supply'], df['W_S_Inlet'] - df['W_supply']) - average_ss_supply_humidity,
    0
)

df['Supply Humidity Delta (Averaged Inlet)'] = np.where(df['U_Config'] == 1,
                                                        average_W_U_Inlet - df['W_supply'],
                                                        average_W_S_Inlet - df['W_supply'])
df['Supply Humidity Delta (Averaged Inlet)'] = np.maximum(
    np.where(df['U_Config'] == 1, average_W_U_Inlet - df['W_supply'], average_W_S_Inlet - df['W_supply']) - average_ss_supply_humidity,
    0
)
df['Process_airflow'] = np.where(df['U_Config'] == 1,
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
df['COP'] = df['Capacity']/(df['Compressor Power']+df['Fan Power'])

df['CEER']=df['Capacity']/(df['Total_Power']+ df['Standby_power'])


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
    output_file = OUTPUT_PATH + 'updated_data_with_merged_columns.xlsx'
    df.to_excel(output_file, index=False)
    print("Data merged and saved to", output_file)
except Exception as e:
    print(f"Error saving to {output_file}: {e}")
