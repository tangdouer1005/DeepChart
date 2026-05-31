import sys
import io
import pandas as pd
import numpy as np
import json

# ---------------------------------------------------------
# 1. Source Data Embedding
# ---------------------------------------------------------
csv_data = """
| Station | PM_size | Site_type | Site_topography | Country | Date_start | Date_end | N_samples | OP_AA_v_mean | OP_AA_v_SD | PM_mass_mean | PM_mass_SD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| nan | nan | nan | nan | nan | nan | nan | nan | nmol min-1 m-3 | nmol min-1 m-3 | µg m-3 | µg m-3 |
| ATH | PM10 | Urban | Other | GR | 2022-06-23 | 2023-12-06 | 147 | 2.2 | 2.65 | 31.99 | 14.89 |
| PASSY | PM10 | Suburban | Valley | FR | 2013-11-14 | 2018-03-02 | 437 | 3.02 | 3.79 | 29.19 | 18.4 |
| KRAK | PM10 | Urban | Other | PL | 2018-01-23 | 2018-09-27 | 63 | 1.48 | 1.19 | 28.69 | 18.9 |
| STG-cle | PM10 | Traffic | Other | FR | 2013-04-11 | 2020-01-03 | 147 | 2.54 | 3.26 | 27.87 | 14.58 |
| RBX | PM10 | Traffic | Other | FR | 2013-01-20 | 2014-05-26 | 159 | 2.07 | 1.41 | 27.8 | 15.26 |
| GSY | PM10 | Industrial | Coastal | FR | 2018-01-01 | 2020-06-29 | 133 | 1.05 | 0.86 | 27.05 | 14.6 |
| LENS | PM10 | Urban | Other | FR | 2011-03-09 | 2012-03-06 | 116 | 1.02 | 1.13 | 25.86 | 14.74 |
| ROUEN | PM10 | Urban | Other | FR | 2013-01-02 | 2014-03-30 | 135 | 1.46 | 1.49 | 25.39 | 13.88 |
| NOGENT | PM10 | Urban | Other | FR | 2013-01-02 | 2018-05-22 | 199 | 2.07 | 2.3 | 24.88 | 13.72 |
| CHAM | PM10 | Urban | Valley | FR | 2013-11-02 | 2014-10-31 | 98 | 2.3 | 2.69 | 23.47 | 12.72 |
| BCN | PM10 | Urban | Coastal | ES | 2018-01-03 | 2023-12-02 | 270 | 1.56 | 0.88 | 23.31 | 8.94 |
| NICE | PM10 | Urban | Coastal | FR | 2014-07-11 | 2018-07-06 | 110 | 0.99 | 0.62 | 22.88 | 7.72 |
| FSM | PM10 | Industrial | Coastal | FR | 2018-02-13 | 2018-09-23 | 29 | 1.13 | 0.84 | 21.89 | 7.84 |
| PARIS-lh | PM10 | Urban | Other | FR | 2022-04-07 | 2023-09-26 | 386 | 1.41 | 1.01 | 20.74 | 13.22 |
| PDB | PM10 | Industrial | Coastal | FR | 2014-06-01 | 2018-11-10 | 139 | 0.59 | 0.5 | 20.74 | 7.05 |
| CALAIS | PM10 | Industrial | Coastal | FR | 2021-02-01 | 2021-06-20 | 139 | 1.42 | 1.07 | 20.5 | 9.21 |
| TAL | PM10 | Urban | Other | FR | 2012-03-01 | 2019-11-03 | 235 | 1.17 | 1.25 | 20.05 | 10.98 |
| BERN | PM10 | Traffic | Other | CH | 2013-01-01 | 2020-12-31 | 738 | 3.71 | 1.71 | 19.42 | 10.22 |
| PARIS-lcpp | PM10 | Urban | Other | FR | 2020-04-21 | 2021-09-22 | 184 | 1.52 | 1.22 | 19.4 | 9.26 |
| LYON | PM10 | Urban | Other | FR | 2019-01-02 | 2019-12-31 | 122 | 1.5 | 1.3 | 19.32 | 12.19 |
| GRE-fr | PM10 | Urban | Valley | FR | 2013-01-02 | 2022-05-12 | 1351 | 1.53 | 1.58 | 18.9 | 10.23 |
| MRS-lcp | PM10 | Urban | Coastal | FR | 2015-01-11 | 2024-02-29 | 271 | 1.04 | 0.8 | 18.62 | 8.09 |
| ARREST | PM10 | Rural | Other | FR | 2021-02-01 | 2021-06-20 | 140 | 1.4 | 1.38 | 18.58 | 8.89 |
| MARNAZ | PM10 | Rural | Valley | FR | 2013-11-02 | 2014-10-31 | 93 | 1.57 | 2.02 | 18.49 | 12.28 |
| AIX | PM10 | Urban | Other | FR | 2013-08-02 | 2014-07-13 | 59 | 1.76 | 1.75 | 18.39 | 10.21 |
| ZURICH | PM10 | Urban | Other | CH | 2011-05-24 | 2019-05-29 | 204 | 2.03 | 1.53 | 18.38 | 12.57 |
| GRE-cb | PM10 | Urban | Valley | FR | 2017-02-28 | 2021-07-10 | 247 | 1.48 | 1.32 | 18.08 | 9.39 |
| COURMAY | PM10 | Rural | Valley | IT | 2023-08-12 | 2024-01-09 | 67 | 0.55 | 0.4 | 17.58 | 12.9 |
| DIEPPE | PM10 | Rural | Coastal | FR | 2021-02-11 | 2021-06-29 | 137 | 0.54 | 0.53 | 16.72 | 8.3 |
| MGD | PM10 | Rural | Valley | CH | 2013-01-04 | 2019-05-29 | 240 | 1.78 | 1.92 | 16.7 | 10.6 |
| RDAM | PM10 | Urban | Other | NL | 2023-07-26 | 2024-02-18 | 56 | 1.43 | 0.71 | 16.21 | 4.17 |
| PLOURZ | PM10 | Rural | Other | FR | 2023-03-10 | 2024-05-20 | 171 | 0.23 | 0.22 | 15.73 | 8.13 |
| KANAL | PM10 | Industrial | Valley | SI | 2020-11-12 | 2021-11-16 | 120 | 2.64 | 3.36 | 15.62 | 11.65 |
| LHV | PM10 | Industrial | Coastal | FR | 2021-02-01 | 2021-06-16 | 136 | 1.17 | 0.96 | 15.33 | 7.37 |
| BOSSONS | PM10 | Traffic | Other | FR | 2023-08-12 | 2024-01-09 | 96 | 2.15 | 1.34 | 14.67 | 7.19 |
| VIF | PM10 | Suburban | Other | FR | 2017-02-28 | 2021-07-10 | 253 | 1.27 | 1.52 | 14.32 | 9.34 |
| BASEL | PM10 | Suburban | Other | CH | 2018-06-03 | 2019-05-29 | 90 | 1.24 | 1.09 | 13.97 | 9.26 |
| PAYRN | PM10 | Rural | Other | CH | 2013-01-01 | 2019-05-29 | 103 | 0.71 | 0.49 | 13.49 | 8.31 |
| MSY | PM10 | Rural | Other | ES | 2018-01-11 | 2019-03-27 | 106 | 0.41 | 0.25 | 12.82 | 6.24 |
| OPE | PM10 | Rural | Other | FR | 2017-06-13 | 2020-12-29 | 200 | 0.4 | 0.47 | 9.54 | 6.54 |
| SRJV | PM2.5 | Urban | Valley | BA | 2022-08-20 | 2023-03-01 | 103 | 2.96 | 3.43 | 32.69 | 22.95 |
| ATH | PM2.5 | Urban | Coastal | GR | 2022-01-07 | 2023-12-06 | 152 | 1.94 | 2.22 | 24.7 | 16.61 |
| BCN | PM2.5 | Urban | Coastal | ES | 2018-01-03 | 2023-02-28 | 197 | 0.89 | 0.54 | 17.48 | 6.32 |
| BDP | PM2.5 | Urban | Other | HU | 2017-10-18 | 2018-08-01 | 61 | 2.09 | 1.98 | 15.03 | 8.69 |
| BERN | PM2.5 | Traffic | Other | CH | 2013-01-01 | 2020-12-29 | 644 | 1.35 | 0.75 | 12.61 | 7.52 |
| PARIS-lcpp | PM2.5 | Urban | Other | FR | 2020-11-07 | 2021-09-22 | 69 | 0.85 | 0.79 | 12.51 | 7.26 |
| LILLE | PM2.5 | Urban | Other | FR | 2023-04-03 | 2024-04-01 | 121 | 0.68 | 0.67 | 11.19 | 6.82 |
| ZURICH | PM2.5 | Urban | Other | CH | 2018-06-03 | 2019-05-29 | 90 | 0.82 | 0.56 | 10.8 | 6.97 |
| MGD | PM2.5 | Rural | Valley | CH | 2014-01-03 | 2019-05-29 | 153 | 1.13 | 1.45 | 10.61 | 7.2 |
| BASEL | PM2.5 | Suburban | Other | CH | 2018-06-03 | 2019-05-29 | 90 | 0.68 | 0.86 | 10.6 | 7.76 |
| PARIS-lh | PM2.5 | Urban | Other | FR | 2020-06-24 | 2023-09-26 | 806 | 0.73 | 0.58 | 10.48 | 6.27 |
| PAYRN | PM2.5 | Rural | Other | CH | 2013-01-01 | 2019-05-29 | 102 | 0.39 | 0.34 | 9.68 | 6.73 |
| MSY | PM2.5 | Rural | Other | ES | 2018-01-11 | 2019-03-31 | 107 | 0.34 | 0.22 | 9.62 | 4.68 |
| OPE | PM2.5 | Rural | Other | FR | 2014-01-01 | 2015-12-28 | 102 | 0.23 | 0.22 | 8.79 | 7.16 |
| BCN | PM1 | Urban | Coastal | ES | 2018-01-03 | 2019-03-15 | 94 | 0.66 | 0.33 | 14.71 | 4.91 |
| MRS-lcp | PM1 | Urban | Coastal | FR | 2022-12-10 | 2024-07-26 | 262 | 0.76 | 0.77 | 13.65 | 13.48 |
| KRAK | PM1 | Urban | Other | PL | 2018-01-23 | 2018-09-27 | 63 | 0.71 | 0.69 | 19.73 | 17.28 |
| MSY | PM1 | Rural | Other | ES | 2018-01-11 | 2019-03-31 | 94 | 0.28 | 0.17 | 9.35 | 4.39 |
"""

