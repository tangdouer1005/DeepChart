import numpy as np
import json
import os
from scipy import stats

def compute_data():
    # 1. Source Data
    # Organized as a list of lists corresponding to the columns in the provided table
    # Mapping:
    # 0: DMSO
    # 1: Rapamycin 40 nM
    # 2: Rapamycin 100 nM
    # 3: Rapamycin 200 nM
    # 4: LY294002 1 uM
    # 5: LY294002 5 uM
    # 6: LY294002 10 uM
    # 7: MK2206 0.2 uM
    # 8: MK2206 1 uM
    
    data = [
        [3.22, 2.5, 2.29, 2.37],       # DMSO
        [2.15, 1.72, 1.35, 2.07],      # Rap 40 nM
        [1.79, 1.58, 1.35, 1.42],      # Rap 100 nM
        [2.01, 1.51, 1.19, 2.14],      # Rap 200 nM
        [3.42, 3.01, 4.06, 3.32],      # LY 1 uM
        [13, 11.7, 11.9, 11.7],        # LY 5 uM
        [15.8, 16.2, 16.2, 16.1],      # LY 10 uM
        [28, 31.5, 32.7, 32.6],        # MK 0.2 uM
        [78.8, 73.6, 82.3, 83.2]       # MK 1 uM
    ]

    # Calculate Means and Standard Deviations
    means = [np.mean(d) for d in data]
    stds = [np.std(d, ddof=1) for d in data] # Using sample standard deviation

    # Calculate P-value
    # DMSO (index 0) vs MK 1uM (index 8)
    _, p_val = stats.ttest_ind(data[0], data[8])
    
    # Prepare data for JSON
    scr_data = data
    der_data = {
        "means": means,
        "stds": stds,
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
        
    output_path = os.path.join(output_dir, "54.json")
    
    with open(output_path, "w") as f:
        json.dump(output_json, f, indent=4)
        
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    compute_data()
