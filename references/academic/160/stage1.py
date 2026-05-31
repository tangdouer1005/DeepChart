import sys
import io
import pandas as pd
import json
import numpy as np

def compile_data(output_filename):
    # 1. Source Data
    # Embedding the provided markdown data directly
    csv_data = """| million$                               |   Unnamed: 1 |   central estimate of SAF cost |   low SAF cost |   high SAF cost |
|:---------------------------------------|-------------:|-------------------------------:|---------------:|----------------:|
| central estimate of CORSIA offset cost |         2027 |                         2250.3 |         1062.2 |          3057.8 |
| nan                                    |         2028 |                         2016.3 |          803   |          2952.4 |
| nan                                    |         2029 |                         1818.1 |          549.4 |          2888.1 |
| nan                                    |         2030 |                         1655.5 |          301   |          2865   |
| nan                                    |         2031 |                         1528.6 |           58   |          2883.3 |
| nan                                    |         2032 |                         1362.6 |         -180   |          2883.9 |
| nan                                    |         2033 |                         1213.7 |         -381.8 |          2875.3 |
| nan                                    |         2034 |                         1064.8 |         -604.1 |          2909   |
| nan                                    |         2035 |                          915.9 |         -821.1 |          2955.7 |
| nan                                    |          nan |                          nan   |          nan   |           nan   |
| low estimate of CORSIA offset cost     |         2027 |                         2726.8 |         1538.7 |          3534.3 |
| nan                                    |         2028 |                         2599.5 |         1386.2 |          3535.6 |
| nan                                    |         2029 |                         2518.8 |         1250.1 |          3588.8 |
| nan                                    |         2030 |                         2484.7 |         1130.2 |          3694.2 |
| nan                                    |         2031 |                         2497.4 |         1026.7 |          3852.1 |
| nan                                    |         2032 |                         2482.1 |          939.5 |          4003.4 |
| nan                                    |         2033 |                         2464.2 |          868.7 |          4125.8 |
| nan                                    |         2034 |                         2483.1 |          814.2 |          4327.3 |
| nan                                    |         2035 |                         2513   |          776   |          4552.8 |
| nan                                    |          nan |                          nan   |          nan   |           nan   |
| high estimate of CORSIA offset cost    |         2027 |                         1706.5 |          518.4 |          2514   |
| nan                                    |         2028 |                         1349.4 |          136.1 |          2285.5 |
| nan                                    |         2029 |                         1015.4 |         -253.3 |          2085.4 |
| nan                                    |         2030 |                          704.3 |         -650.1 |          1913.8 |
| nan                                    |         2031 |                          416   |        -1054.6 |          1770.7 |
| nan                                    |         2032 |                           75.6 |        -1467   |          1596.9 |
| nan                                    |         2033 |                         -225.2 |        -1820.8 |          1436.4 |
| nan                                    |         2034 |                         -568.3 |        -2237.2 |          1275.9 |
| nan                                    |         2035 |                         -924.4 |        -2661.4 |          1115.4 |"""

    # 2. Data Processing
    # Read as string first to avoid type inference errors on the markdown separator line
    df = pd.read_csv(io.StringIO(csv_data), sep="|", skipinitialspace=True, dtype=str, header=0)
    
    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Remove the first and last columns which are empty due to markdown pipe format
    # The columns are likely ['', 'million$', 'Unnamed: 1', ..., '']
    df = df.iloc[:, 1:-1]
    
    # Rename columns for easier access
    df.columns = ['Category', 'Year', 'Central', 'Low', 'High']
    
    # Drop the separator row (index 0 in the dataframe, which corresponds to the markdown separator line)
    # The original script dropped row 0 assuming it's the markdown separator.
    # But in the provided CSV string, the header line is the first one, and then the actual separator is the second.
    # Let's clean it by dropping rows where 'Year' is not a valid number.
    
    # Clean Category column and forward fill
    df['Category'] = df['Category'].str.strip()
    df['Category'] = df['Category'].replace({'nan': np.nan, '': np.nan}).ffill()
    
    # Convert numeric columns, coercing errors to handle 'nan' strings
    cols_to_numeric = ['Year', 'Central', 'Low', 'High']
    for col in cols_to_numeric:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    # Drop rows where Year is NaN (separator rows between data blocks and empty rows)
    df = df.dropna(subset=['Year'])

    # Save to JSON
    output_data = {
        "scr_data": df.to_dict(orient='records'),
        "der_data": []
    }
    
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/160.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compile_data(output_file)
