import sys
import json
import pandas as pd
import numpy as np

def get_data():
    # 1. Data Preparation
    # Extracting non-NaN values from the provided source table
    data = {
        "Vehicle": [
            1.67691414, 0.85776341, 0.85776341, 1.52754235, 0.79955316, 
            0.98719009, 0.5492265, 0.90853999, 1.4973423, 0.33816465, 
            0.91338701, 1.08661299, 1.3186889, 0.72344104, 0.633546, 
            1.23962408, 0.7431799, 1.46442985, 0.87709022
        ],
        "icFSP1": [
            0.63799637, 0.9680146, 0.82384558, 1.06462968, 0.21999558, 
            0.57015749, 1.46761419, 0.65525489
        ],
        "viFSP1": [
            0.414588, 0.11516141, 0.86840956, 0.15949909, 0.07711164, 
            0.61260379, 0.72365508, 0.59192079, 0.70135255, 0.62916065
        ],
        "BSO": [
            0.661774471, 1.4176097, 0.323789802, 1.406779054, 1.597920275, 
            1.487901399, 1.107086638, 1.572788207, 0.791496725, 0.879682758, 
            0.779937778, 0.924634707, 0.716008452, 1.334819278
        ],
        "icFSP1 + BSO": [
            1.48194219, 0.91662165, 0.14804192, 0.83834204, 0.80823838, 
            0.57720985, 0.76833597, 0.72874142
        ],
        "viFSP1 + BSO": [
            0.17624038, 0.29652135, 0.2772585, 1.12237907, 1.13213888, 
            0.76512095, 0.51511285, 0.71736243, 0.6371418, 0.54660466
        ]
    }

    # Convert to DataFrame for easier handling and JSON serialization
    df_list = []
    for group, values in data.items():
        for val in values:
            df_list.append({'Group': group, 'Value': val})
    df_data = pd.DataFrame(df_list)

    # Statistical Annotations - these are fixed values from the original code
    annotations = [
        # Level 1 (Lowest)
        (0, 1, 1.75, "0.7767"), # Vehicle vs icFSP1
        (3, 4, 1.75, "0.4194"), # BSO vs icFSP1+BSO
        
        # Level 2
        (0, 2, 1.95, "0.0038"), # Vehicle vs viFSP1
        (3, 5, 1.95, "0.0232"), # BSO vs viFSP1+BSO
        
        # Level 3
        (0, 3, 2.15, "0.9974"), # Vehicle vs BSO
        
        # Level 4
        (0, 4, 2.35, "0.6975"), # Vehicle vs icFSP1+BSO
        
        # Level 5 (Highest)
        (0, 5, 2.55, "0.0573")  # Vehicle vs viFSP1+BSO
    ]

    return df_data.to_dict(orient='records'), annotations

if __name__ == "__main__":
    output_path = "bench/ground_truth_code/nature_1_output/110.json"
    try:
        df_records, annotations = get_data()
        
        output_data = {
            "scr_data": {
                "data_records": df_records
            },
            "der_data": {
                "annotations": annotations
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=4)
        print(f"Data saved to {output_path}")
    except Exception as e:
        print(f"Error computing data: {e}")
        sys.exit(1)
