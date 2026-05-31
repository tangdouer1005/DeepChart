import sys
import io
import pandas as pd
import json

def compile_data(output_filename):
    # 1. Source Data
    csv_data = """Unnamed: 0,central estimate,low,high
MSW-SAF,102.7,33.1,197
MSW-H2,170.7,69.4,306.6
MSW-PTL,177,81.7,395.3"""

    df = pd.read_csv(io.StringIO(csv_data))

    # Rename columns for clarity if needed, or keep as is. 
    # The original script used 'Unnamed: 0' for category.
    # Let's clean it up slightly for the JSON to be more semantic, 
    # but since I need to respect the original logic, I'll keep the data values exact.
    # I'll rename 'Unnamed: 0' to 'Category' for better JSON structure.
    df = df.rename(columns={'Unnamed: 0': 'Category'})

    # Save to JSON
    output_data = {
        "scr_data": df.to_dict(orient='records'),
        "der_data": []
    }
    
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/153.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compile_data(output_file)