def load_and_clean_data(csv_str):
    # Pre-process string to remove markdown separator lines
    lines = csv_str.strip().split('\n')
    # Filter out lines that contain only dashes, pipes, colons, spaces
    cleaned_lines = []
    for line in lines:
        # Check if line is a separator line (e.g., |---|---|) 
        if not set(line.strip()) <= {'|', '-', ' ', ':'}:
            cleaned_lines.append(line)
            
    cleaned_csv = '\n'.join(cleaned_lines)
    
    # Read CSV with pipe separator
    df = pd.read_csv(io.StringIO(cleaned_csv), sep="|", skipinitialspace=True)
    
    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Remove "Unnamed" columns (artifacts of markdown table parsing)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Keep a raw copy before filtering
    df_raw = df.copy()

    # Drop the row which contains units (where Station is NaN or 'nan')
    df = df[pd.to_numeric(df['OP_AA_v_mean'], errors='coerce').notna()]
    
    # Convert numeric columns
    numeric_cols = ['OP_AA_v_mean', 'OP_AA_v_SD', 'PM_mass_mean', 'PM_mass_SD']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col])
        
    # Clean string columns
    str_cols = ['Station', 'PM_size', 'Site_type', 'Site_topography']
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()
        
    return df_raw, df

def process_and_save():
    df_raw, df = load_and_clean_data(csv_data)
    
    # Site Type Order (for grouping on x-axis)
    site_order = ['Traffic', 'Urban', 'Industrial', 'Suburban', 'Rural']
    
    # PM Sizes to plot
    pm_sizes = ['PM10', 'PM2.5', 'PM1']
    
    output = {}
    
    for pm in pm_sizes:
        sub_df = df[df['PM_size'] == pm].copy()
        
        # Sort Logic:
        # 1. By Site_type (Traffic -> Urban -> ...)
        # 2. By Topography (Valley first, to group hatched bars)
        # 3. By Station Name (Alphabetical)
        sub_df['Site_type_cat'] = pd.Categorical(sub_df['Site_type'], categories=site_order, ordered=True)
        sub_df['Topo_sort'] = sub_df['Site_topography'].apply(lambda x: 0 if x == 'Valley' else 1)
        
        sub_df = sub_df.sort_values(by=['Site_type_cat', 'Topo_sort', 'Station'], ascending=[True, True, True])
        
        # Convert to list of dicts
        # Need to handle NaN values for JSON serialization
        sub_data = sub_df.to_dict(orient='records')
        output[pm] = sub_data
        
    return df_raw, output

if __name__ == "__main__":
    df_raw, processed_data = process_and_save()
    
    final_output = {
        "scr_data": df_raw.to_dict(orient='records'),
        "der_data": processed_data
    }
    
    with open('bench/ground_truth_code/nature_1_output/77.json', 'w') as f:
        json.dump(final_output, f, indent=4)
