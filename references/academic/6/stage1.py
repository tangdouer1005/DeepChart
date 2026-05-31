import sys
import io
import json
import numpy as np
import pandas as pd
from scipy import stats

def process_data(output_filename):
    csv_data = """WT saline,WT K,A1ko saline,A1ko K,A2a ko saline,A2a ko K
48.1752,87.156,50.9091,63.3663,60,80.16
66.2921,81.6514,88.9831,39.6226,83.47,72.88
82.0513,62.5514,80.0781,61.9048,51.06,58.86
55.6391,60.9043,58.0524,60.7595,68.25,52.89
56.6901,83.5249,63.986,60.0746,57.25,66.97
88.3803,91.8182,71.1679,82.7206,43.1,60.5
62.0155,75.6477,64.2857,60.794,72,67.53
72.9167,73.4615,65.4762,63.7288,62.55,66.52
55.3719,67.2199,46.9055,40.0862,nan,nan
51.5038,74.4361,37.5,53.0351,nan,nan
62.5,66.6667,nan,nan,nan,nan
45.0237,79.3774,nan,nan,nan,nan
65.26,82.88,nan,nan,nan,nan
62.61,81.76,nan,nan,nan,nan
56.64,66.67,nan,nan,nan,nan
69.52,78.55,nan,nan,nan,nan
61.04,63.23,nan,nan,nan,nan
50.8,87.82,nan,nan,nan,nan
67.17,64.86,nan,nan,nan,nan"""

    df = pd.read_csv(io.StringIO(csv_data))

    columns = ['WT saline', 'WT K', 'A1ko saline', 'A1ko K', 'A2a ko saline', 'A2a ko K']
    
    means = df[columns].mean().to_dict()
    sems = df[columns].sem().to_dict()
    
    raw_data = {}
    for col in columns:
        raw_data[col] = df[col].dropna().tolist()

    comparisons = [
        (0, 1),
        (2, 3),
        (4, 5)
    ]

    comparisons_results = []
    for c1, c2 in comparisons:
        d1 = df.iloc[:, c1].dropna()
        d2 = df.iloc[:, c2].dropna()
        t, p_val = stats.ttest_ind(d1, d2)
        
        comparisons_results.append({
            'col1_idx': c1,
            'col2_idx': c2,
            'col1': columns[c1],
            'col2': columns[c2],
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
    output_file = "bench/ground_truth_code/nature_2_output/6.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    process_data(output_file)
