import sys
import io
import json
import numpy as np
import pandas as pd
from scipy import stats

def process_data(output_filename):
    csv_data = """
|   WT naive |   WT saline |     WT K |   A1 ko naive |   A1ko saline |   A1ko K |   A2a ko naive |   A2a ko saline |   A2a ko K |
|-----------:|------------:|---------:|--------------:|--------------:|---------:|---------------:|----------------:|-----------:|
|    55.5556 |     65.5914 |  82.2878 |       97.2881 |       40.5512 |  49.7382 |        80.2198 |         80      |    54.5455 |
|    95.9821 |     57.2072 |  88.8393 |       96.4169 |       76.4463 |  57.5758 |        79.5322 |         55.9322 |    83.3333 |
|    74.0458 |     58.1673 |  48.1081 |       82.3708 |       68.75   |  61.6541 |        96.6258 |         81.1225 |    79.2627 |
|    71.9512 |     44.9735 |  86.1925 |       92.9578 |       53.7234 |  75.3927 |        71.5596 |         74.8603 |    47.9245 |
|    80.2691 |     72.1774 |  63.8743 |       77.6786 |       83.3333 |  66.8293 |        70.5882 |         81.8182 |    66.3158 |
|    79.0941 |     54.1936 |  86.9565 |       80.8725 |       73.0337 |  85.1282 |        61.6601 |         58.9226 |    57.7092 |
|    76.0563 |     63.587  |  84.188  |       86.0656 |       25.1724 |  78.7879 |        77.1784 |         88.835  |    78.2101 |
|    74.6114 |     48.731  |  78.0172 |       84.9582 |       76.1468 |  47.541  |        86.2069 |         80.1136 |    88.0597 |
|    89      |     35.3591 |  95.0226 |       70.7395 |       85.4406 |  75.6493 |        87.5598 |         60.9091 |   nan      |
|    92.4603 |     59.6154 |  73.5178 |       86.6667 |      nan      |  84.5902 |        95.6522 |         46.25   |   nan      |
|    91.4062 |     69.0196 |  93.609  |       70.1492 |      nan      |  77.8912 |        83.7963 |         43.949  |   nan      |
|    75.8755 |     61.6601 |  52.7094 |       71.0191 |      nan      | nan      |        82.5911 |         70.4918 |   nan      |
|    92.7185 |     81.0127 |  44.6237 |       56.3319 |      nan      | nan      |        84.5745 |        nan      |   nan      |
|    76.7933 |     54.0909 |  88.421  |       74.6988 |      nan      | nan      |        75.5245 |        nan      |   nan      |
|    69.9531 |     60.4938 |  79.9257 |       65.942  |      nan      | nan      |        56.5217 |        nan      |   nan      |
|    71.5026 |     62.3037 | nan      |       70.3971 |      nan      | nan      |        96.8641 |        nan      |   nan      |
|    88.6598 |     53.8117 | nan      |       83.5766 |      nan      | nan      |       nan      |        nan      |   nan      |
|    62.234  |    nan      | nan      |      nan      |      nan      | nan      |       nan      |        nan      |   nan      |
"""
    lines = [line for line in csv_data.strip().split('\n') if '---' not in line]
    cleaned_csv = '\n'.join(lines)
    
    # Use simple separator
    df = pd.read_csv(io.StringIO(cleaned_csv), sep='|', skipinitialspace=True)
    
    # Drop columns that are completely empty
    if len(df.columns) > 0 and (df.columns[0] == '' or df.columns[0].startswith('Unnamed')):
        df = df.iloc[:, 1:]
    if len(df.columns) > 0 and (df.columns[-1] == '' or df.columns[-1].startswith('Unnamed')):
        df = df.iloc[:, :-1]
    
    # Clean column names
    df.columns = [c.strip() for c in df.columns]
    
    # Ensure numeric
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 2. Data Processing
    means = df.mean().to_dict()
    sems = df.sem().to_dict()
    
    columns = list(df.columns)
    raw_data = {}
    for col in columns:
        raw_data[col] = df[col].dropna().tolist()
        
    # Comparisons
    groups = [
        (0, 3, [(0, 1), (1, 2)]), # WT
        (3, 6, [(3, 4), (4, 5)]), # A1
        (6, 9, [(6, 7), (7, 8)])  # A2a
    ]

    comparisons_results = []
    
    for start, end, pairs in groups:
        for col1_idx, col2_idx in pairs:
            if col1_idx >= len(columns) or col2_idx >= len(columns):
                continue
            col1 = columns[col1_idx]
            col2 = columns[col2_idx]
            
            d1 = df[col1].dropna()
            d2 = df[col2].dropna()
            
            if len(d1) > 1 and len(d2) > 1:
                t_stat, p_val = stats.ttest_ind(d1, d2)
            else:
                p_val = 1.0
            
            comparisons_results.append({
                'group_start': start,
                'group_end': end,
                'col1_idx': col1_idx,
                'col2_idx': col2_idx,
                'col1': col1,
                'col2': col2,
                'p_val': p_val
            })

    output_data = {
        "scr_data": {
            "raw_data": raw_data
        },
        "der_data": {
            "means": means,
            "sems": sems,
            "columns": columns,
            "comparisons": comparisons_results
        }
    }
    
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/3.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    process_data(output_file)
