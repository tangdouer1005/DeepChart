import sys
import json
import numpy as np
import pandas as pd

def compute_data():
    # ---------------------------------------------------------
    # 1. Data Preparation
    # ---------------------------------------------------------
    # Raw data extracted from the provided source table
    data = {
        'B16-F0': [1.0524294, 0.99642126, 0.95114935],
        'LN7-1134BL': [0.74170805, 0.7873782, 0.75957924],
        'LN8-1194BR': [0.57713831, 0.54398637, 0.56088287],
        'LN9-1315BL': [0.54237196, 0.53865737, 0.50458335],
        'F0Luc, -Cys': [0.03989584, 0.0410516, 0.03855378], # Header in data was "B16-F0 - Cys"
        'LN7-1134BL, -Cys': [0.01544157, 0.0159137, 0.01655506],
        'LN8-1194BR, -Cys': [0.01384739, 0.01401451, 0.01451768],
        'LN9-1315BL, -Cys': [0.01376061, 0.01339609, 0.01397419]
    }

    # Convert to DataFrame for easier handling
    df = pd.DataFrame(data)
    
    # Calculate Means and Standard Deviations
    means = df.mean().to_dict()
    stds = df.std().to_dict()
    
    # X-axis labels matching the chart image
    labels = [
        'B16-F0', 'LN7-1134BL', 'LN8-1194BR', 'LN9-1315BL',
        'F0Luc, -Cys', 'LN7-1134BL, -Cys', 'LN8-1194BR, -Cys', 'LN9-1315BL, -Cys'
    ]

    output_data = {
        "scr_data": {
            "raw_data": data,
            "labels": labels
        },
        "der_data": {
            "means": means,
            "stds": stds
        }
    }
    return output_data

if __name__ == "__main__":
    output_path = "bench/ground_truth_code/nature_1_output/102.json"
    try:
        data = compute_data()
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to {output_path}")
    except Exception as e:
        print(f"Error computing data: {e}")
        sys.exit(1)
