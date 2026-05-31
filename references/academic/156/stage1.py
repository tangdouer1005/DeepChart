import sys
import io
import pandas as pd
import json

def compile_data(output_filename):
    # 1. Source Data
    csv_data = """Region,Scenario,Central,Low,High
China,S1,18.6,14.4,23.4
nan,S2,35.5,25.3,36.3
nan,S3,57.8,41.6,70.8
nan,nan,nan,nan,nan
EU27,S1,9,7,11.5
nan,S2,17.4,12.2,17.9
nan,S3,28.4,20.1,35
nan,nan,nan,nan,nan
United States,S1,8.3,6.5,10.8
nan,S2,16.5,11.3,17.1
nan,S3,26.8,18.6,33.4
nan,nan,nan,nan,nan
India,S1,8.1,6.3,10.2
nan,S2,15.5,11,15.9
nan,S3,25.3,18.1,31"""

    # Read data into DataFrame
    df = pd.read_csv(io.StringIO(csv_data))

    # 2. Data Cleaning and Preparation
    # Forward fill the Region column to handle the 'nan' values for S2/S3
    df['Region'] = df['Region'].ffill()
    
    # Drop rows where Scenario is NaN (the spacer rows)
    df = df.dropna(subset=['Scenario'])

    # Rename "United States" to "US" to match the chart labels
    df['Region'] = df['Region'].replace('United States', 'US')

    # Create the combined label (e.g., "China-S1")
    df['Label'] = df['Region'] + '-' + df['Scenario']

    # Save to JSON
    output_data = {
        "scr_data": df.to_dict(orient='records'),
        "der_data": []
    }
    
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/156.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compile_data(output_file)
