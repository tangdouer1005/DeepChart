import sys
import json
import io
import pandas as pd
import numpy as np

def get_source_data():
    csv_data = """| Fig. 5d | Unnamed: 1 | Unnamed: 2 | Unnamed: 3 | Unnamed: 4 | Unnamed: 5 | Unnamed: 6 | Unnamed: 7 | Unnamed: 8 | Unnamed: 9 |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| Relative viability (%) | nan | nan | nan | nan | nan | nan | nan | nan | nan |
| F0Luc - Vehicule | F0Luc - viFSP1 (30 μM) | F0Luc - BSO (1mM) | F0Luc - viFSP1 (30 μM) + BSO (1mM) | F0Luc - viFSP1 (30 μM) + BSO (1mM) + Liprox (1μM) | LN8 - Vehicule | LN8 - viFSP1 (30 μM) | LN8 - BSO (1mM) | LN8 - viFSP1 (30 μM) + BSO (1mM) | LN8 -  viFSP1 (30 μM) + BSO (1mM) + Liprox (1μM) |
| 98.225957 | 98.8795518 | 74.4164332 | 78.2446312 | 105.50887 | 104.461688 | 110.766246 | 65.1794374 | 42.5800194 | 89.1367604 |
| 102.240896 | 102.521008 | 83.56676 | 89.9159664 | 99.1596639 | 98.6420951 | 100.969932 | 66.9253152 | 48.5935984 | 85.6450048 |
| 99.5331466 | 97.5723623 | 77.9645191 | 83.8468721 | 106.90943 | 97.0902037 | 95.4413191 | 63.5305529 | 51.2124151 | 86.3239573 |
"""
    # Read the markdown table format.
    df = pd.read_csv(io.StringIO(csv_data), sep="|", header=3, skipinitialspace=True)
    df.columns = [c.strip() for c in df.columns]
    df = df.iloc[:, 1:-1]
    df = df.apply(pd.to_numeric, errors='coerce')
    return df

def compute_stats():
    df = get_source_data()
    means = df.mean(axis=0).values.tolist()
    
    output_data = {
        "scr_data": df.to_dict(orient='list'),
        "der_data": {
            "means": means
        }
    }
    return output_data

if __name__ == "__main__":
    output_path = "bench/ground_truth_code/nature_1_output/107.json"
    try:
        data = compute_stats()
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to {output_path}")
    except Exception as e:
        print(f"Error computing data: {e}")
        sys.exit(1)
