import sys
import io
import pandas as pd
import json
import numpy as np

def compile_data(output_filename):
    # 1. Source Data Loading
    csv_data = """
| million$                               |   Unnamed: 1 |   central estimate of SAF cost |   low SAF cost |   high SAF cost |
|:---------------------------------------|-------------:|-------------------------------:|---------------:|----------------:|
| central estimate of CORSIA offset cost |         2027 |                         3413.1 |         1962.7 |          4236.8 |
| nan                                    |         2028 |                         3374   |         1859.9 |          4350.1 |
| nan                                    |         2029 |                         3335   |         1734   |          4465.8 |
| nan                                    |         2030 |                         3310.8 |         1590.8 |          4595.4 |
| nan                                    |         2031 |                         3317.2 |         1436.4 |          4751.7 |
| nan                                    |         2032 |                         3044.9 |         1173.7 |          4632.6 |
| nan                                    |         2033 |                         2712.1 |          850.7 |          4464.3 |
| nan                                    |         2034 |                         2379.4 |          565.7 |          4294.6 |
| nan                                    |         2035 |                         2046.7 |          303.2 |          4141   |
| nan                                    |          nan |                          nan   |          nan   |           nan   |
| low estimate of CORSIA offset cost     |         2027 |                         3784.4 |         2333.9 |          4608   |
| nan                                    |         2028 |                         3833.8 |         2319.6 |          4809.9 |
| nan                                    |         2029 |                         3894   |         2293   |          5024.8 |
| nan                                    |         2030 |                         3980.3 |         2260.3 |          5264.9 |
| nan                                    |         2031 |                         4108.8 |         2228   |          5543.2 |
| nan                                    |         2032 |                         3970.6 |         2099.4 |          5558.3 |
| nan                                    |         2033 |                         3802.5 |         1941.1 |          5554.7 |
| nan                                    |         2034 |                         3633   |         1819.3 |          5548.2 |
| nan                                    |         2035 |                         3477.4 |         1734   |          5571.8 |
| nan                                    |          nan |                          nan   |          nan   |           nan   |
| high estimate of CORSIA offset cost    |         2027 |                         2989.5 |         1539   |          3813.1 |
| nan                                    |         2028 |                         2848.2 |         1334.1 |          3824.4 |
| nan                                    |         2029 |                         2694.6 |         1093.6 |          3825.4 |
| nan                                    |         2030 |                         2542.8 |          822.8 |          3827.4 |
| nan                                    |         2031 |                         2408.1 |          527.3 |          3842.6 |
| nan                                    |         2032 |                         1980.6 |          109.4 |          3568.3 |
| nan                                    |         2033 |                         1457.5 |         -403.9 |          3209.7 |
| nan                                    |         2034 |                          935.9 |         -877.9 |          2851.1 |
| nan                                    |         2035 |                          398.1 |        -1345.4 |          2492.4 |
"""

    # Parse the markdown table
    # Use '|' as separator, skip initial spaces.
    df = pd.read_csv(io.StringIO(csv_data), sep="|", skipinitialspace=True)
    
    # Clean column names: remove whitespace
    df.columns = [c.strip() for c in df.columns]
    
    # The markdown format results in empty first and last columns (due to leading/trailing pipes), remove them
    df = df.iloc[:, 1:-1]
    
    # Rename columns for easier access
    df.columns = ['Scenario', 'Year', 'Central', 'Low', 'High']
    
    # Clean 'Scenario' column: strip whitespace and replace string 'nan' with np.nan
    df['Scenario'] = df['Scenario'].astype(str).str.strip()
    df['Scenario'] = df['Scenario'].replace({'nan': np.nan, 'None': np.nan})
    
    # Forward fill the 'Scenario' column to propagate the group names
    df['Scenario'] = df['Scenario'].ffill()
    
    # Coerce 'Year' to numeric. This handles 'nan' strings, separator lines '---', etc. by turning them into NaN
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    
    # Drop rows where Year is NaN (this removes the separator rows and empty spacer rows)
    df = df.dropna(subset=['Year'])
    
    # Convert Year to integer
    df['Year'] = df['Year'].astype(int)
    
    # Convert data columns to numeric
    for col in ['Central', 'Low', 'High']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Save to JSON
    output_data = {
        "scr_data": df.to_dict(orient='records'),
        "der_data": []
    }
    
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/158.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compile_data(output_file)
