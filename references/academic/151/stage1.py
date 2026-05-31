import sys
import io
import pandas as pd
import json
import numpy as np

def compile_data(output_filename):
    # 1. Source Data
    data_str = """
| Unnamed: 0        | Unnamed: 1      |   low,gCO2e/MJ |   high,gCO2e/MJ |
|:------------------|:----------------|---------------:|----------------:|
| MSW management    | MSW composition |           13.9 |            28.1 |
| nan               | MSW moisture    |           11.4 |            16.7 |
| nan               | Pre-treatment   |            9.9 |            14.1 |
| nan               | nan             |          nan   |           nan   |
| SAF production    | Syngas yield    |           10.3 |            16.7 |
| nan               | CO+H2 ratio     |           12.7 |            22.5 |
| nan               | CO conversion   |           14.1 |            15.1 |
| nan               | nan             |          nan   |           nan   |
| Energy and others | Electricity     |            3.6 |            20.9 |
| nan               | Others          |           11.9 |            20.3 |
"""
    
    # Read CSV
    try:
        df = pd.read_csv(io.StringIO(data_str), sep="|", skipinitialspace=True)
    except Exception as e:
        print(f"Error reading data: {e}")
        return

    # Clean columns
    if len(df.columns) >= 5:
        df = df.iloc[:, 1:5]
    
    df.columns = ['Group', 'Parameter', 'Low', 'High']
    
    # Strip whitespace from strings
    # We convert to string first to handle everything uniformly, then replace 'nan'
    df['Group'] = df['Group'].astype(str).str.strip()
    df['Parameter'] = df['Parameter'].astype(str).str.strip()

    # Filter out separator row
    df = df[~df['Group'].str.contains('---')]
    df = df[~df['Group'].str.startswith(':')]

    # Replace 'nan' string with np.nan
    df['Group'] = df['Group'].replace('nan', np.nan)
    df['Parameter'] = df['Parameter'].replace('nan', np.nan)
    
    # Clean data values
    df['Low'] = pd.to_numeric(df['Low'], errors='coerce')
    df['High'] = pd.to_numeric(df['High'], errors='coerce')
    
    # Forward fill Group
    df['Group'] = df['Group'].ffill()
    
    # Remove rows where Parameter is NaN
    df = df.dropna(subset=['Parameter'])
    
    # Save to JSON
    output_data = {
        "scr_data": df.to_dict(orient='records'),
        "der_data": []
    }
    
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/151.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compile_data(output_file)