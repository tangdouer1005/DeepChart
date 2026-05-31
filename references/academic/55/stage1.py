import pandas as pd
import numpy as np
import json
import os
from scipy import stats

def compute_data():
    # 1. Source Data Preparation
    data = {
        'DMSO': [33.9, 34.6, 42.6, 39.4],
        'Rap_40nM': [33.7, 40.1, 35.5, 37.1],
        'Rap_100nM': [35.7, 36.2, 36.8, 36.0],
        'Rap_200nM': [37.2, 36.7, 37.6, 37.7],
        'LY_1uM': [31.7, 40.0, 37.7, 40.1],
        'LY_5uM': [41.5, 42.6, 43.4, 40.3],
        'LY_10uM': [34.4, 38.7, 39.9, 37.4],
        'MK_0.2uM': [50.3, 48.4, 49.7, 51.7],
        'MK_1uM': [46.8, 41.7, 46.0, 47.6]
    }
    
    df = pd.DataFrame(data)
    
    # Calculate Means and Standard Deviations
    means = df.mean().to_dict()
    stds = df.std().to_dict()
    
    # Calculate P-values
    p_values = {}
    
    def calculate_p_val(group1, group2):
        _, p_val = stats.ttest_ind(data[group1], data[group2])
        return p_val

    p_values['DMSO_vs_MK_0.2uM'] = calculate_p_val('DMSO', 'MK_0.2uM')
    p_values['DMSO_vs_MK_1uM'] = calculate_p_val('DMSO', 'MK_1uM')
    
    # Prepare data for JSON
    scr_data = data
    der_data = {
        "means": means,
        "stds": stds,
        "p_values": p_values,
        "columns": list(data.keys())
    }
    
    output_json = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Ensure output directory exists
    output_dir = "bench/ground_truth_code/nature_1_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, "55.json")
    
    with open(output_path, "w") as f:
        json.dump(output_json, f, indent=4)
        
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    compute_data()
