import psychrolib
import math
import pandas as pd
from helper_functions import U_config_or_not
from datetime import datetime
import numpy as np
psychrolib.SetUnitSystem(psychrolib.SI)
TDewPoint = psychrolib.GetTDewPointFromRelHum(25.0, 0.80)
print(TDewPoint)
#read csv
df = pd.read_csv('Book2.csv',header=None)

#Assign columns
columns_to_process_at = df.columns[2:11]  # Assuming 'C' is the third column (index 2)
columns_to_process_lt = df.columns[12:17]  # Assuming 'M' is the 13th column (index 12)
columns_to_process_rh = df.columns[20:27]  # Assuming 'U' is the 21st column (index 20)
columns_to_process_w = df.columns[28:35]  # Assuming 'AC' is the 29th column (index 28)

#variables
AT = {}
LT = {}
RH = {}
W = {}

for i, column in enumerate(columns_to_process_at, start=1):
    AT[f'{i}'] = df[column]

for i, column in enumerate(columns_to_process_lt, start=1):
    LT[f'{i}'] = df[column]

P1 = df[df.columns[18]]
df = df.rename(columns={18: 'P1'})
P2 = df[df.columns[19]]

for i, column in enumerate(columns_to_process_rh, start=1):
    RH[f'{i}'] = df[column]

for i, column in enumerate(columns_to_process_w, start=1):
    W[f'{i}'] = df[column]

KWh = df[df.columns[36]]
Watt = df[df.columns[37]]

df = df.iloc[1:]

df['valid_times'] = pd.to_datetime(df.iloc[:, 1], format='%H:%M:%S', errors='coerce')
df['valid_times'] = df['valid_times'].dt.time  # Extract time part only

start_time = df['valid_times'].dropna().iloc[0]
#create a new column
df['TimeDifference'] = 0.0
# Iterate over each row and calculate the time difference
for index, row in df.iterrows():
    current_time = row['valid_times']
    time_difference = (current_time.hour * 3600 + current_time.minute * 60 + current_time.second) - (start_time.hour * 3600 + start_time.minute * 60 + start_time.second)
    df.at[index, 'TimeDifference'] = time_difference / 3600
    
df['Total_Power'] = Watt
df['U_Config'] = U_config_or_not(df[13], df[15])
df['Super_Heat'] = 0.0
df['Sub_Cool'] = 0.0
#df['T_supply'] = df[df.columns[5:11]].apply(lambda x: pd.to_numeric(''.join(map(str, x).split()), errors='coerce')).mean(axis=1)

temp_df = df.copy()
supply_temp = temp_df.columns[5:11]
temp_df[supply_temp] = temp_df[supply_temp].apply(lambda x: pd.to_numeric(x.str.replace(r'[^0-9.]', ''), errors='coerce'))

df['T_supply'] = temp_df[supply_temp].mean(axis=1)
df['T_return'] = np.where(df['U_Config'] == 1, df.iloc[:, 4], df.iloc[:, 2])
df['T_return'] = pd.to_numeric(df['T_return'], errors='coerce')
df['T_supply'] = pd.to_numeric(df['T_supply'], errors='coerce')

df.iloc[:, 4] = pd.to_numeric(df.iloc[:, 4], errors='coerce')  # Assuming the 4th column needs conversion
df.iloc[:, 20] = pd.to_numeric(df.iloc[:, 20], errors='coerce')  # Assuming the 20th column needs conversion

df['dT[C]'] = df['T_return'] - df['T_supply']

# Create an empty list to store calculated values
hr_u_inlet_values = []

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    TDryBulb = row.iloc[4]
    RelHum = row.iloc[20] / 100
    Pressure = 101325
    hr_u_inlet = psychrolib.GetHumRatioFromRelHum(TDryBulb, RelHum, Pressure)*1000
    hr_u_inlet_values.append(hr_u_inlet)

# Assign the list of calculated values to the 'HR_U_Inlet' column
df['HR_U_Inlet'] = hr_u_inlet_values

# Convert the column to numeric
df['HR_U_Inlet'] = pd.to_numeric(df['HR_U_Inlet'], errors='coerce')

#Generate the output file
#generate output excel
excel_output = 'output_file.xlsx'
df.to_excel(excel_output, index=False)