import sys
import io
import pandas as pd
import json

def compile_data(output_filename):
    # 1. Load Source Data
    csv_data = """Unnamed: 0,Unnamed: 1,central estimate,low,high
MSW-SAF,MSW management,14.1,8.1,30.1
nan,SAF production,nan,8.6,33.5
nan,Energy and Others,nan,10.4,24.7
nan,nan,nan,nan,nan
MSW-H2,MSW management,7.3,3.2,17.3
nan,SAF production,nan,3.6,20.3
nan,Energy and Others,nan,5.1,11.5
nan,nan,nan,nan,nan
MSW-PTL,MSW management,25.4,23.4,30.3
nan,SAF production,nan,23.6,31.8
nan,Energy and Others,nan,7.6,30.8"""

    # Read data
    df = pd.read_csv(io.StringIO(csv_data))
    
    # Clean Data
    # Forward fill the group column (Unnamed: 0)
    df['Unnamed: 0'] = df['Unnamed: 0'].ffill()
    # Drop rows where 'low' or 'high' is NaN (the spacer rows in the source)
    df = df.dropna(subset=['low', 'high'])
    
    # Rename columns for clarity
    df.columns = ['Group', 'Subcategory', 'Central', 'Low', 'High']
    
    # Save to JSON
    output_data = {
        "scr_data": df.to_dict(orient='records'),
        "der_data": []
    }
    
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/152.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compile_data(output_file)
