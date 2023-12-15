import psychrolib
import pandas as pd
from helper_functions import U_config_or_not
import numpy as np
import matplotlib.pyplot as plt
import Steady_state as ss
psychrolib.SetUnitSystem(psychrolib.SI)
#test Psychro
TDewPoint = psychrolib.GetTDewPointFromRelHum(25.0, 0.80)
print(TDewPoint)
# Read CSV file and set the first usable row
first_usable_row = 24
df = pd.read_csv('Performance Testing/Book2.csv',header=None)
df = df.iloc[first_usable_row:]
df.iloc[:, 2:] = df.iloc[:, 2:].apply(pd.to_numeric, errors='coerce')

# Assign columns for different variables
columns_to_process_at = df.columns[2:11]  # Assuming 'C' is the third column (index 2)
columns_to_process_lt = df.columns[12:17]  # Assuming 'M' is the 13th column (index 12)
columns_to_process_rh = df.columns[20:27]  # Assuming 'U' is the 21st column (index 20)
columns_to_process_w = df.columns[28:35]  # Assuming 'AC' is the 29th column (index 28)

# Set variables
process_airflow1 = 750
process_airflow2 = 615
regen_airflow = 395
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

df = df.iloc[1:]

df['valid_times'] = pd.to_datetime(df.iloc[:, 1], format='%H:%M:%S', errors='coerce')
df['valid_times'] = df['valid_times'].dt.time  # Extract time part only

start_time = df['valid_times'].dropna().iloc[0]
# Create a new column for time differences
df['TimeDifference'] = 0.0
# Iterate over each row and calculate the time difference
for index, row in df.iterrows():
    current_time = row['valid_times']
    time_difference = (current_time.hour * 3600 + current_time.minute * 60 + current_time.second) - (start_time.hour * 3600 + start_time.minute * 60 + start_time.second)
    df.at[index, 'TimeDifference'] = time_difference / 60
    
df['Total_Power'] = Watt
df['U_Config'] = df.apply(lambda row: U_config_or_not(row[df.columns[13]], row[df.columns[15]]), axis=1)
df['Super_Heat'] = 0.0
df['Sub_Cool'] = 0.0

temp_df = df.copy()
supply_temp = temp_df.columns[5:11]

df['T_supply'] = temp_df[supply_temp].mean(axis=1)
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
                                 process_airflow1,
                                 process_airflow2)
df['Process V_dot'] = df['Process_airflow']/2118.88
df['Process M_dot [kg/s]'] = df['Process V_dot']*1.18
df['Regen Airflow'] = regen_airflow
df['Regen V_dot'] = df['Regen Airflow']/2118.88
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

###################
sd = df.loc[270:].copy()

sd['valid_times'] = pd.to_datetime(df.iloc[:, 1], format='%H:%M:%S', errors='coerce')
sd['valid_times'] = sd['valid_times'].dt.time  # Extract time part only

start_time = sd['valid_times'].dropna().iloc[0]
#create a new column
sd['TimeDifference'] = 0.0
# Iterate over each row and calculate the time difference
for index, row in df.iterrows():
    current_time = row['valid_times']
    time_difference = (current_time.hour * 3600 + current_time.minute * 60 + current_time.second) - (start_time.hour * 3600 + start_time.minute * 60 + start_time.second)
    sd.at[index, 'TimeDifference'] = time_difference / 60

# Save the separated data to a new Excel file

sd.to_excel('steady_state_processed_data.xlsx', index=False)

#Generate the output file
#generate output excel
excel_output = 'output_file.xlsx'
df.to_excel(excel_output, index=False)

# Create a figure with subplots
fig, axs = plt.subplots(2, 2, figsize=(15, 10))
plt.suptitle('Switching Performance', fontsize=16, fontweight='bold')

# Plot 1
axs[0, 0].plot(df['TimeDifference'], df['AT3'])
axs[0, 0].set_xlabel('Time Difference (Minute)')
axs[0, 0].set_ylabel('AT3')
axs[0, 0].set_title('Plot of Time Difference vs AT3')
axs[0, 0].grid(True)

# Plot 2
axs[0, 1].plot(df['TimeDifference'], df['Total_Power'], label='Total Power')
axs[0, 1].plot(df['TimeDifference'], df['Average_Power_5min'], label='Average Power (5min)')
axs[0, 1].set_xlabel('Time Difference (Minute)')
axs[0, 1].set_ylabel('Power')
axs[0, 1].set_title('Plot of Time vs Power')
axs[0, 1].grid(True)
axs[0, 1].legend()

# Plot 3
axs[1, 0].plot(df['TimeDifference'], df['Q_tot (Exhaust Latent) [BTU/hr]'], label='Total Cooling')
axs[1, 0].plot(df['TimeDifference'], df['Average_Q_tot_5min'], label='Average Cooling (5min)')
axs[1, 0].set_xlabel('Time Difference (Minute)')
axs[1, 0].set_ylabel('Total Cooling')
axs[1, 0].set_title('Plot of Time vs Total Cooling')
axs[1, 0].grid(True)
axs[1, 0].legend()

# Plot 4
axs[1, 1].plot(df['TimeDifference'], df['EER (Exhaust Latent) [BTU/Wh]'], label='EER')
axs[1, 1].plot(df['TimeDifference'], df['EER_5min'], label='EER (5min)')
axs[1, 1].set_xlabel('Time Difference (Minute)')
axs[1, 1].set_ylabel('EER')
axs[1, 1].set_title('Plot of Time vs EER')
axs[1, 1].grid(True)
axs[1, 1].legend()

# Adjust layout to prevent clipping of titles and labels
plt.tight_layout()

# Show the combined plot


# Save the plot as an image file (choose the format you prefer)
image_file_path = 'Performance Testing/switching_performance_plot.png'
plt.savefig(image_file_path, bbox_inches='tight')
plt.show()

# Print a message indicating where the image file is saved
print(f"Plot saved as {image_file_path}")
