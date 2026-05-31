import sys
import io
import numpy as np
import pandas as pd
import json
from scipy import stats

# ---------------------------------------------------------
# 1. Source Data Embedding
# ---------------------------------------------------------
raw_data = """
| Electrolyte        | SSL ratio (%)                                | Li+ binding energy (eV)   | Ionic conductivity (mS cm-1)   | Initial interfacial resistance (Ohm)   |   SEI thickness (nm) |   F ratio (%) |   C ratio (%) |   O ratio (%) |   15th Rinterface (ohm) |   15th overpotential (V) |   Thickness of deposited Li (μm) |   Cycle life |
|:-------------------|:---------------------------------------------|:--------------------------|:-------------------------------|:---------------------------------------|---------------------:|--------------:|--------------:|--------------:|------------------------:|-------------------------:|---------------------------------:|-------------:|
| LiAsF6 electrolyte | 90                                           | -1.10496                  | 0.346                          | 88                                     |              9.8513  |          3.18 |         32.24 |         32.24 |                   21.22 |                    0.22  |                             11.7 |          279 |
| LiPF6 electrolyte  | 80                                           | -1.11207                  | 0.336                          | 71                                     |              8.90335 |          7.99 |         38.74 |         22.7  |                    9.5  |                    0.17  |                             12.3 |          115 |
| LiFSI electrolyte  | 78.33333                                     | -1.19801                  | 0.344                          | 47                                     |             10.2788  |          4.44 |         38.34 |         25.79 |                    6.4  |                    0.14  |                             14.2 |           71 |
| LiTFSI electrolyte | 76.66667                                     | -1.2481                   | 0.322                          | 52                                     |              9.10781 |         14.17 |         29.5  |         22.27 |                    8    |                    0.155 |                             15.8 |           53 |
| LiClO4 electrolyte | 71.66667                                     | -1.22465                  | 0.28                           | 35                                     |              8.86617 |          7.89 |         26.13 |         32.59 |                    4.3  |                    0.25  |                             15.8 |           56 |
| LiBF4 electrolyte  | 75                                           | -1.20247                  | 0.3                            | 24                                     |              9.83271 |          9.65 |         27.63 |         23.13 |                   30.1  |                    0.22  |                             16.1 |           38 |
| LiDFOB electrolyte | 70.4918                                      | -1.36423                  | 0.279                          | 50                                     |             11.7379  |          7.07 |         32.83 |         29.61 |                    6.6  |                    0.16  |                             14.9 |           45 |
| LiNO3 electrolyte  | 68.33333                                     | -1.40999                  | 0.277                          | 52                                     |             17.0074  |          7.47 |         33.73 |         24.44 |                    4.54 |                    0.18  |                             17   |           30 |
| nan                | nan                                          | nan                       | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| nan                | nan                                          | nan                       | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| Electrolyte        | CCD measurement #1 (mA cm-2)                 | measurement #2            | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiAsF6 electrolyte | 36                                           | 36                        | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiPF6 electrolyte  | 32                                           | 28                        | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiFSI electrolyte  | 29                                           | 22                        | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiTFSI electrolyte | 20                                           | 18                        | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiClO4 electrolyte | 26                                           | 23                        | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiBF4 electrolyte  | 21                                           | 17                        | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiDFOB electrolyte | 20                                           | 16                        | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiNO3 electrolyte  | 15                                           | 15                        | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| nan                | nan                                          | nan                       | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| nan                | nan                                          | nan                       | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| Electrolyte        | Average crystallite size measurement #1 (nm) | measurement #2            | measurement #3                 | measurement #4                         |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiAsF6 electrolyte | 2.9                                          | 2.6                       | 2.6                            | 2.7                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiPF6 electrolyte  | 3                                            | 3.3                       | 2.8                            | 3.3                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiFSI electrolyte  | 3.2                                          | 3.1                       | 3.3                            | 3                                      |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiTFSI electrolyte | 3.9                                          | 3.4                       | 3                              | 3.7                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiClO4 electrolyte | 4.1                                          | 4.8                       | 4.2                            | 3.8                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiBF4 electrolyte  | 3.9                                          | 4.1                       | 5.4                            | 4.4                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiDFOB electrolyte | 4.7                                          | 4.5                       | 4.9                            | 5.4                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiNO3 electrolyte  | 5.2                                          | 5.2                       | 6.2                            | 5.3                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
"""

# ---------------------------------------------------------
# 2. Data Processing
# ---------------------------------------------------------

