import sys
import io
import pandas as pd
import json
import numpy as np

def compile_data(output_filename):
    csv_data = """million$,Unnamed: 1,central estimate of SAF cost,low SAF cost,high SAF cost
central estimate of CORSIA offset cost,2027,823,458.6,2499.9
nan,2028,535.3,153.5,2296.2
nan,2029,277,-153.8,2115.3
nan,2030,60.5,-449.5,1986.5
nan,2031,-114.2,-733.8,1910
nan,2032,-334.8,-1006.6,1804
nan,2033,-535.3,-1237.2,1693.9
nan,2034,-735.8,-1481.9,1626.2
nan,2035,-936.3,-1715.2,1571.3
nan,nan,nan,nan,nan
low estimate of CORSIA offset cost,2027,1299.5,935.1,2976.5
nan,2028,1118.4,736.7,2879.4
nan,2029,977.7,546.9,2816
nan,2030,889.7,379.6,2815.7
nan,2031,854.5,235,2878.7
nan,2032,784.7,112.9,2923.5
nan,2033,715.2,13.3,2944.4
nan,2034,682.4,-63.7,3044.4
nan,2035,660.8,-118.1,3168.4
nan,nan,nan,nan,nan
high estimate of CORSIA offset cost,2027,279.2,-85.2,1956.2
nan,2028,-131.6,-513.4,1629.3
nan,2029,-525.6,-956.5,1312.6
nan,2030,-890.6,-1400.7,1035.3
nan,2031,-1226.8,-1846.4,797.4
nan,2032,-1621.8,-2293.7,516.9
nan,2033,-1974.2,-2676.1,255
nan,2034,-2369,-3115.1,-7
nan,2035,-2776.6,-3555.5,-269
"""

    df = pd.read_csv(io.StringIO(csv_data))

    # Clean and split data into three blocks based on the descriptive label
    df['label'] = df['million$'].replace('nan', pd.NA)
    df['label'] = df['label'].ffill()

    # Drop rows with NaN in year column
    df = df.dropna(subset=['Unnamed: 1'])

    # Rename columns for convenience
    df = df.rename(columns={
        'Unnamed: 1': 'year',
        'central estimate of SAF cost': 'central',
        'low SAF cost': 'low',
        'high SAF cost': 'high'
    })

    # Drop the original 'million$' column as it's been replaced by 'label'
    df = df.drop(columns=['million$'])

    # Convert year to numeric (already done, but ensure consistency)
    df['year'] = pd.to_numeric(df['year'])
    
    # Convert central, low, high to numeric
    for col in ['central', 'low', 'high']:
        df[col] = pd.to_numeric(df[col])

    # Save to JSON
    output_data = {
        "scr_data": df.to_dict(orient='records'),
        "der_data": []
    }
    
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/159.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compile_data(output_file)