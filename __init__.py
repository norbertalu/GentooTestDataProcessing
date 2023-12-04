import psychrolib
import math
import pandas as pd
from helper_functions import U_config_or_not
psychrolib.SetUnitSystem(psychrolib.IP)
#test Psychro
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
P2 = df[df.columns[19]]

for i, column in enumerate(columns_to_process_rh, start=1):
    RH[f'{i}'] = df[column]

for i, column in enumerate(columns_to_process_w, start=1):
    W[f'{i}'] = df[column]

KWh = df[df.columns[36]]
Watt = df[df.columns[37]]
print(df)
#Time_From_Start = df[df.columns[39]]
#Total_Power_W = df[df.columns[40]]

#u_config = U_config_or_not(LT['2'],LT['4'])

    