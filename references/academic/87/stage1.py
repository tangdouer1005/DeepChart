import pandas as pd
import numpy as np
import json
import os

def process_data(output_filename='bench/ground_truth_code/nature_2_output/87.json'):
    # 1. Data Preparation
    # Extracted directly from the provided Markdown table (Source Data)
    # Keys are Generations (LN0-LN9 -> 0-9), Values are the Y-values (Fsp1 TPM)
    raw_data = {
        0: [5.86566848, 8.15498, 8.072314491],
        1: [10.08575711, 10.8043, 8.624570815, 7.92934],
        2: [8.299775685, 10.4507, 9.935653318],
        3: [10.21662252, 8.68885, 12.23267],
        4: [13.14692214, 11.2483, 17.66730274],
        5: [11.23320993, 11.317, 14.40373849],
        6: [16.84068224, 20.4273, 9.949043375, 10.8217, 10.8965],
        7: [16.60248485, 12.4377, 13.09089132],
        8: [8.269548139, 12.3538, 17.2109045],
        9: [9.73430569, 16.1348]
    }

    # Flatten data for JSON
    data_points = []
    for gen, values in raw_data.items():
        for val in values:
            if not np.isnan(val):
                data_points.append({'Generation': gen, 'TPM': val})
    
    # 2. Statistical Calculations (Matching Source Data)
    # The table provides specific regression stats.
    stats_data = {
        'slope': 0.676,
        'intercept': 8.724,
        'r_squared': 0.3089,
        'syx': 2.879
    }

    # Combine into one object
    output_data = {
        'data': data_points,
        'stats': stats_data
    }

    return raw_data, output_data

if __name__ == "__main__":
    raw_source_data, processed_derived_data = process_data()
    
    final_output = {
        "scr_data": raw_source_data,
        "der_data": processed_derived_data
    }
    
    output_filename = 'bench/ground_truth_code/nature_1_output/87.json'
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    with open(output_filename, 'w') as f:
        json.dump(final_output, f, indent=4)
        
    print(f"Data saved to {output_filename}")