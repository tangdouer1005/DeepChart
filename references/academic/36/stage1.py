import sys
import numpy as np
import pandas as pd
import json

def generate_data(output_filename):
    # ---------------------------------------------------------
    # 1. Data Preparation
    # ---------------------------------------------------------
    # Based on the provided Source Data tables.
    # X-axis: "Thickness of deposited Li (μm)" from the first table.
    # Y-axis: Calculated Mean from "Average crystallite size measurement" (Section 3).
    # Error Bars: Calculated Standard Deviation from the measurements.
    
    data = {
        'Electrolyte': [
            'LiAsF6', 'LiPF6', 'LiFSI', 'LiTFSI', 
            'LiClO4', 'LiBF4', 'LiDFOB', 'LiNO3'
        ],
        # Extracted from Table 1: Thickness of deposited Li (μm)
        'Thickness_Li_um': [
            11.7, 12.3, 14.2, 15.8, 
            15.8, 16.1, 14.9, 17.0
        ],
        # Extracted from Table 3: Measurements #1, #2, #3, #4
        'Measurements': [
            [2.9, 2.6, 2.6, 2.7],   # LiAsF6
            [3.0, 3.3, 2.8, 3.3],   # LiPF6
            [3.2, 3.1, 3.3, 3.0],   # LiFSI
            [3.9, 3.4, 3.0, 3.7],   # LiTFSI
            [4.1, 4.8, 4.2, 3.8],   # LiClO4
            [3.9, 4.1, 5.4, 4.4],   # LiBF4
            [4.7, 4.5, 4.9, 5.4],   # LiDFOB
            [5.2, 5.2, 6.2, 5.3]    # LiNO3
        ]
    }

    df = pd.DataFrame(data)
    
    # Calculate Mean and Std Dev for Y-axis
    df['Crystallite_Mean'] = df['Measurements'].apply(np.mean)
    # Using population std or sample std? Usually sample (ddof=1) for error bars.
    df['Crystallite_Std'] = df['Measurements'].apply(lambda x: np.std(x, ddof=1))

    # Save to JSON
    scr_data = df[['Electrolyte', 'Thickness_Li_um', 'Measurements']].to_dict(orient='records')
    der_data = df[['Electrolyte', 'Crystallite_Mean', 'Crystallite_Std']].to_dict(orient='records')
    
    output_json = {
        "scr_data": scr_data,
        "der_data": der_data
    }
    
    with open(output_filename, 'w') as f:
        json.dump(output_json, f, indent=4)
        
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/36.json"
    generate_data(output_file)
