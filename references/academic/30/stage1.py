import sys
import pandas as pd
import json
import os
import io

csv_data = """flow_rate,heat_power,h2_power
4,12.54969,2.56383
4.22222,12.94205,2.55607
4.44444,13.30578,2.54881
4.66667,13.64379,2.54199
4.88889,13.95868,2.53551
5.11111,14.25273,2.52925
5.33333,14.52797,2.52308
5.55556,14.78616,2.51698
5.77778,15.02868,2.51115
6,15.25653,2.5061
"""

def process_data(output_filename):
    df = pd.read_csv(io.StringIO(csv_data))
    
    # Prepare output data structure
    output_data = {
        "scr_data": {
            "plot_data": df.to_dict(orient='records')
        },
        "der_data": {}
    }
    
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
        
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_2_output/30.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    process_data(output_file)
