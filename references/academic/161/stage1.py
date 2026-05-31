import sys
import io
import pandas as pd
import numpy as np
import json

def process_data(output_filename):
    # 1. Source Data
    csv_data = """| million$                               |   Unnamed: 1 |   central estimate of SAF cost |   low SAF cost |   high SAF cost |
|:---------------------------------------|-------------:|-------------------------------:|---------------:|----------------:|
| central estimate of CORSIA offset cost |         2027 |                         -555.1 |         -555.1 |           351.8 |
| nan                                    |         2028 |                         -628.1 |         -668.4 |           134.2 |
| nan                                    |         2029 |                         -692.9 |         -791.4 |           -28.8 |
| nan                                    |         2030 |                         -757.6 |         -925.3 |          -139.5 |
| nan                                    |         2031 |                         -822.3 |        -1070.3 |          -216   |
| nan                                    |         2032 |                         -887.1 |        -1226.5 |          -322   |
| nan                                    |         2033 |                         -951.8 |        -1363   |          -432.1 |
| nan                                    |         2034 |                        -1016.6 |        -1536.2 |          -418.2 |
| nan                                    |         2035 |                        -1081.3 |        -1720.5 |          -344.7 |
| nan                                    |          nan |                          nan   |          nan   |           nan   |
| low estimate of CORSIA offset cost     |         2027 |                          -78.6 |          -78.6 |           828.4 |
| nan                                    |         2028 |                          -44.9 |          -85.2 |           717.4 |
| nan                                    |         2029 |                            7.8 |          -90.7 |           671.9 |
| nan                                    |         2030 |                           71.6 |          -96.1 |           689.7 |
| nan                                    |         2031 |                          146.4 |         -101.6 |           752.7 |
| nan                                    |         2032 |                          232.4 |         -107   |           797.5 |
| nan                                    |         2033 |                          298.7 |         -112.5 |           818.4 |
| nan                                    |         2034 |                          401.7 |         -118   |          1000.1 |
| nan                                    |         2035 |                          515.8 |         -123.4 |          1252.4 |
| nan                                    |          nan |                          nan   |          nan   |           nan   |
| high estimate of CORSIA offset cost    |         2027 |                        -1098.9 |        -1098.9 |          -192   |
| nan                                    |         2028 |                        -1295   |        -1335.3 |          -532.7 |
| nan                                    |         2029 |                        -1495.5 |        -1594   |          -831.4 |
| nan                                    |         2030 |                        -1708.8 |        -1876.5 |         -1090.7 |
| nan                                    |         2031 |                        -1934.9 |        -2182.9 |         -1328.6 |
| nan                                    |         2032 |                        -2174.1 |        -2513.6 |         -1609.1 |
| nan                                    |         2033 |                        -2390.7 |        -2801.9 |         -1871   |
| nan                                    |         2034 |                        -2649.7 |        -3169.4 |         -2051.3 |
| nan                                    |         2035 |                        -2921.6 |        -3560.8 |         -2185   |"""

    # 2. Data Processing
    # Read csv with '|' separator. 
    df = pd.read_csv(io.StringIO(csv_data), sep='|', skipinitialspace=True)
    
    # Clean column names
    df.columns = [c.strip() for c in df.columns]
    
    # Select relevant columns: 'million$', 'Unnamed: 1', 'central...', 'low...', 'high...'
    df = df.iloc[:, 1:6]
    df.columns = ['Scenario', 'Year', 'Central', 'Low', 'High']
    
    # Clean Scenario column: strip whitespace and replace 'nan' string with np.nan
    df['Scenario'] = df['Scenario'].astype(str).str.strip()
    df['Scenario'] = df['Scenario'].replace({'nan': np.nan, 'NaN': np.nan, '': np.nan})
    
    # Forward fill Scenario to propagate labels to rows with 'nan' scenario
    df['Scenario'] = df['Scenario'].ffill()
    
    # Clean Year column: coerce to numeric (handles '---' separator lines)
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    
    # Drop rows where Year is NaN (removes separator lines and empty spacer lines)
    df = df.dropna(subset=['Year'])
    df['Year'] = df['Year'].astype(int)
    
    # Convert numeric columns
    for col in ['Central', 'Low', 'High']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Save to JSON
    data_list = df.to_dict(orient='records')
    output_data = {
        "scr_data": data_list,
        "der_data": []
    }
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/161.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    process_data(output_file)
