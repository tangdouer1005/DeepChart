import sys
import json
import numpy as np
import pandas as pd # pandas is not used but was imported in original code

def process_and_extract_data():
    # ---------------------------------------------------------
    # 1. Source Data Preparation
    # ---------------------------------------------------------
    # Raw data extracted from Columns 0-9 of the provided table.
    # 'nan' values are represented as np.nan
    raw_data = {
        'B16-F0': [0.999999823, 1.00032767, 1.000005438, 0.861667086, 1.003190644, 1.136074996, 0.999999998],
        'LN1-18IL': [0.800686, 1.500677, 1.341806, 1.640613, 1.483361, 1.106523, 0.813898],
        'LN7-1112AR': [0.587407, 0.932256, 0.847907, 0.563434468, np.nan, np.nan, np.nan],
        'LN7-1120BL': [1.054753, 1.447167, 1.117306, np.nan, np.nan, np.nan, np.nan],
        'LN7-1134BL': [0.270697051, 0.731263444, 0.744321601, 0.463934401, np.nan, np.nan, np.nan],
        'LN8-1194BR': [0.179749188, 0.782426964, 0.479145444, np.nan, np.nan, np.nan, np.nan],
        'LN8-1198AR': [0.70873371, 1.548417104, 1.414139626, np.nan, np.nan, np.nan, np.nan],
        'LN8-1205BL': [0.485153079, 1.03000271, 0.782000195, np.nan, np.nan, np.nan, np.nan],
        'LN9-1315BL': [0.492599693, 0.953486003, 0.618357257, 0.371824586, 0.625783402, 0.705343274, 0.451463534],
        'LN9-1358IR': [0.33207914, 0.455197984, 0.453811153, 0.537530998, 0.160409973, 0.327652464, 0.318659655]
    }

    # P-values extracted from the "Adjusted P Value" column in the table.
    # Note: The chart does not show a P-value for LN1-18IL.
    p_values = {
        'LN7-1112AR': 0.4237,
        'LN7-1120BL': 0.7995,
        'LN7-1134BL': 0.0342,
        'LN8-1194BR': 0.0225,
        'LN8-1198AR': 0.7291,
        'LN8-1205BL': 0.6822,
        'LN9-1315BL': 0.0249,
        'LN9-1358IR': 0.0001
    }

    groups = list(raw_data.keys())

    # Calculate Mean and Std Dev for plotting
    means = []
    stds = []
    clean_data_points = []

    for g in groups:
        # Filter out NaNs
        data = [x for x in raw_data[g] if not np.isnan(x)]
        clean_data_points.append(data)
        means.append(np.mean(data))
        stds.append(np.std(data, ddof=1)) # Sample standard deviation

    # Prepare data for JSON
    # We need to serialize numpy floats to native python floats
    output_data = {
        "groups": groups,
        "p_values": p_values,
        "means": [float(x) for x in means],
        "stds": [float(x) for x in stds],
        "clean_data_points": clean_data_points # these are already lists of floats
    }

    return raw_data, output_data

if __name__ == "__main__":
    src_data, der_data = process_and_extract_data()
    
    final_output = {
        "scr_data": src_data,
        "der_data": der_data
    }
    
    with open("bench/ground_truth_code/nature_1_output/92.json", "w") as f:
        json.dump(final_output, f, indent=4)
