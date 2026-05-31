import sys
import pandas as pd
import numpy as np
import json

def generate_data(output_filename):
    # 1. Data Preparation
    # We reconstruct the dataframes exactly from the provided source data.
    
    # Part 1: SSL Ratios (from the first section of the source table)
    ssl_data = {
        "Electrolyte": [
            "LiAsF6 electrolyte", "LiPF6 electrolyte", "LiFSI electrolyte", 
            "LiTFSI electrolyte", "LiClO4 electrolyte", "LiBF4 electrolyte", 
            "LiDFOB electrolyte", "LiNO3 electrolyte"
        ],
        "SSL ratio (%)": [
            90, 80, 78.33333, 
            76.66667, 71.66667, 75, 
            70.4918, 68.33333
        ]
    }
    
    # Part 2: Crystallite Size Measurements (from the third section of the source table)
    # Columns: measurement #1, #2, #3, #4
    size_data = {
        "Electrolyte": [
            "LiAsF6 electrolyte", "LiPF6 electrolyte", "LiFSI electrolyte", 
            "LiTFSI electrolyte", "LiClO4 electrolyte", "LiBF4 electrolyte", 
            "LiDFOB electrolyte", "LiNO3 electrolyte"
        ],
        "m1": [2.9, 3.0, 3.2, 3.9, 4.1, 3.9, 4.7, 5.2],
        "m2": [2.6, 3.3, 3.1, 3.4, 4.8, 4.1, 4.5, 5.2],
        "m3": [2.6, 2.8, 3.3, 3.0, 4.2, 5.4, 4.9, 6.2],
        "m4": [2.7, 3.3, 3.0, 3.7, 3.8, 4.4, 5.4, 5.3]
    }

    # Create DataFrames
    df_ssl = pd.DataFrame(ssl_data)
    df_size = pd.DataFrame(size_data)

    # Merge DataFrames
    df = pd.merge(df_ssl, df_size, on="Electrolyte")

    # Clean Electrolyte names (remove " electrolyte" suffix) for labeling
    df["Label"] = df["Electrolyte"].str.replace(" electrolyte", "")

    # Calculate Mean and Standard Deviation for Crystallite Size
    measurements = ["m1", "m2", "m3", "m4"]
    df["Mean_Size"] = df[measurements].mean(axis=1)
    df["Std_Size"] = df[measurements].std(axis=1)

    # Save to JSON
    scr_data = {
        "ssl_data": ssl_data,
        "size_data": size_data
    }
    
    der_data = df[['Electrolyte', 'Label', 'Mean_Size', 'Std_Size']].to_dict(orient='records')
    
    output_json = {
        "scr_data": scr_data,
        "der_data": der_data
    }
    
    with open(output_filename, 'w') as f:
        json.dump(output_json, f, indent=4)
        
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/38.json"
    generate_data(output_file)
