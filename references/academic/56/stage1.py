import numpy as np
import json
import os
from scipy import stats

def compute_data():
    # 1. Source Data
    data_map = {
        "DMSO": {
            "vals": [9.07, 10.2, 12.2, 10.4],
            "group": "DMSO",
            "conc": "DMSO"
        },
        "Rapa_40": {
            "vals": [61.6, 56.6, 58.1, 57.0],
            "group": "Rapamycin",
            "conc": "40 nM"
        },
        "Rapa_100": {
            "vals": [59.0, 59.2, 60.1, 59.3],
            "group": "Rapamycin",
            "conc": "100 nM"
        },
        "Rapa_200": {
            "vals": [62.8, 60.0, 59.8, 60.8],
            "group": "Rapamycin",
            "conc": "200 nM"
        },
        "LY_1": {
            "vals": [20.8, 26.5, 27.6, 26.5],
            "group": "LY294002",
            "conc": "1 μM"
        },
        "LY_5": {
            "vals": [59.0, 59.6, 59.2, 56.7],
            "group": "LY294002",
            "conc": "5 μM"
        },
        "LY_10": {
            "vals": [78.6, 76.9, 75.5, 75.0],
            "group": "LY294002",
            "conc": "10 μM"
        },
        "MK_0.2": {
            "vals": [66.3, 67.1, 66.7, 67.3],
            "group": "MK2206",
            "conc": "0.2 μM"
        },
        "MK_1": {
            "vals": [71.1, 73.7, 74.1, 71.7],
            "group": "MK2206",
            "conc": "1 μM"
        }
    }

    order = [
        "DMSO", 
        "Rapa_40", "Rapa_100", "Rapa_200", 
        "LY_1", "LY_5", "LY_10", 
        "MK_0.2", "MK_1"
    ]

    # Calculate statistics
    means = {}
    stds = {}
    p_values = {}
    
    dmso_vals = data_map["DMSO"]["vals"]
    
    for key in order:
        vals = data_map[key]["vals"]
        means[key] = np.mean(vals)
        stds[key] = np.std(vals) # Using population std as in original code (default ddof=0)
        
        if key != "DMSO":
            _, p_val = stats.ttest_ind(dmso_vals, vals)
            p_values[key] = p_val

    # Prepare data for JSON
    scr_data = {
        "data_map": data_map,
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
        
    output_path = os.path.join(output_dir, "56.json")
    
    with open(output_path, "w") as f:
        json.dump(output_json, f, indent=4)
        
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    compute_data()
