import sys
import pandas as pd
import numpy as np
import io
import json

def generate_data(output_filename):
    # 1. Load and Process Source Data
    # The provided data contains the raw measurements for the "Experimental" series.
    csv_data = """Electrolyte|measurement #1|measurement #2|measurement #3|measurement #4
LiAsF6 electrolyte|2.9|2.6|2.6|2.7
LiPF6 electrolyte|3|3.3|2.8|3.3
LiFSI electrolyte|3.2|3.1|3.3|3
LiTFSI electrolyte|3.9|3.4|3|3.7
LiClO4 electrolyte|4.1|4.8|4.2|3.8
LiBF4 electrolyte|3.9|4.1|5.4|4.4
LiDFOB electrolyte|4.7|4.5|4.9|5.4
LiNO3 electrolyte|5.2|5.2|6.2|5.3"""

    # Parse the CSV data
    df = pd.read_csv(io.StringIO(csv_data), sep='|')
    
    # Clean up column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Clean up electrolyte names (strip whitespace)
    df['Electrolyte'] = df['Electrolyte'].str.strip()

    # Calculate Mean and Standard Deviation for the Experimental series (Blue Diamonds)
    measurement_cols = ['measurement #1', 'measurement #2', 'measurement #3', 'measurement #4']
    df['Experimental_Mean'] = df[measurement_cols].mean(axis=1)
    df['Experimental_Std'] = df[measurement_cols].std(axis=1)

    # 2. Define Simulation Data
    simulation_values = [
        2.05,  # LiAsF6
        2.32,  # LiPF6
        2.65,  # LiFSI
        2.75,  # LiTFSI
        2.95,  # LiClO4
        3.15,  # LiBF4
        3.40,  # LiDFOB
        4.32   # LiNO3
    ]
    df['Simulation_Mean'] = simulation_values

    # 3. Prepare Plotting Labels (Formatting chemical formulas)
    label_map = {
        'LiAsF6 electrolyte': r'AsF$_6$',
        'LiPF6 electrolyte': r'PF$_6$',
        'LiFSI electrolyte': 'FSI',
        'LiTFSI electrolyte': 'TFSI',
        'LiClO4 electrolyte': r'ClO$_4$',
        'LiBF4 electrolyte': r'BF$_4$',
        'LiDFOB electrolyte': 'DFOB',
        'LiNO3 electrolyte': r'NO$_3$'
    }
    df['Label'] = df['Electrolyte'].map(label_map)

    # Save to JSON
    scr_data = df[['Electrolyte', 'measurement #1', 'measurement #2', 'measurement #3', 'measurement #4', 'Simulation_Mean']].to_dict(orient='records')
    der_data = df[['Electrolyte', 'Label', 'Experimental_Mean', 'Experimental_Std']].to_dict(orient='records')
    
    output_json = {
        "scr_data": scr_data,
        "der_data": der_data
    }
    
    with open(output_filename, 'w') as f:
        json.dump(output_json, f, indent=4)
        
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/39.json"
    generate_data(output_file)
