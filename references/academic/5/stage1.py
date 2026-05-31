import sys
import io
import json
import numpy as np
import pandas as pd
from scipy import stats

def process_data(output_filename):
    csv_data = """
|   WT saline |     WT K |   A1ko saline |   A1ko K |   A2a ko saline |   A2a ko K |
|------------:|---------:|--------------:|---------:|----------------:|-----------:|
|     163.926 | 146.915  |       93.4671 |  168.582 |           89.33 |     144.37 |
|     164.714 | 130.208  |      141.638  |  167.291 |          143.23 |     153.87 |
|     141.336 | 133.681  |      164.543  |   82.285 |          183.09 |     154.22 |
|     130.72  | 118.735  |      157.607  |  112.291 |           54.72 |     139.03 |
|     178.996 |  87.1218 |      201.418  |  121.264 |          167.68 |      74.62 |
|     160.724 | 144.446  |      148.003  |  152.277 |          201.62 |     123.2  |
|     151.167 | 101.561  |      165.569  |  150.877 |          181.81 |     147.89 |
|     102.942 | 137.995  |      167.359  |  146.772 |          198.38 |     190.94 |
|     178.892 | 151.035  |      141.59   |  120.345 |          nan    |     nan    |
|     165.005 | 130.827  |       99.848  |  147.588 |          nan    |     nan    |
|     146.067 | 110.871  |      nan      |  nan     |          nan    |     nan    |
|     198.72  |  62.9039 |      nan      |  nan     |          nan    |     nan    |
|     178.15  | 138.84   |      nan      |  nan     |          nan    |     nan    |
|      93.44  | 124.06   |      nan      |  nan     |          nan    |     nan    |
|     158.86  | 100.39   |      nan      |  nan     |          nan    |     nan    |
|     171.53  | 118.43   |      nan      |  nan     |          nan    |     nan    |
|     175.43  | 104.59   |      nan      |  nan     |          nan    |     nan    |
|     128     |  97      |      nan      |  nan     |          nan    |     nan    |
|     nan     | 108      |      nan      |  nan     |          nan    |     nan    |
|     nan     | 112      |      nan      |  nan     |          nan    |     nan    |
"""
    # Read CSV
    df = pd.read_csv(io.StringIO(csv_data), sep='|', skipinitialspace=True)
    
    # Drop empty columns
    df = df.dropna(axis=1, how='all') 
    
    # Clean column names
    df.columns = [c.strip() for c in df.columns]
    
    # Remove separator row
    df = df.iloc[1:].reset_index(drop=True)
    
    # Convert to numeric
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    cols = ['WT saline', 'WT K', 'A1ko saline', 'A1ko K', 'A2a ko saline', 'A2a ko K']
    
    means = df[cols].mean().to_dict()
    sems = df[cols].sem().to_dict()
    
    raw_data = {}
    for col in cols:
        raw_data[col] = df[col].dropna().tolist()

    # Comparisons
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
    output_file = "bench/ground_truth_code/nature_2_output/5.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    process_data(output_file)
