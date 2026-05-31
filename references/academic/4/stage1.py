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
    # Clean and parse
    lines = csv_data.strip().split('\n')
    clean_csv_str = "\n".join([lines[0]] + lines[2:])
    
    # Use pipe separator
    df = pd.read_csv(io.StringIO(clean_csv_str), sep="|")
    
    # Drop empty columns
    df = df.dropna(axis=1, how='all')
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Ensure numeric
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 2. Stats
    cols = [
        'WT naive', 'WT saline', 'WT K',
        'A1 ko naive', 'A1ko saline', 'A1ko K',
        'A2a ko naive', 'A2a ko saline', 'A2a ko K'
    ]
    
    means = df[cols].mean().to_dict()
    sems = df[cols].sem().to_dict()
    
    raw_data = {}
    for col in cols:
        raw_data[col] = df[col].dropna().tolist()

    # 3. Comparisons
    # (col1_idx, col2_idx) pairs to check
    comparisons_to_check = [
        (0, 1),
        (1, 2),
        (3, 4),
        (4, 5),
        (6, 7),
        (7, 8)
    ]
    
    comparisons_results = []
    for c1, c2 in comparisons_to_check:
        d1 = df.iloc[:, c1].dropna()
        d2 = df.iloc[:, c2].dropna()
        t, p_val = stats.ttest_ind(d1, d2)
        
        comparisons_results.append({
            'col1_idx': c1,
            'col2_idx': c2,
            'col1': cols[c1],
            'col2': cols[c2],
            'p_val': p_val
        })

    output_data = {
        "scr_data": {
            "raw_data": raw_data
        },
        "der_data": {
            "means": means,
            "sems": sems,
            "columns": cols,
            "comparisons": comparisons_results
        }
    }
    
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_2_output/4.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    process_data(output_file)
