import pandas as pd
import numpy as np
import json
import os
from scipy import stats

def compute_data():
    # 1. Source Data Preparation
    raw_data = {
        'DMSO': [16.4, 18.8, 18.2, 17.6],
        
        # Rapamycin (Columns 2, 3, 4 in source)
        'Rapamycin_40nM':  [32.0, 28.7, 30.1, 28.7],
        'Rapamycin_100nM': [31.6, 31.1, 31.5, 27.2],
        'Rapamycin_200nM': [30.5, 30.4, 32.1, 29.5],
        
        # LY294002 (Columns 8, 9, 10 in source - Note: Chart places LY before MK)
        'LY294002_1uM':  [19.0, 19.7, 20.3, 19.1],
        'LY294002_5uM':  [32.4, 31.1, 28.5, 27.8],
        'LY294002_10uM': [44.3, 40.8, 43.6, 39.8],
        
        # MK2206 (Columns 5, 6, 7 in source)
        'MK2206_0.2uM': [29.9, 30.3, 30.8, 29.0],
        'MK2206_1uM':   [27.8, 30.5, 35.3, 30.4],
        'MK2206_5uM':   [1.59, 1.34, 1.49, 1.77]
    }

    # Convert to DataFrame for easier handling
    df = pd.DataFrame(raw_data)
    
    # Calculate Means and Standard Deviations
    means = df.mean().to_dict()
    stds = df.std().to_dict()
    
    # Calculate P-value
    # Comparing DMSO (raw_data['DMSO']) vs MK2206 5uM (raw_data['MK2206_5uM'])
    _, p_val = stats.ttest_ind(raw_data['DMSO'], raw_data['MK2206_5uM'])
    
    # Prepare data for JSON
    scr_data = raw_data
    der_data = {
        "means": means,
        "stds": stds,
        "p_val": p_val,
        "columns": list(raw_data.keys())
    }
    
    output_json = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Ensure output directory exists
    output_dir = "bench/ground_truth_code/nature_1_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, "52.json")
    
    with open(output_path, "w") as f:
        json.dump(output_json, f, indent=4)
        
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    compute_data()
