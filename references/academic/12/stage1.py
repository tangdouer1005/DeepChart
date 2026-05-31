import sys
import io
import pandas as pd
import numpy as np
import json

def compute_data(output_path):
    # 1. Load Source Data
    csv_data = """Unnamed: 0,control,Unnamed: 2,Unnamed: 3,K2,Unnamed: 5,Unnamed: 6,K10,Unnamed: 8,Unnamed: 9,K50,Unnamed: 11,Unnamed: 12
Pyruvate,0.223058,0.210762,0.149665,0.379206,0.293885,0.464718,0.442063,0.254092,0.40376,0.614279,0.562326,0.429538
Citrate,0.258809,0.309936,0.356968,0.30788,0.325941,0.289485,0.296881,0.274078,0.282906,0.279333,0.314928,0.289988
Glutamate,0.367758,0.344181,0.376461,0.347516,0.379106,0.342397,0.314315,0.281335,0.302929,0.284958,0.332328,0.30411
Succinate,0.382252,0.328351,0.398149,0.360708,0.386626,0.357401,0.335758,0.298984,0.327873,0.297441,0.350486,0.323474
Fumarate,0.097648,0.104257,0.106706,0.0843699,0.0890736,0.0680718,0.0878835,0.0631375,0.0819516,0.0646776,0.0777998,0.0697304
Malate,0.0979276,0.11186,0.113111,0.0915563,0.0970604,0.069992,0.0949667,0.0724992,0.0904031,0.0690075,0.0819516,0.0725173
Aspartic acid,0.140544,0.158885,0.161802,0.132497,0.130524,0.105984,0.137745,0.0969118,0.124096,0.10052,0.12154,0.103243
"""
    
    # Read data
    df = pd.read_csv(io.StringIO(csv_data))
    
    # 2. Data Preprocessing
    # Set index to metabolite names
    df = df.set_index('Unnamed: 0')
    
    # Rename index to match the chart (lowercase, specific mapping)
    index_mapping = {
        'Pyruvate': 'pyruvate',
        'Citrate': 'citrate',
        'Glutamate': 'glutamate',
        'Succinate': 'succinate',
        'Fumarate': 'fumarate',
        'Malate': 'malate',
        'Aspartic acid': 'aspartate'
    }
    df = df.rename(index=index_mapping)
    
    # Calculate Z-score row-wise (normalized to vehicle control group)
    # Normalized to control means: (x - mean(control)) / std(all)
    def zscore_to_control(row):
        # Control samples are the first 3 columns
        control_mean = row.iloc[0:3].mean()
        global_std = row.std() 
        return (row - control_mean) / global_std

    df_zscore = df.apply(zscore_to_control, axis=1)

    # Convert to JSON compatible format
    # We will save the zscore dataframe
    output_data = {
        "scr_data": {
            "index": df.index.tolist(),
            "columns": df.columns.tolist(),
            "data": df.values.tolist()
        },
        "der_data": {
            "index": df_zscore.index.tolist(),
            "columns": df_zscore.columns.tolist(),
            "data": df_zscore.values.tolist()
        }
    }
    
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_2_output/12.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compute_data(output_file)
