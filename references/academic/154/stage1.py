import sys
import io
import pandas as pd
import json
import numpy as np

def compile_data(output_filename):
    # 1. Source Data
    csv_data = """
| Unnamed: 0    | Unnamed: 1   |   central estimate,Mt/yr |   low |   high |
|:--------------|:-------------|-------------------------:|------:|-------:|
| China         | S1           |                      5.8 |   4.3 |    9.5 |
| nan           | S2           |                     11   |   7.5 |   14.8 |
| nan           | S3           |                     16.5 |  11.2 |   22.1 |
| nan           | nan          |                    nan   | nan   |  nan   |
| EU27          | S1           |                      2.8 |   2.1 |    4.7 |
| nan           | S2           |                      5.4 |   3.6 |    7.3 |
| nan           | S3           |                      8.1 |   5.4 |   10.9 |
| nan           | nan          |                    nan   | nan   |  nan   |
| United States | S1           |                      2.6 |   1.9 |    4.4 |
| nan           | S2           |                      5.1 |   3.3 |    7   |
| nan           | S3           |                      7.6 |   5   |   10.4 |
| nan           | nan          |                    nan   | nan   |  nan   |
| India         | S1           |                      2.5 |   1.9 |    4.2 |
| nan           | S2           |                      4.8 |   3.2 |    6.5 |
| nan           | S3           |                      7.2 |   4.8 |    9.7 |
"""

    # 2. Data Processing
    # Read the markdown table. 
    # sep='|' splits by pipe. skipinitialspace=True handles spaces after pipes.
    df = pd.read_csv(io.StringIO(csv_data), sep='|', skipinitialspace=True)

    # Markdown tables often result in empty columns at the start (index 0) and end due to outer pipes.
    # We select the 5 content columns by index: 1, 2, 3, 4, 5.
    df = df.iloc[:, 1:6]

    # Rename columns to standard names
    df.columns = ['Region', 'Scenario', 'Central', 'Low', 'High']

    # Filter out the markdown separator row (e.g., |:---|---|...)
    # This row usually appears as the first data row and contains dashes.
    df = df[~df['Region'].astype(str).str.contains('---')]

    # Strip whitespace from Region before any other checks
    df['Region'] = df['Region'].astype(str).str.strip()
    
    # Replace 'nan' string with actual NaN
    df['Region'] = df['Region'].replace({'nan': np.nan, 'NaN': np.nan})

    # Forward fill the Region column to propagate region names to S2 and S3 rows
    df['Region'] = df['Region'].ffill()
    
    # Filter out spacer rows where Scenario is NaN or 'nan' string
    df = df[df['Scenario'].notna()]
    df = df[df['Scenario'].astype(str).str.strip() != 'nan']

    # Convert numeric columns to float
    cols_numeric = ['Central', 'Low', 'High']
    for col in cols_numeric:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Clean whitespace
    df['Scenario'] = df['Scenario'].astype(str).str.strip()

    # Rename 'United States' to 'US' to match the chart labels
    df['Region'] = df['Region'].replace('United States', 'US')

    # Create the X-axis label (e.g., "China-S1")
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
    output_file = "bench/ground_truth_code/nature_1_output/154.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compile_data(output_file)