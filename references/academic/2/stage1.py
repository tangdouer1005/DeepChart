import sys
import io
import json
import numpy as np
import pandas as pd
from scipy import stats

def process_data(output_filename):
    # 1. Load Source Data
    csv_data = """saline|K5|K10|K20|K30|K50
-0.15442|2.02859|5.40501|5.92692|8.08702|6.62419
-0.58043|0.878401|2.23115|4.92276|5.83228|13.2996
1.58696|0.98349|6.34756|11.0817|11.3787|8.36267
0.868186|0.785771|2.56239|7.97339|9.18607|11.9092
2.32056|0.388214|4.55303|7.98792|8.53485|17.7595
2.3009|2.19805|5.07432|8.42453|9.63262|21.4167
1.01952|1.57333|4.39348|9.63153|11.4553|21.2146
1.11587|1.50217|4.89635|9.48093|10.6288|9.24065
0.781112|3.44616|3.20176|7.67429|10.3601|5.81632
0.46059|nan|3.7647|7.56366|9.52821|7.84489
0.517398|nan|3.76893|6.8856|5.61355|11.644
1.76375|nan|3.87353|4.87388|4.66221|nan"""

    # Read data into pandas DataFrame
    df = pd.read_csv(io.StringIO(csv_data), sep='|')
    df.columns = [c.strip() for c in df.columns]

    # 2. Calculate Statistics
    means = df.mean().to_dict()
    sems = df.sem().to_dict()
    
    # Raw data for scatter
    columns = list(df.columns)
    raw_data = {}
    for col in columns:
        raw_data[col] = df[col].dropna().tolist()

    # 3. Calculate p-values
    comparisons = [
        ('saline', 'K5', 0, 1, 5.0),
        ('K5', 'K10', 1, 2, 8.8),
        ('K10', 'K20', 2, 3, 13.2),
        ('K20', 'K30', 3, 4, 17.0),
        ('K30', 'K50', 4, 5, 23.0)
    ]
    
    comparisons_results = []
    for col1, col2, x1, x2, y_pos in comparisons:
        d1 = df[col1].dropna()
        d2 = df[col2].dropna()
        t_stat, p_val = stats.ttest_ind(d1, d2)
        comparisons_results.append({
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
            "comparisons": comparisons_results,
            "columns": columns,
            "x_labels": ['0', '5', '10', '20', '30', '50']
        }
    }
    
    # 5. Save Output
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/2.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    process_data(output_file)
