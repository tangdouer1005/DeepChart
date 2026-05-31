import sys
import pandas as pd
import json

def process_and_save_data(output_filename='bench/ground_truth_code/nature_2_output/79.json'):
    # 2. Load Data
    # Creating a DataFrame directly from the provided source data values.
    # Mapping the raw rows to the labels seen in the chart.
    data = [
        # Label, PM_mass_mean (X), PM_mass_SEM (Xerr), OP_AA_m_mean (Y), OP_AA_m_SEM (Yerr), Color, Text Offset
        ("I",   20.22, 1.78, 0.07, 0.02, "#EA899A", (-5, 5)),   # Industrial (Pink)
        ("R",   15.52, 1.00, 0.06, 0.01, "#D966E8", (-10, -10)), # Rural (Purple)
        ("SU",  20.73, 6.58, 0.12, 0.03, "#6FAEE5", (-5, 5)),   # Suburban (Blue)
        ("T",   22.44, 3.26, 0.13, 0.03, "#C4B068", (5, 5)),    # Traffic (Gold/Brown)
        ("U",   21.91, 0.99, 0.07, 0.00, "#7FB866", (5, 5)),    # Urban (Green)
        ("(V)", 20.34, 2.10, 0.11, 0.01, "#C0C0C0", (-15, -5))  # Valley (Grey)
    ]
    
    # Structure for JSON
    output_data = []
    for item in data:
        output_data.append({
            "Label": item[0],
            "X": item[1],
            "Xerr": item[2],
            "Y": item[3],
            "Yerr": item[4],
            "Color": item[5],
            "Offset": item[6]
        })
        
    return data, output_data

if __name__ == "__main__":
    raw_data, processed_data = process_and_save_data()
    
    final_output = {
        "scr_data": raw_data,
        "der_data": processed_data
    }
    
    with open('bench/ground_truth_code/nature_1_output/79.json', 'w') as f:
        json.dump(final_output, f, indent=4)
