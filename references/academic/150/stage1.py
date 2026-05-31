import sys
import io
import pandas as pd
import json

def process_data(output_filename):
    # 1. Source Data
    csv_data = """Combustion,73.2
Others,4.7
Transport,2.6
Loss,103.5
Electricity,10.5
Heat,0.6
Credits,-4.3
Biogenic,-176.7"""

    # Load data
    df = pd.read_csv(io.StringIO(csv_data), header=None, names=['Category', 'Value'])
    
    # Save to JSON
    output_data = {
        "scr_data": df.to_dict(orient='records'),
        "der_data": []
    }
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "bench/ground_truth_code/nature_1_output/150.json"
    process_data(output_file)
