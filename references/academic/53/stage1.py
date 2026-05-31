import pandas as pd
import numpy as np
import json
import os
from scipy import stats

def compute_data():
    # 1. Data Preparation
    data = {
        'DMSO': [62, 65, 65, 59],
        'Rapamycin_40nM': [70, 67, 66, 64],
        'Rapamycin_100nM': [71, 72, 71, 68],
        'Rapamycin_200nM': [70, 70, 72, 66],
        'LY294002_1uM': [66, 67, 66, 62],
        'LY294002_5uM': [74, 74, 68, 63],
        'LY294002_10uM': [80, 72, 69, 65],
        'MK2206_0.2uM': [84, 85, 85, 85],
        'MK2206_1uM': [80, 80, 84, 79]
    }
    
    df = pd.DataFrame(data)
    
    # Calculate means and standard deviations
    means = df.mean().to_dict()
    stds = df.std().to_dict()
    
    # Calculate P-values
    p_values = {}
    
    def calculate_p_val(group1, group2):
        _, p_val = stats.ttest_ind(data[group1], data[group2])
        return p_val

    p_values['DMSO_vs_Rapamycin_40nM'] = calculate_p_val('DMSO', 'Rapamycin_40nM')
    p_values['DMSO_vs_Rapamycin_100nM'] = calculate_p_val('DMSO', 'Rapamycin_100nM')
    p_values['DMSO_vs_Rapamycin_200nM'] = calculate_p_val('DMSO', 'Rapamycin_200nM')
    p_values['DMSO_vs_LY294002_1uM'] = calculate_p_val('DMSO', 'LY294002_1uM')
    p_values['DMSO_vs_MK2206_0.2uM'] = calculate_p_val('DMSO', 'MK2206_0.2uM')
    
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
        
    output_path = os.path.join(output_dir, "53.json")
    
    with open(output_path, "w") as f:
        json.dump(output_json, f, indent=4)
        
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    compute_data()
