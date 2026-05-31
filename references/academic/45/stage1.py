import numpy as np
import json
import os

def compute_data(output_json_path):
    # 2. Source Data
    # Hardcoding the data from the provided Markdown table to ensure integrity.
    # Structure: Current Density (mA/cm2) -> [Rep1, Rep2, Rep3]
    
    data_20c = {
        50:  [-1.95, -1.95, -1.97],
        100: [-2.02, -2.00, -2.04],
        200: [-2.15, -2.14, -2.17],
        300: [-2.23, -2.21, -2.25],
        400: [-2.28, -2.27, -2.30],
        500: [-2.33, -2.31, -2.35],
        600: [-2.37, -2.35, -2.41],
        700: [-2.42, -2.39, -2.46],
        800: [-2.46, -2.44, -2.50]
    }

    data_35c = {
        50:  [-1.85, -1.85, -1.87],
        100: [-1.93, -1.93, -1.95],
        200: [-2.00, -2.01, -2.02],
        300: [-2.07, -2.08, -2.08],
        400: [-2.13, -2.14, -2.14],
        500: [-2.17, -2.18, -2.18],
        600: [-2.21, -2.22, -2.22],
        700: [-2.25, -2.26, -2.25],
        800: [-2.30, -2.31, -2.31]
    }

    data_50c = {
        50:  [-1.80, -1.84, -1.83],
        100: [-1.89, -1.90, -1.90],
        200: [-1.95, -1.96, -1.95],
        300: [-2.03, -2.02, -2.01],
        400: [-2.08, -2.09, -2.06],
        500: [-2.13, -2.15, -2.11],
        600: [-2.17, -2.19, -2.15],
        700: [-2.21, -2.23, -2.19],
        800: [-2.24, -2.27, -2.24]
    }

    # Helper function to process data into plotting format (Mean and Std Dev)
    def process_data(raw_data):
        x = sorted(raw_data.keys())
        y_mean = []
        y_std = []
        for val in x:
            replicates = raw_data[val]
            y_mean.append(np.mean(replicates))
            y_std.append(np.std(replicates, ddof=1)) # Using sample standard deviation
        return x, y_mean, y_std

    x_20, y_20, err_20 = process_data(data_20c)
    x_35, y_35, err_35 = process_data(data_35c)
    x_50, y_50, err_50 = process_data(data_50c)

    output_data = []
    # Assuming x_20, x_35, x_50 are identical (which they are, based on keys)
    for i in range(len(x_20)):
        output_data.append({
            "Current_Density": x_20[i],
            "20C_mean": y_20[i],
            "20C_std": err_20[i],
            "35C_mean": y_35[i],
            "35C_std": err_35[i],
            "50C_mean": y_50[i],
            "50C_std": err_50[i]
        })

    scr_data = {
        "data_20c": data_20c,
        "data_35c": data_35c,
        "data_50c": data_50c
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
    output_json = "bench/ground_truth_code/nature_1_output/45.json"
    compute_data(output_json)
