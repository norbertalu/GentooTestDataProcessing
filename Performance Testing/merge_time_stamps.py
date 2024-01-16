import psychrolib
import pandas as pd
from helper_functions import U_config_or_not
import numpy as np
import matplotlib.pyplot as plt
psychrolib.SetUnitSystem(psychrolib.SI)
#read csv
df = pd.read_csv('Performance Testing/Input csv/test18.txt', delimiter='\t')
df.iloc[:, 2:] = df.iloc[:, 2:].apply(pd.to_numeric, errors='coerce')
df['valid_times'] = pd.to_datetime(df.iloc[:, 1], format='%H:%M:%S', errors='coerce')
df['valid_times'] = df['valid_times'].dt.time 
print(df['valid_times'])

new_df = pd.read_csv('Performance Testing/Input csv/test18_log.txt',delimiter='\t') 
new_df.iloc[:, 2:] = new_df.iloc[:, 2:].apply(pd.to_numeric, errors='coerce')
# Convert the timestamp column to a common format
new_df['valid_times'] = pd.to_datetime(new_df.iloc[:,1], format='%m/%d/%Y %I:%M:%S %p', errors = 'coerce')
new_df['valid_times'] = new_df['valid_times'].dt.time 

print(new_df['valid_times'])

#df.set_index('valid_times', inplace=True)
#new_df.set_index('valid_times', inplace=True)

new_df = new_df.rename(columns={
    new_df.columns[24]: 'Superheat',
    new_df.columns[25]: 'Subcool',
    new_df.columns[26]: 'Num_Cycles',
    new_df.columns[27]: 'Compressor_En',
    new_df.columns[28]: 'Compressor',
    new_df.columns[29]: 'Fan_En',
    new_df.columns[30]: 'Process_Fan',
    new_df.columns[31]: 'Regen_Fan',
    new_df.columns[32]: 'EEV',
    new_df.columns[33]: 'Left_Right',
    new_df.columns[34]: 'Cooling_Heating',
    new_df.columns[35]: 'Automode_En'
})

columns_to_merge = ['Superheat', 'Subcool', 'Num_Cycles', 'Compressor_En', 'Compressor', 
                     'Fan_En', 'Process_Fan', 'Regen_Fan', 'EEV', 'Left_Right', 
                     'Cooling_Heating', 'Automode_En']
new_df[columns_to_merge] = new_df[columns_to_merge].apply(pd.to_numeric, errors='coerce')
print(new_df[columns_to_merge])
print(df)
# Perform the merge based on a time difference of 5 seconds
merged_dfs = []

# Iterate over rows in df and extract selected columns from new_df with timestamp within 5 seconds

for index, row in df.iterrows():
    time_difference = (new_df['valid_times'].apply(lambda x: x.hour * 3600 + x.minute * 60 + x.second) -
                       row['valid_times'].hour * 3600 -
                       row['valid_times'].minute * 60 -
                       row['valid_times'].second)
    
    close_rows = new_df[abs(time_difference) <= 5]
    
    if not close_rows.empty:
        selected_columns = close_rows[columns_to_merge]
        for col in columns_to_merge:
            df.at[index, col] = selected_columns.iloc[0][col]  # Add the merged column to df


# Save the merged dataframe to a new Excel file
df.to_excel('Performance Testing/Output excel files/updated_data_with_merged_columns.xlsx', index=False)