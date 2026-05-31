import sys
import io
import pandas as pd
import numpy as np
from scipy import stats
import json

def compute_data(output_path):
    # 1. Source Data
    # The data is provided as a markdown table string.
    csv_data = """K5 | DCK5 | K10 | DCK10
2.02859 | 7.2504 | 5.40501 | 9.87058
0.878401 | 3.31785 | 2.23115 | 8.92622
0.98349 | 7.06946 | 6.34756 | 7.82007
0.785771 | 7.76414 | 2.56239 | 8.22059
0.388214 | 4.70172 | 4.55303 | 10.6351
2.19805 | 6.59061 | 5.07432 | 6.57444
1.57333 | 7.09779 | 4.39348 | 11.0517
1.50217 | 6.17586 | 4.89635 | nan
3.44616 | nan | 3.20176 | nan
nan | nan | 3.7647 | nan
nan | nan | 3.76893 | nan
nan | nan | 3.87353 | nan"""
    
    # Load data
    df = pd.read_csv(io.StringIO(csv_data), sep=r"\s*\|\s*", engine='python')
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Convert all columns to numeric
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Prepare data for plotting (remove NaNs)
    # Convert to lists for JSON serialization
    plot_data_dict = {
        'K5': df['K5'].dropna().tolist(),
        'DCK5': df['DCK5'].dropna().tolist(),
        'K10': df['K10'].dropna().tolist(),
        'DCK10': df['DCK10'].dropna().tolist()
    }
    
    plot_data_list = [
        plot_data_dict['K5'],
        plot_data_dict['DCK5'],
        plot_data_dict['K10'],
        plot_data_dict['DCK10']
    ]

    # Calculate significance stats (Derived data)
    t_stat_left, p_val_left = stats.ttest_ind(plot_data_list[0], plot_data_list[1])
    t_stat_right, p_val_right = stats.ttest_ind(plot_data_list[2], plot_data_list[3])

    output_data = {
        "scr_data": {
            "raw_data": plot_data_dict
        },
        "der_data": {
            "p_val_left": p_val_left,
            "p_val_right": p_val_right
        }
    }

    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_2_output/11.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compute_data(output_file)
