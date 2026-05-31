import sys
import io
import json
import pandas as pd
import numpy as np
from scipy import stats

def process_data(output_filename):
    # 1. Load Source Data
    csv_data = """
|   saline |        K5 |     K10 |     K20 |     K30 |      K50 |
|---------:|----------:|--------:|--------:|--------:|---------:|
|  2.61617 |  10.9128  | 17.0236 | 27.166  | 29.3987 |  24.7485 |
|  2.36168 |   8.18393 | 10.8045 | 24.2927 | 25.5928 |  32.7675 |
|  7.15327 |   7.4796  | 19.7571 | 40.8666 | 43.1267 |  30.3007 |
|  5.95655 |   6.79138 | 11.4857 | 33.6696 | 38.4147 |  35.1756 |
|  8.7249  |   6.06007 | 20.58   | 28.6541 | 34.1275 |  45.9113 |
| 10.075   |  10.8698  | 22.387  | 32.8038 | 38.4792 |  50.5032 |
|  4.65983 |  11.254   | 17.5725 | 36.9777 | 41.937  |  50.1651 |
|  5.17181 |   6.60699 | 19.0825 | 35.9643 | 39.0227 |  33.9109 |
|  4.41222 |  11.6103  | 20.2917 | 30.9105 | 37.767  |  23.291  |
|  3.4727  | nan       | 20.6828 | 27.4061 | 35.177  |  25.8906 |
|  3.31779 | nan       | 13.9655 | 21.5009 | 20.7624 |  33.9761 |
|  7.68342 | nan       | 14.848  | 22.4181 | 21.3724 | nan      |
"""

    # Parse the markdown table
    df = pd.read_csv(io.StringIO(csv_data), sep="|", skipinitialspace=True)
    
    # Clean up dataframe
    df = df.dropna(axis=1, how='all')
    df.columns = [c.strip() for c in df.columns]
    
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 2. Prepare Data
    columns = ['saline', 'K5', 'K10', 'K20', 'K30', 'K50']
    
    # Calculate Mean and SEM
    means = df[columns].mean().to_dict()
    sems = df[columns].sem().to_dict()
    
    # Raw data for scatter (handle NaNs for JSON)
    raw_data = {}
    for col in columns:
        raw_data[col] = df[col].dropna().tolist()

    # 3. Calculate p-values
    comparisons = [
        ('saline', 'K5', 0, 1, 14),
        ('K5', 'K10', 1, 2, 26),
        ('K10', 'K20', 2, 3, 44),
        ('K20', 'K30', 3, 4, 51),
        ('K30', 'K50', 4, 5, 59)
    ]

    comparisons_data = []
    for col1, col2, x1, x2, y_pos in comparisons:
        d1 = df[col1].dropna()
        d2 = df[col2].dropna()
        t_stat, p_val = stats.ttest_ind(d1, d2)
        
        comparisons_data.append({
            'col1': col1,
            'col2': col2,
            'x1': x1,
            'x2': x2,
            'y_pos': y_pos,
            'p_val': p_val
        })

    # 4. Construct Output
    output_data = {
        "scr_data": {
            "raw_data": raw_data
        },
        "der_data": {
            "means": means,
            "sems": sems,
            "comparisons": comparisons_data,
            "columns": columns,
            "x_labels": ['0', '5', '10', '20', '30', '50']
        }
    }
    
    # 5. Save Output
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/1.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    process_data(output_file)
