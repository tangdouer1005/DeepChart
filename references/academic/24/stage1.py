import sys
import io
import pandas as pd
import numpy as np
from scipy import stats
import json
import os

def get_source_data():
    """
    Returns the raw data provided in the prompt as a pandas DataFrame.
    """
    csv_data = """Cancer Type|Model|Percentage of Slides in Pretraining Dataset (%)|Average Downstream Performance (AUROC)
LUNG|ctranspath|8.4|0.7101566922966756
BRCA|ctranspath|7.5|0.6901946923437127
STAD|ctranspath|3.4|0.6727500426566878
CRC|ctranspath|11.7|0.6402351975254987
LUNG|phikon|9.7|0.7086469364758765
BRCA|phikon|8.8|0.6333019990370683
STAD|phikon|4|0.6650650873334706
CRC|phikon|5.7|0.6335703165007269
LUNG|uni|9.8|0.7582049929810751
BRCA|uni|3.3|0.6884572772690907
STAD|uni|6.7|0.6769115022211536
CRC|uni|8.3|0.6585192894528652
LUNG|kaiko|9.7|0.7311053739265448
BRCA|kaiko|8.8|0.685518762408426
STAD|kaiko|4|0.6679383667204072
CRC|kaiko|5.7|0.609584221956904
LUNG|prov-gigapath|45|0.7578128341867243
BRCA|prov-gigapath|2.7|0.66703719221213
STAD|prov-gigapath|0.7|0.6867942247149665
CRC|prov-gigapath|30|0.6796362735454282
LUNG|virchow-class|6.1|0.7174955993098335
BRCA|virchow-class|25|0.6589119444462541
STAD|virchow-class|3.5|0.6845577051089727
CRC|virchow-class|3.2|0.6476261453717196
LUNG|virchow2-class|4|0.7453463548176368
BRCA|virchow2-class|19|0.7043400914608242
STAD|virchow2-class|3|0.7171710064688561
CRC|virchow2-class|6|0.6911429496854462
LUNG|panakeia|0|0.7136461434822977
BRCA|panakeia|82|0.7080816433172487
STAD|panakeia|0|0.6830453013043695
CRC|panakeia|18|0.6616418630330357"""
    
    df = pd.read_csv(io.StringIO(csv_data), sep='|')
    return df

def process_data(output_filename):
    df = get_source_data()
    
    # Rename columns for easier access
    df.columns = ['Cancer Type', 'Model', 'Percentage', 'Performance']
    
    # Ensure numeric types
    df['Percentage'] = pd.to_numeric(df['Percentage'])
    df['Performance'] = pd.to_numeric(df['Performance'])

    # Calculate stats for legend
    cancer_order = ['LUNG', 'STAD', 'BRCA', 'CRC']
    stats_list = []
    for c_type in cancer_order:
        subset = df[df['Cancer Type'] == c_type]
        if len(subset) > 1:
            r_val, p_val = stats.pearsonr(subset['Percentage'], subset['Performance'])
        else:
            r_val, p_val = None, None
            
        stats_list.append({
            "cancer_type": c_type,
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
    output_file = "bench/ground_truth_code/nature_2_output/24.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    process_data(output_file)
