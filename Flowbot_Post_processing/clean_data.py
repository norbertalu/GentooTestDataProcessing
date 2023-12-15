import math
import pandas as pd
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

excel_file_path = 'Flowbot_Post_processing/Book3.xlsx'
df = pd.read_excel(excel_file_path, header=None, usecols=[0,3, 5]) 
df.columns = range(df.shape[1])  # Reset column indices

first_row_time = 65
up_out_time = 45
up_time = 20

rows_8 = 8
rows_16 = 16
count_15 = 15
count_2 = 2

df = df.iloc[1:]
# Initialize an empty DataFrame to store the final result
result_df = pd.DataFrame()

result_df = pd.concat([result_df, df.iloc[:first_row_time].copy()])

for i in range(first_row_time, len(df), up_time + first_row_time):
    # Skip up_out_time rows starting from the 64th row
    current_rows = df.iloc[i + up_out_time:i + up_out_time + first_row_time + up_time + first_row_time]

    # Append the current_rows to the result_df
    result_df = pd.concat([result_df, current_rows], ignore_index=True)

result_df = result_df[result_df.iloc[:,1] >= 0.5].reset_index(drop=True)

# Define the averaging patterns

# Initialize an empty DataFrame to store the averaged results
averaged_df = pd.DataFrame()

# Take the average of every 8 rows for 120 rows, generating 15 average points
for i in range(0, 8*15,8):
    avg_rows = result_df.iloc[i:i + 8].mean()
    averaged_df = pd.concat([averaged_df, avg_rows], axis=1, ignore_index=True)

for i in range((8*15+1), (8*15+1)+16*2, 16):
    avg_rows = result_df.iloc[i:i + 16].mean()
    averaged_df = pd.concat([averaged_df, avg_rows], axis=1, ignore_index=True)
print(len(result_df))

"""
start_index = (8*15+1)+16*2
for rows, count in patterns:
    for _ in range(len(result_df)):
        avg_rows = result_df.iloc[start_index:start_index + rows].mean()
        averaged_df = pd.concat([averaged_df, avg_rows], axis=1, ignore_index=True)
        start_index += rows*count
"""
# Transpose the result to have rows as samples and columns as features
averaged_df = averaged_df.T

output_averaged_excel_path = 'Flowbot_Post_processing/output_averaged_cleaned_airflow_data.xlsx'
averaged_df.to_excel(output_averaged_excel_path, index=False)

output_excel_path = 'Flowbot_Post_processing/cleaned_airflow_data.xlsx'
result_df.to_excel(output_excel_path, index=False)

# Print a message indicating where the Excel file is saved
print(f"Modified DataFrame saved as {output_excel_path}")