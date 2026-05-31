import sys
import io
import pandas as pd
import json

# 1. Source Data (Embedded)
csv_data = """
| Fig. 7a              | Unnamed: 1      | Unnamed: 2          |   Unnamed: 3 | Fig. 7b                    | Unnamed: 5      | Unnamed: 6          |   Unnamed: 7 | Fig. 7c                       | Unnamed: 9      | Unnamed: 10         |   Unnamed: 11 | Fig. 7d                    | Unnamed: 13     | Unnamed: 14         |
|:---------------------|:----------------|:--------------------|-------------:|:---------------------------|:----------------|:--------------------|-------------:|:------------------------------|:----------------|:--------------------|--------------:|:---------------------------|:----------------|:--------------------|
| nan                  | nan             | nan                 |          nan | nan                        | nan             | nan                 |          nan | nan                           | nan             | nan                 |           nan | nan                        | nan             | nan                 |
| nan                  | nan             | nan                 |          nan | nan                        | nan             | nan                 |          nan | nan                           | nan             | nan                 |           nan | nan                        | nan             | nan                 |
| Water flowrate [LPM] | Heat power [kW] | H2 power (HHV) [kW] |          nan | Number of EC in series [-] | Heat power [kW] | H2 power (HHV) [kW] |          nan | Fraction increase PV area [-] | Heat power [kW] | H2 power (HHV) [kW] |           nan | Fraction inhomogeneity [-] | Heat power [kW] | H2 power (HHV) [kW] |
| 4                    | 12.54969        | 2.56383             |          nan | 30                         | 14.06738        | 2.42885             |          nan | -0.01                         | 14.00903        | 2.44504             |           nan | 0                          | 14.00411        | 2.52974             |
| 4.22222              | 12.94205        | 2.55607             |          nan | 31                         | 14.0313         | 2.48638             |          nan | 0.00222                       | 13.99935        | 2.55441             |           nan | 0.11111                    | 13.97707        | 2.57286             |
| 4.44444              | 13.30578        | 2.54881             |          nan | 32                         | 14.00105        | 2.53463             |          nan | 0.01444                       | 13.99101        | 2.66164             |           nan | 0.22222                    | 13.94922        | 2.61728             |
| 4.66667              | 13.64379        | 2.54199             |          nan | 33                         | 13.97772        | 2.57183             |          nan | 0.02667                       | 13.98485        | 2.7654              |           nan | 0.33333                    | 13.91881        | 2.66577             |
| 4.88889              | 13.95868        | 2.53551             |          nan | 34                         | 13.95487        | 2.60828             |          nan | 0.03889                       | 13.97775        | 2.87066             |           nan | 0.44444                    | 13.88884        | 2.71358             |
| 5.11111              | 14.25273        | 2.52925             |          nan | 35                         | 13.94783        | 2.6195              |          nan | 0.05111                       | 13.96978        | 2.9773              |           nan | 0.55556                    | 13.85947        | 2.76041             |
| 5.33333              | 14.52797        | 2.52308             |          nan | 36                         | 13.93679        | 2.63711             |          nan | 0.06333                       | 13.96196        | 3.0837              |           nan | 0.66667                    | 13.82843        | 2.80991             |
| 5.55556              | 14.78616        | 2.51698             |          nan | 37                         | 13.92168        | 2.66119             |          nan | 0.07556                       | 13.95426        | 3.18993             |           nan | 0.77778                    | 13.79622        | 2.86128             |
| 5.77778              | 15.02868        | 2.51115             |          nan | 38                         | 13.95207        | 2.61274             |          nan | 0.08778                       | 13.94662        | 3.29604             |           nan | 0.88889                    | 13.76039        | 2.91842             |
| 6                    | 15.25653        | 2.5061              |          nan | 39                         | 13.94198        | 2.62883             |          nan | 0.1                           | 13.93902        | 3.40209             |           nan | 1                          | 13.73574        | 2.95773             |
| nan                  | nan             | nan                 |          nan | 40                         | 13.93424        | 2.64117             |          nan | nan                           | nan             | nan                 |           nan | nan                        | nan             | nan                 |
| nan                  | nan             | nan                 |          nan | 41                         | 13.92495        | 2.65599             |          nan | nan                           | nan             | nan                 |           nan | nan                        | nan             | nan                 |
| nan                  | nan             | nan                 |          nan | 42                         | 13.9187         | 2.66595             |          nan | nan                           | nan             | nan                 |           nan | nan                        | nan             | nan                 |
| nan                  | nan             | nan                 |          nan | 43                         | 13.9798         | 2.56851             |          nan | nan                           | nan             | nan                 |           nan | nan                        | nan             | nan                 |
| nan                  | nan             | nan                 |          nan | 44                         | 14.13696        | 2.31789             |          nan | nan                           | nan             | nan                 |           nan | nan                        | nan             | nan                 |
| nan                  | nan             | nan                 |          nan | 45                         | 14.32758        | 2.0139              |          nan | nan                           | nan             | nan                 |           nan | nan                        | nan             | nan                 |
"""

def process_data(csv_text):
    # Read the entire CSV as string first to handle the markdown structure safely
    df = pd.read_csv(io.StringIO(csv_text), sep='|', header=None, dtype=str)
    
    # Clean whitespace from all cells
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    
    # Locate the header row for "Fig. 7b" data
    # We search for the specific column header "Number of EC in series [-]"
    start_row = -1
    col_idx = -1
    
    for r in range(len(df)):
        for c in range(len(df.columns)):
            val = str(df.iloc[r, c]).strip()
            if val == "Number of EC in series [-]":
                start_row = r
                col_idx = c
                break
        if start_row != -1:
            break
            
    if start_row == -1:
        raise ValueError("Could not find the target data header in the provided CSV.")
        
    # Extract the relevant columns: N_EC, Heat Power, H2 Power
    # These are contiguous in the source table: col_idx, col_idx+1, col_idx+2
    # The data starts immediately after the header row
    target_df = df.iloc[start_row+1:, col_idx:col_idx+3].copy()
    target_df.columns = ['N_EC', 'Heat_Power', 'H2_Power']
    
    # Convert columns to numeric
    # errors='coerce' turns "nan" strings and other non-numerics into actual NaNs
    for col in target_df.columns:
        target_df[col] = pd.to_numeric(target_df[col], errors='coerce')
        
    # Drop rows where N_EC is NaN (this removes the trailing 'nan' rows)
    target_df = target_df.dropna(subset=['N_EC'])
    
    return target_df

if __name__ == "__main__":
    try:
        df = process_data(csv_data)
        
        # Save to JSON
        output_path = "bench/ground_truth_code/nature_1_output/31.json"
        
        # Convert DataFrame to dictionary records
        data = df.to_dict(orient='records')
        
        output_json = {
            "scr_data": data,
            "der_data": []
        }

        with open(output_path, 'w') as f:
            json.dump(output_json, f, indent=4)
            
        print(f"Data saved to {output_path}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
