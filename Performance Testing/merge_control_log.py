import psychrolib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Constants
TIME_THRESHOLD_SECONDS = 5
INPUT_PATH = 'Performance Testing/Input csv/'
OUTPUT_PATH = 'Performance Testing/Output excel files/'

# Setting unit system for psychrolib
psychrolib.SetUnitSystem(psychrolib.SI)

# Function to parse and clean data
def prepare_dataframe(file_path, time_format, timestamp_col_index=1):
    df = pd.read_csv(file_path, delimiter='\t')
    df.iloc[:, 2:] = df.iloc[:, 2:].apply(pd.to_numeric, errors='coerce')
    df['valid_times'] = pd.to_datetime(df.iloc[:, timestamp_col_index], format=time_format, errors='coerce')
    df['valid_times'] = df['valid_times'].dt.time
    return df

# Read and prepare the first dataframe
df = prepare_dataframe(INPUT_PATH + 'test18.txt', '%H:%M:%S')
print(df['valid_times'])

# Read and prepare the second dataframe
new_df = prepare_dataframe(INPUT_PATH + 'test18_log.txt', '%m/%d/%Y %I:%M:%S %p')
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

# Save the merged dataframe to a new Excel file
output_file = OUTPUT_PATH + 'updated_data_with_merged_columns.xlsx'
df.to_excel(output_file, index=False)

print("Data merged and saved to", output_file)