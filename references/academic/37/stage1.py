import numpy as np
import sys
import json
import pandas as pd

def main():
    # 1. Data Preparation
    # Extracted directly from the provided Markdown tables.
    # Structure: Name, Y-values (CCD), X-values (Crystallite size), Color (approximate hex)
    
    data_points = [
        {
            "name": "LiAsF$_6$",
            "y_raw": [36, 36],
            "x_raw": [2.9, 2.6, 2.6, 2.7],
            "color": "#D32F2F", # Red
            "label_pos": (-10, 20) # Offset for text (x, y)
        },
        {
            "name": "LiPF$_6$",
            "y_raw": [32, 28],
            "x_raw": [3.0, 3.3, 2.8, 3.3],
            "color": "#305496", # Dark Blue
            "label_pos": (15, 15)
        },
        {
            "name": "LiFSI",
            "y_raw": [29, 22],
            "x_raw": [3.2, 3.1, 3.3, 3.0],
            "color": "#F4C63D", # Yellow/Gold
            "label_pos": (-35, -5)
        },
        {
            "name": "LiTFSI",
            "y_raw": [20, 18],
            "x_raw": [3.9, 3.4, 3.0, 3.7],
            "color": "#6AA84F", # Green
            "label_pos": (-40, -15)
        },
        {
            "name": "LiClO$_4$",
            "y_raw": [26, 23],
            "x_raw": [4.1, 4.8, 4.2, 3.8],
            "color": "#674EA7", # Purple
            "label_pos": (-10, 10)
        },
        {
            "name": "LiBF$_4$",
            "y_raw": [21, 17],
            "x_raw": [3.9, 4.1, 5.4, 4.4],
            "color": "#8E8E8E", # Grey
            "label_pos": (-35, -25)
        },
        {
            "name": "LiDFOB",
            "y_raw": [20, 16],
            "x_raw": [4.7, 4.5, 4.9, 5.4],
            "color": "#E06666", # Salmon/Red
            "label_pos": (15, 15)
        },
        {
            "name": "LiNO$_3$",
            "y_raw": [15, 15],
            "x_raw": [5.2, 5.2, 6.2, 5.3],
            "color": "#6D9EEB", # Light Blue
            "label_pos": (10, -15)
        }
    ]

    processed_data = []

    # 3. Processing
    for point in data_points:
        # Calculate Mean
        x_mean = np.mean(point["x_raw"])
        y_mean = np.mean(point["y_raw"])
        
        # Calculate Standard Deviation for Error Bars
        x_err = np.std(point["x_raw"], ddof=1)
        y_err = np.std(point["y_raw"], ddof=1)
        
        processed_data.append({
            "name": point["name"],
            "x_mean": x_mean,
            "y_mean": y_mean,
            "x_err": x_err,
            "y_err": y_err,
            "color": point["color"],
            "label_pos": point["label_pos"],
            "x_raw_mean": x_mean, # keep for correlation calc if needed, or just use x_mean
            "y_raw_mean": y_mean
        })

    # Save to JSON
    output_path = "bench/ground_truth_code/nature_1_output/37.json"
    
    output_json = {
        "scr_data": data_points,
        "der_data": processed_data
    }

    with open(output_path, 'w') as f:
        json.dump(output_json, f, indent=4)
        
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    main()
