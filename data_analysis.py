import pandas as pd
import os

# Define the directory containing the CSV files
directory_path = 'datasets'

# List all files in the directory
files = os.listdir(directory_path)

# Filter out CSV files
csv_files = [file for file in files if file.endswith('.csv')]
# print(csv_files)

# Read all CSV files into a dictionary of DataFrames
dataframes = {file: pd.read_csv(os.path.join(directory_path, file)) for file in csv_files}

file_names = ['40percent.csv', '60percent.csv', '80percent.csv', '100percent.csv']

for file, dataframe in dataframes.items():
    print(file)
    print("-"*20)

    count_t_state = (dataframe['larynx_T_state__patient'] != '*').sum()
    print(f"{count_t_state} cases patients have the T-state")

    t_state = ['T0', 'Tis', 'T1', 'T1a', 'T1b', 'T2', 'T3', 'T4a', 'T4b', 'absurd']
    for state in t_state:
        count_state = (dataframe['larynx_T_state__patient'] == state).sum()
        print(f"\t{count_state} cases patients have the {state} state")



    count_n_state = (dataframe['N_state__patient'] != '*').sum()
    print(f"{count_n_state} cases patients have the N-state")

    n_state = ['N0', 'N1', 'N2a', 'N2b', 'N2c', 'N3', 'absurd']
    for state in n_state:
        count_state = (dataframe['N_state__patient'] == state).sum()
        print(f"\t{count_state} cases patients have the {state} state")



    count_m_state = (dataframe['M_state__patient'] != '*').sum()
    print(f"{count_m_state} cases patients have the M-state")

    m_state = ['M0', 'M1']
    for state in m_state:
        count_state = (dataframe['M_state__patient'] == state).sum()
        print(f"\t{count_state} cases patients have the {state} state")

    print()


# Display the list of CSV files and their DataFrames to the user
# print(csv_files, dataframes.keys())
