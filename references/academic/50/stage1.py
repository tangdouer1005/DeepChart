import numpy as np
import pandas as pd
import json
import os
from scipy import stats

def compute_data(output_json_path):
    # ---------------------------------------------------------
    # 1. Data Preparation
    # ---------------------------------------------------------
    # Raw data extracted from the provided Markdown table (Proliferation section)
    # Acute = Teff, Chronic = Tex
    
    days = np.array([0, 2, 4, 6, 8])
    
    # Acute (Teff) raw data columns
    acute_data = np.array([
        [1, 1, 1, 1],           # Day 0
        [1.34, 1.09, 1.4, 1],   # Day 2
        [8.64, 5.16, 7.21, 5.45], # Day 4
        [26.8, 17.3, 19.3, 20.6], # Day 6
        [97.8, 70, 91.7, 74]      # Day 8
    ])
    
    # Chronic (Tex) raw data columns
    chronic_data = np.array([
        [1, 1, 1, 1],           # Day 0
        [1.34, 1.09, 1.4, 1],   # Day 2
        [2.48, 2.47, 2.16, 2.1],  # Day 4
        [6.12, 5.8, 4.61, 4.62],  # Day 6
        [11.9, 11.7, 12.3, 13.5]  # Day 8
    ])

    # Calculate Mean and Standard Deviation
    # Using ddof=1 for sample standard deviation
    teff_mean = np.mean(acute_data, axis=1)
    teff_std = np.std(acute_data, axis=1, ddof=1)
    
    tex_mean = np.mean(chronic_data, axis=1)
    tex_std = np.std(chronic_data, axis=1, ddof=1)

    # Calculate P-value for Day 8
    _, p_val = stats.ttest_ind(acute_data[-1], chronic_data[-1], equal_var=True)

    # Construct JSON data
    data_list = []
    for i in range(len(days)):
        data_list.append({
            "day": int(days[i]),
            "Teff_mean": float(teff_mean[i]),
            "Teff_std": float(teff_std[i]),
            "Tex_mean": float(tex_mean[i]),
            "Tex_std": float(tex_std[i])
        })

    scr_data = {
        "acute_data": acute_data.tolist(),
        "chronic_data": chronic_data.tolist(),
        "days": days.tolist()
    }

    der_data = {
        "data": data_list,
        "p_value": float(p_val)
    }

    output_json = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

    with open(output_json_path, 'w') as f:
        json.dump(output_json, f, indent=4)
    print(f"Data saved to {output_json_path}")

if __name__ == "__main__":
    output_json = "bench/ground_truth_code/nature_1_output/50.json"
    compute_data(output_json)