def load_and_clean_data(raw_str):
    # Read the full markdown table structure
    # We use '|' as separator and skip initial/trailing whitespace
    df_raw = pd.read_csv(io.StringIO(raw_str), sep='|', skipinitialspace=True, header=None)
    
    # Clean up column names and drop empty columns (first and last usually empty due to markdown | borders)
    df_raw = df_raw.dropna(axis=1, how='all')
    
    # The data is split into 3 sections by 'nan' rows. 
    # We identify sections by looking for the 'Electrolyte' keyword in the first valid column.
    
    # Find indices where a new table starts
    start_indices = df_raw[df_raw.iloc[:, 0].str.contains("Electrolyte", na=False)].index.tolist()
    
    # Helper to extract a block
    def extract_block(start_row, num_rows):
        block = df_raw.iloc[start_row:start_row+num_rows+1].copy()
        # Set header
        block.columns = block.iloc[0].str.strip()
        block = block[1:] # Drop header row
        # Drop separator row if it exists (starts with :)
        block = block[~block.iloc[:,0].str.contains('---', na=False, regex=False)]
        block = block[~block.iloc[:,0].str.contains(':', na=False, regex=False)]
        return block.reset_index(drop=True)

    # Main Table
    df_main = extract_block(0, 9)
    
    # CCD Table
    ccd_start = start_indices[1]
    df_ccd_raw = extract_block(ccd_start, 9)
    
    # Crystallite Table
    cryst_start = start_indices[2]
    df_cryst_raw = extract_block(cryst_start, 9)

    # --- Process Main Table ---
    cols_main = df_main.columns
    for c in cols_main:
        if c != 'Electrolyte':
            df_main[c] = pd.to_numeric(df_main[c], errors='coerce')
            
    df_main.set_index('Electrolyte', inplace=True)

    # --- Process CCD Table ---
    df_ccd = pd.DataFrame()
    df_ccd['Electrolyte'] = df_ccd_raw['Electrolyte']
    meas_cols = [c for c in df_ccd_raw.columns if 'measurement' in c.lower()]
    for c in meas_cols:
        df_ccd_raw[c] = pd.to_numeric(df_ccd_raw[c], errors='coerce')
    
    df_ccd['J_crit'] = df_ccd_raw[meas_cols].mean(axis=1)
    df_ccd.set_index('Electrolyte', inplace=True)

    # --- Process Crystallite Table ---
    df_cryst = pd.DataFrame()
    df_cryst['Electrolyte'] = df_cryst_raw['Electrolyte']
    meas_cols_c = [c for c in df_cryst_raw.columns if 'measurement' in c.lower()]
    for c in meas_cols_c:
        df_cryst_raw[c] = pd.to_numeric(df_cryst_raw[c], errors='coerce')
        
    df_cryst['Crystallite_size'] = df_cryst_raw[meas_cols_c].mean(axis=1)
    df_cryst.set_index('Electrolyte', inplace=True)

    # --- Merge All ---
    df_final = df_main.join(df_ccd['J_crit']).join(df_cryst['Crystallite_size'])
    
    return df_final

df = load_and_clean_data(raw_data)

# ---------------------------------------------------------
# 3. Prepare Data for Correlation Matrix
# ---------------------------------------------------------

# Map DataFrame columns to Chart Labels and desired order
column_mapping = {
    'SSL ratio (%)': 'SSL ratio',
    'Li+ binding energy (eV)': 'Li+ binding energy',
    'Ionic conductivity (mS cm-1)': 'Ionic conductivity',
    'Initial interfacial resistance (Ohm)': 'Initial R_interface',
    'SEI thickness (nm)': 'SEI thickness',
    'F ratio (%)': 'F%',
    'C ratio (%)': 'C%',
    'O ratio (%)': 'O%',
    '15th Rinterface (ohm)': 'R_interface',
    '15th overpotential (V)': 'eta_15th',
    'J_crit': 'J_crit',
    'Crystallite_size': 'Crystallite size',
    'Thickness of deposited Li (μm)': 'Thickness',
    'Cycle life': 'Cycle performance'
}

# Reorder and rename
ordered_keys = [
    'SSL ratio (%)',
    'Li+ binding energy (eV)',
    'Ionic conductivity (mS cm-1)',
    'Initial interfacial resistance (Ohm)',
    'SEI thickness (nm)',
    'F ratio (%)',
    'C ratio (%)',
    'O ratio (%)',
    '15th Rinterface (ohm)',
    '15th overpotential (V)',
    'J_crit',
    'Crystallite_size',
    'Thickness of deposited Li (μm)',
    'Cycle life'
]

df_chart = df[ordered_keys].copy()
df_chart.columns = [column_mapping[k] for k in ordered_keys]

# Calculate P-values
n_vars = len(df_chart.columns)
p_values = np.zeros((n_vars, n_vars))

for i in range(n_vars):
    for j in range(n_vars):
        if i == j:
            p_values[i, j] = np.nan
        else:
            col1 = df_chart.iloc[:, i]
            col2 = df_chart.iloc[:, j]
            valid = ~np.isnan(col1) & ~np.isnan(col2)
            if np.sum(valid) > 2:
                _, p = stats.pearsonr(col1[valid], col2[valid])
                p_values[i, j] = p
            else:
                p_values[i, j] = 1.0

# Save to JSON
# We'll save the p_values matrix and the column names
output_path = "bench/ground_truth_code/nature_1_output/35.json"

output_json = {
    "scr_data": df_chart.to_dict(orient='records'),
    "der_data": {
        "columns": df_chart.columns.tolist(),
        "p_values": p_values.tolist() # numpy array to list
    }
}

with open(output_path, 'w') as f:
    json.dump(output_json, f, indent=4)
    
print(f"Data saved to {output_path}")
