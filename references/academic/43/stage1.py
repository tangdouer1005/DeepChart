import numpy as np
import pandas as pd
import json
import os

def compute_data(output_json_path):
    # 1. Data Preparation
    # Transcribing the provided source data exactly
    current_density = [50, 100, 200, 300, 400, 500, 600, 700, 800]

    # AEM Data (Voltage replicates)
    aem_data = np.array([
        [-2.19, -2.21, -2.18], # 50
        [-2.29, -2.32, -2.30], # 100
        [-2.42, -2.45, -2.43], # 200
        [-2.51, -2.55, -2.53], # 300
        [-2.60, -2.64, -2.62], # 400
        [-2.69, -2.73, -2.70], # 500
        [-2.76, -2.80, -2.77], # 600
        [-2.83, -2.86, -2.83], # 700
        [-2.89, -2.92, -2.89]  # 800
    ])

    # Separator Data (Voltage replicates)
    separator_data = np.array([
        [-2.11, -2.10, -2.13], # 50
        [-2.21, -2.19, -2.20], # 100
        [-2.29, -2.27, -2.30], # 200
        [-2.37, -2.34, -2.38], # 300
        [-2.44, -2.42, -2.46], # 400
        [-2.50, -2.48, -2.53], # 500
        [-2.56, -2.54, -2.60], # 600
        [-2.61, -2.57, -2.63], # 700
        [-2.65, -2.60, -2.66]  # 800
    ])

    # Calculate Mean and Standard Deviation
    aem_mean = np.mean(aem_data, axis=1)
    aem_std = np.std(aem_data, axis=1)

    sep_mean = np.mean(separator_data, axis=1)
    sep_std = np.std(separator_data, axis=1)

    output_data = []
    for i in range(len(current_density)):
        output_data.append({
            "Current_Density": current_density[i],
            "AEM_mean": aem_mean[i],
            "AEM_std": aem_std[i],
            "Separator_mean": sep_mean[i],
            "Separator_std": sep_std[i]
        })

    scr_data = []
    for i in range(len(current_density)):
        scr_data.append({
            "Current_Density": current_density[i],
            "AEM_reps": aem_data[i].tolist(),
            "Separator_reps": separator_data[i].tolist()
        })

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
    output_json = "bench/ground_truth_code/nature_1_output/43.json"
    compute_data(output_json)
