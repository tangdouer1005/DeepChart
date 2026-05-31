import sys
import numpy as np
import json
import os
from scipy import stats

def compute_data():
    # ---------------------------------------------------------
    # 1. Data Preparation
    # ---------------------------------------------------------
    
    days = [0, 2, 4, 6, 8]
    
    # Raw data for Acute (Teff)
    raw_acute = [
        [99, 98, 99, 97],  # Day 0
        [90, 82, 90, 86],  # Day 2
        [84, 75, 75, 83],  # Day 4
        [94, 87, 90, 92],  # Day 6
        [96, 92, 94, 95]   # Day 8
    ]
    
    # Raw data for Chronic (Tex)
    raw_chronic = [
        [99, 98, 99, 97],  # Day 0
        [90, 82, 90, 86],  # Day 2
        [54, 56, 55, 49],  # Day 4
        [62, 60, 50, 50],  # Day 6
        [59, 54, 59, 58]   # Day 8
    ]

    # Calculate Mean and Standard Deviation
    teff_means = [np.mean(row) for row in raw_acute]
    teff_stds = [np.std(row, ddof=1) for row in raw_acute] # Using sample SD
    
    tex_means = [np.mean(row) for row in raw_chronic]
    tex_stds = [np.std(row, ddof=1) for row in raw_chronic]

    # Calculate P-value for Day 8 (index 4)
    _, p_val = stats.ttest_ind(raw_acute[4], raw_chronic[4])
    
    # Prepare data for JSON
    scr_data = {
        "days": days,
        "raw_acute": raw_acute,
        "raw_chronic": raw_chronic
    }
    
    der_data = {
        "teff_means": teff_means,
        "teff_stds": teff_stds,
        "tex_means": tex_means,
        "tex_stds": tex_stds,
        "p_val": p_val
    }

    output_json = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Ensure output directory exists
    output_dir = "bench/ground_truth_code/nature_1_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, "51.json")
    
    with open(output_path, "w") as f:
        json.dump(output_json, f, indent=4)
        
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    compute_data()
