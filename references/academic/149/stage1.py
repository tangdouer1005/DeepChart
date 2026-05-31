import sys
import io
import pandas as pd
import json

def process_data(output_filename):
    # 1. Source Data Loading
    csv_data = """Unnamed: 0|GHG emission intensity,gCO2e/MJ
MSW transport|2.2
Pre-treatment+Gasification|24
Water gas shift reaction|-13.6
Rectisol Process|92.6
Fischer Tropsch|5.7
Hydrotreating|0.4
Hydrocracking|0.5
Others|9.8
Fuel transport|0.4
Operation|73.2
Biogenic content|-176.7
Credit|-4.3"""

    # Read data
    df = pd.read_csv(io.StringIO(csv_data), sep="|")
    
    # Clean column names and data
    df.columns = [c.strip() for c in df.columns]
    df.rename(columns={df.columns[0]: 'Category', df.columns[1]: 'Value'}, inplace=True)
    df['Category'] = df['Category'].str.strip()
    
    # Save to JSON
    output_data = {
        "scr_data": df.to_dict(orient='records'),
        "der_data": []
    }
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "bench/ground_truth_code/nature_1_output/149.json"
    process_data(output_file)
