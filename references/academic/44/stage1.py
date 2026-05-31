import pandas as pd
import numpy as np
import json
import os

def compute_data(output_json_path):
    # 2. Data Preparation
    # Raw data transcribed exactly from the provided source table
    
    # IrOx Data
    irox_raw = {
        'current_density': [50, 100, 200, 300, 400, 500, 600, 700, 800],
        'r1': [-2.11, -2.21, -2.29, -2.37, -2.44, -2.50, -2.56, -2.61, -2.65],
        'r2': [-2.10, -2.19, -2.27, -2.34, -2.42, -2.48, -2.54, -2.57, -2.60],
        'r3': [-2.13, -2.20, -2.30, -2.38, -2.46, -2.53, -2.60, -2.63, -2.66]
    }
    
    # NiFe-B Data
    nife_raw = {
        'current_density': [50, 100, 200, 300, 400, 500, 600, 700, 800],
        'r1': [-1.95, -2.02, -2.15, -2.23, -2.28, -2.33, -2.37, -2.42, -2.46],
        'r2': [-1.95, -2.00, -2.14, -2.21, -2.27, -2.31, -2.35, -2.39, -2.44],
        'r3': [-1.97, -2.04, -2.17, -2.25, -2.30, -2.35, -2.41, -2.46, -2.50]
    }

    # Create DataFrames
    df_irox = pd.DataFrame(irox_raw)
    df_nife = pd.DataFrame(nife_raw)

    # Calculate Mean and Std Dev (using ddof=1 for sample standard deviation)
    # Axis 1 calculates across the replicate columns
    df_irox['mean'] = df_irox[['r1', 'r2', 'r3']].mean(axis=1)
    df_irox['std'] = df_irox[['r1', 'r2', 'r3']].std(axis=1)

    df_nife['mean'] = df_nife[['r1', 'r2', 'r3']].mean(axis=1)
    df_nife['std'] = df_nife[['r1', 'r2', 'r3']].std(axis=1)

    output_data = []
    current_density = df_irox['current_density'].tolist()
    
    for i in range(len(current_density)):
        output_data.append({
            "Current_Density": current_density[i],
            "IrOx_mean": df_irox['mean'][i],
            "IrOx_std": df_irox['std'][i],
            "NiFe-B_mean": df_nife['mean'][i],
            "NiFe-B_std": df_nife['std'][i]
        })

    scr_data = {
        "IrOx": irox_raw,
        "NiFe-B": nife_raw
    }

    output_json = {
        "scr_data": scr_data,
        "der_data": output_data
    }

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

    with open(output_json_path, 'w') as f:
        json.dump(output_json, f, indent=4)
    print(f"Data saved to {output_json_path}")

if __name__ == "__main__":
    output_json = "bench/ground_truth_code/nature_1_output/44.json"
    compute_data(output_json)
