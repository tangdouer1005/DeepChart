import sys
import pandas as pd
import numpy as np
from scipy import stats
import json
import os

def process_data(output_filename):
    # 1. Data Preparation
    data_records = [
        {'Model': 'conch', 'Category': 'Morphology', 'AUROC': 0.7659939108398429, 'Dataset': 1.2},
        {'Model': 'biomedclip', 'Category': 'Morphology', 'AUROC': 0.7331658780868027, 'Dataset': 15},
        {'Model': 'plip', 'Category': 'Morphology', 'AUROC': 0.6983860366946149, 'Dataset': 0.208},
        
        {'Model': 'conch', 'Category': 'Biomarker', 'AUROC': 0.726168367463843, 'Dataset': 1.2},
        {'Model': 'biomedclip', 'Category': 'Biomarker', 'AUROC': 0.667361737958213, 'Dataset': 15},
        {'Model': 'plip', 'Category': 'Biomarker', 'AUROC': 0.6516216846643966, 'Dataset': 0.208},
        
        {'Model': 'conch', 'Category': 'Prognosis', 'AUROC': 0.6318876255522493, 'Dataset': 1.2},
        {'Model': 'biomedclip', 'Category': 'Prognosis', 'AUROC': 0.6051941716893544, 'Dataset': 15},
        {'Model': 'plip', 'Category': 'Prognosis', 'AUROC': 0.5674663216946358, 'Dataset': 0.208},
    ]
    
    df = pd.DataFrame(data_records)

    # Categories in the specific order shown in the legend
    categories = ['Morphology', 'Biomarker', 'Prognosis']

    # Calculate statistics (derived data)
    stats_list = []
    for cat in categories:
        subset = df[df['Category'] == cat]
        
        if len(subset) > 1:
            r_val, p_val = stats.pearsonr(subset['Dataset'], subset['AUROC'])
        else:
            r_val, p_val = None, None
        
        stats_list.append({
            "category": cat,
            "r": r_val,
            "p": p_val
        })
        
    # Prepare output data structure
    output_data = {
        "scr_data": {
            "plot_data": df.to_dict(orient='records')
        },
        "der_data": {
            "stats_data": stats_list
        }
    }
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
        
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_2_output/23.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    process_data(output_file)
