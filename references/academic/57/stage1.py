import numpy as np
import json
import os
from scipy import stats
import pandas as pd

def compute_data():
    # 1. Data Preparation
    data = {
        'DMSO': [743, 799, 1143, 728],
        '40 nM': [370, 311, 245, 298],
        '100 nM': [357, 342, 247, 314],
        '200 nM': [645, 316, 291, 352],
        '1 μM (LY)': [584, 757, 600, 835],  # Renamed to distinguish from MK 1uM
        '5 μM': [567, 566, 504, 517],
        '10 μM': [513, 530, 521, 451],
        '0.2 μM': [2874, 2719, 2494, 2903],
        '1 μM (MK)': [3053, 2862, 2556, 2965] # Renamed to distinguish from LY 1uM
    }

    # Order corresponding to plot
    order = [
        'DMSO', '40 nM', '100 nM', '200 nM', 
        '1 μM (LY)', '5 μM', '10 μM', 
        '0.2 μM', '1 μM (MK)'
    ]

    # Calculate statistics
    means = {}
    stds = {}
    p_values = {}
    
    dmso_vals = data['DMSO']
    
    for key, vals in data.items():
        means[key] = np.mean(vals)
        stds[key] = np.std(vals, ddof=1) # Using sample std usually
        
    # Calculate specific P-values for annotations
    p_values['DMSO_vs_40nM'] = stats.ttest_ind(dmso_vals, data['40 nM'])[1]
    p_values['DMSO_vs_100nM'] = stats.ttest_ind(dmso_vals, data['100 nM'])[1]
    p_values['DMSO_vs_200nM'] = stats.ttest_ind(dmso_vals, data['200 nM'])[1]
    p_values['DMSO_vs_10uM'] = stats.ttest_ind(dmso_vals, data['10 μM'])[1]
    p_values['DMSO_vs_1uM_MK'] = stats.ttest_ind(dmso_vals, data['1 μM (MK)'])[1]

    # Prepare data for JSON
    scr_data = {
        "data": data,
        "order": order
    }

    der_data = {
        "means": means,
        "stds": stds,
        "p_values": p_values
    }

    output_json = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Ensure output directory exists
    output_dir = "bench/ground_truth_code/nature_1_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, "57.json")
    
    with open(output_path, "w") as f:
        json.dump(output_json, f, indent=4)
        
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    compute_data()
