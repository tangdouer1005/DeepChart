import sys
import io
import pandas as pd
import json

def generate_data(output_filename):
    # 1. Source Data
    # Extracted specifically from the "Fig. 7d" columns in the provided markdown table.
    # Columns: Fraction inhomogeneity [-], Heat power [kW], H2 power (HHV) [kW]
    csv_data = """fraction,heat_power,h2_power
0,14.00411,2.52974
0.11111,13.97707,2.57286
0.22222,13.94922,2.61728
0.33333,13.91881,2.66577
0.44444,13.88884,2.71358
0.55556,13.85947,2.76041
0.66667,13.82843,2.80991
0.77778,13.79622,2.86128
0.88889,13.76039,2.91842
1,13.73574,2.95773
"""

    # Load data
    df = pd.read_csv(io.StringIO(csv_data))

    # Transform X-axis data: Fraction (0-1) to Percentage (0-100)
    df['percent'] = df['fraction'] * 100

    # Save to JSON
    scr_data = df[['fraction', 'heat_power', 'h2_power']].to_dict(orient='records')
    der_data = df[['percent']].to_dict(orient='records')
    
    output_json = {
        "scr_data": scr_data,
        "der_data": der_data
    }
    
    with open(output_filename, 'w') as f:
        json.dump(output_json, f, indent=4)
        
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_path = "bench/ground_truth_code/nature_1_output/33.json"
    generate_data(output_path)
