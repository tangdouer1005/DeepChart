import sys
import io
import numpy as np
import pandas as pd
import json
from scipy import stats

def process_and_save_data(output_filename='bench/ground_truth_code/nature_2_output/75.json'):
    # 1. Source Data (Embedded exactly as provided)
    csv_data = """|
Unnamed: 0   | Unnamed: 1   | Unnamed: 2   | Unnamed: 3   |   Unnamed: 4 |   Unnamed: 5 |   Unnamed: 6 |   Unnamed: 7 |   Unnamed: 8 |   Unnamed: 9 |   Unnamed: 10 |   Unnamed: 11 |   Unnamed: 12 | Unnamed: 13   | Unnamed: 14   | Unnamed: 15   | Unnamed: 16   | Unnamed: 17   | Unnamed: 18   | Unnamed: 19   | Unnamed: 20   | Unnamed: 21   | Unnamed: 22   | Unnamed: 23   | Unnamed: 24         | Unnamed: 25         | Unnamed: 26         | Unnamed: 27         | Unnamed: 28         | Unnamed: 29         | Unnamed: 30         | Unnamed: 31         | Unnamed: 32         | Unnamed: 33         | Unnamed: 34         | Unnamed: 35         | Unnamed: 36         | Unnamed: 37         |
|:-------------|:-------------|:-------------|:-------------|-------------:|-------------:|-------------:|-------------:|-------------:|-------------:|--------------:|--------------:|--------------:|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|
| nan          | NTSR1        | nan          | nan          |    nan       |    nan       |    nan       |    nan       |    nan       |    nan       |     nan       |     nan       |     nan       | No NTSR1      | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 |
| nan          | nan          | nan          | nan          |    nan       |    nan       |    nan       |    nan       |    nan       |    nan       |     nan       |     nan       |     nan       | 3/6/2024      | 3/6/2024      | 3/6/2024      | 3/7/2024      | 3/7/2024      | 3/7/2024      | 3/8/2024      | 3/8/2024      | 3/8/2024      | 6-8-23        | 6-8-23        | 2024-01-25 00:00:00 | 2024-01-25 00:00:00 | 2024-01-25 00:00:00 | 2024-01-26 00:00:00 | 2023-06-29 00:00:00 | 2023-06-29 00:00:00 | 2023-06-29 00:00:00 | 2023-11-22 00:00:00 | 2023-11-22 00:00:00 | 2023-11-22 00:00:00 | 2023-03-17 00:00:00 | 2023-03-17 00:00:00 | 2023-03-23 00:00:00 | 2023-03-23 00:00:00 |
| G15          | -0.09861     | 0.023013*    | 0.015358*    |     -0.1157  |     -0.13439 |     -0.1263  |     -0.119   |     -0.12425 |     -0.12537 |     nan       |     nan       |     nan       | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.03635143578 | 0.02834705032 | 0.0239758348        | 0.02936297897       | 0.03280815393       | 0.02272429095       | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 |
| Gi1          | -0.06814     | -0.06494     | -0.05948     |     -0.12041 |     -0.09415 |     -0.08036 |     -0.10172 |     -0.10296 |     -0.09427 |     nan       |     nan       |     nan       | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | -0.05627221819      | -0.003265948046     | 0.012646862         | 0.02237109425       | 0.03457729744       | 0.003834766583      | -0.01269434146      |
| Gi2          | -0.06814     | -0.06494     | -0.05948     |     -0.12041 |     -0.09415 |     -0.08036 |     -0.10172 |     -0.10296 |     -0.09427 |     nan       |     nan       |     nan       | 0.026585829   | -0.00090738   | 0.007091      | -0.00817      | -0.03506      | -0.04762      | 0.0306        | 0.023158      | -0.00673827   | nan           | nan           | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 |
| GoA          | -0.10739     | -0.13261     | -0.10043     |     -0.12215 |     -0.13214 |     -0.14922 |     -0.08009 |     -0.10627 |     -0.10338 |     nan       |     nan       |     nan       | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan                 | nan                 | nan                 | nan                 | 0.046413            | 0.040247            | 0.050125            | -0.01948815829      | -0.009848719921     | -0.0003642223716    | nan                 | nan                 | nan                 | nan                 |
| GoB          | -0.10066     | -0.12493     | -0.10246     |     -0.11339 |     -0.15058 |     -0.13409 |     -0.17886 |     -0.19844 |     -0.17703 |      -0.14779 |      -0.18754 |      -0.17204 | -0.0059671    | -0.0809716    | -0.05614      | -0.05503      | -0.05067      | -0.04166      | -0.07838      | -0.06805      | -0.02149      | nan           | nan           | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 |
| Gg           | -0.05587     | -0.03747     | -0.02696     |     -0.06502 |     -0.06803 |     -0.05858 |     -0.04931 |     -0.03871 |     -0.04315 |      -0.04863 |      -0.07383 |      -0.04347 | 0.028911      | 0.011637      | 0.021725      | 0.033632      | 0.02368       | 0.011402      | 0.0698347     | 0.0629408     | 0.02384818    | nan           | nan           | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 |
| G12          | -0.10272     | -0.14475     | -0.10265     |     -0.12409 |     -0.14208 |     -0.15277 |     -0.20006 |     -0.23637 |     -0.2368  |     nan       |     nan       |     nan       | -0.05611      | -0.00916      | -0.01579454   | -0.01273      | -0.01917      | -0.04146      | -0.01826      | -0.00963      | -0.0203       | nan           | nan           | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | 0.02153082363       | 0.02811099579       | 0.04487437074       | nan                 | nan                 | nan                 | nan                 |
| G13          | -0.18362     | -0.18632     | -0.15875     |     -0.27634 |     -0.24043 |     -0.24637 |     -0.28347 |     -0.29985 |     -0.26862 |     nan       |     nan       |     nan       | -0.04172175   | -0.02928817   | -0.05098181   | -0.01676      | -0.0028       | -0.04314      | -0.07779      | -0.05963      | -0.05236      | nan           | nan           | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 |
"""

    # 2. Data Processing
    data_lines = csv_data.strip().split('\n')
    data_lines = [l for l in data_lines if not l.strip().startswith('|:')]
    
    header_line = data_lines[0]
    headers = [h.strip() for h in header_line.split('|')]
    if headers[0] == '': headers.pop(0)
    if headers[-1] == '': headers.pop(-1)
    
    rows = []
    for line in data_lines[1:]:
        vals = [v.strip() for v in line.split('|')]
        if vals[0] == '': vals.pop(0)
        if vals[-1] == '': vals.pop(-1)
        rows.append(vals)
        
    df = pd.DataFrame(rows)
    data_rows = df.iloc[2:].copy()
    
    proteins = ['G15', 'Gi1', 'Gi2', 'GoA', 'GoB', 'Gg', 'G12', 'G13']
    
    output_data = []
    
    for _, row in data_rows.iterrows():
        protein_name = row.iloc[0].strip()
        if protein_name not in proteins:
            continue
            
        ntsr1_raw = row.iloc[1:13].values
        no_ntsr1_raw = row.iloc[13:].values
        
        def clean_and_convert(val_list):
            cleaned = []
            for v in val_list:
                s = str(v).strip()
                if s == 'nan' or s == '':
                    continue
                if '*' in s:
                    continue 
                try:
                    val = -1 * float(s)
                    cleaned.append(val)
                except ValueError:
                    continue
            return cleaned

        vals_ntsr1 = clean_and_convert(ntsr1_raw)
        vals_no_ntsr1 = clean_and_convert(no_ntsr1_raw)
        
        # Calculate P-value
        p_val = 1.0
        if len(vals_ntsr1) >= 2 and len(vals_no_ntsr1) >= 2:
            _, p_val = stats.ttest_ind(vals_ntsr1, vals_no_ntsr1)
        
        output_data.append({
            'protein': protein_name,
            'ntsr1': vals_ntsr1,
            'no_ntsr1': vals_no_ntsr1,
            'p_value': float(p_val)
        })

    return df, output_data

if __name__ == "__main__":
    df, processed_data = process_and_save_data()
    
    final_output = {
        "scr_data": df.to_dict(orient='records'),
        "der_data": processed_data
    }
    
    with open('bench/ground_truth_code/nature_1_output/75.json', 'w') as f:
        json.dump(final_output, f, indent=4)