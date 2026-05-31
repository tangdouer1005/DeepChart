import pandas as pd
import numpy as np
import json
import os

def compute_data(output_json_path):
    # ---------------------------------------------------------
    # 1. Data Preparation
    # ---------------------------------------------------------
    # Raw data transcribed exactly from the provided source table.
    # Values are fractions, will be converted to % later.
    
    data = {
        'Current_Density': [200, 200, 200, 400, 400, 400, 600, 600, 600] * 2, # Repeated for AEM and Separator
        'Replicate': [1, 2, 3] * 6,
        'Configuration': ['AEM']*9 + ['Separator']*9,
        
        # H2 Values
        'H2': [
            # AEM (200, 400, 600)
            0.0005102, 0.0004747, 0.0002913, # 200
            0.0004292, 0.0003801, 0.0001648, # 400
            0.0002917, 0.0003309, 0.0001181, # 600
            # Separator (200, 400, 600)
            0.0007523, 0.0009948, 0.00078201, # 200
            0.0006943, 0.0007962, 0.00060853, # 400
            0.0004785, 0.0005823, 0.0004726   # 600
        ],
        
        # C2H4 Values
        'C2H4': [
            # AEM
            0.0003829, 0.0002889, 0.0002951, # 200
            0.0004542, 0.0003147, 0.0003559, # 400
            0.0002639, 0.0001960, 0.0002229, # 600
            # Separator
            0.00024107, 0.0002489, 0.0002301, # 200
            0.0002284,  0.0002373, 0.0002208, # 400
            0.0001712,  0.0001792, 0.0001823  # 600
        ],
        
        # CO Values
        'CO': [
            # AEM
            0.0010257, 0.0008115, 0.0012724, # 200
            0.0007593, 0.0006018, 0.0008532, # 400
            0.0005042, 0.0004595, 0.0005854, # 600
            # Separator
            0.0009924, 0.0006823, 0.0009586, # 200
            0.0008031, 0.0005694, 0.0006918, # 400
            0.0006532, 0.0004572, 0.0005008  # 600
        ]
    }

    df = pd.DataFrame(data)

    # Convert fractions to percentages (multiply by 100)
    cols_to_scale = ['H2', 'C2H4', 'CO']
    df[cols_to_scale] = df[cols_to_scale] * 100

    # Calculate Mean and Std Dev for each group
    grouped = df.groupby(['Current_Density', 'Configuration'])[cols_to_scale].agg(['mean', 'std'])
    
    # Flatten MultiIndex columns
    grouped.columns = ['_'.join(col) for col in grouped.columns]
    grouped = grouped.reset_index()

    # Convert to dictionary for JSON output
    scr_data = df.to_dict(orient='records')
    der_data = grouped.to_dict(orient='records')
    
    output_json = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

    with open(output_json_path, 'w') as f:
        json.dump(output_json, f, indent=4)
    print(f"Data saved to {output_json_path}")

if __name__ == "__main__":
    output_json = "bench/ground_truth_code/nature_1_output/41.json"
    compute_data(output_json)
