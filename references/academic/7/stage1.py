import sys
import io
import json
import pandas as pd
from scipy import stats

def process_data(output_filename):
    csv_data = """vehicle_K,dipy_K
20.2038371448114,17.2002793898328
28.2841222234369,14.5098132817267
17.6957721587514,7.73067754218708
24.5982083872017,16.8116512414254
4.51862967654018,2.32638463554246
22.5550309385981,17.2686735656735
9.47358789887242,1.96725015719119
12.6892037800691,6.56186138881869"""

    df = pd.read_csv(io.StringIO(csv_data))

    # Calculate Paired T-test
    v = df['vehicle_K']
    d = df['dipy_K']
    t_stat, p_val = stats.ttest_rel(v, d)
    
    output_data = {
        "scr_data": {
            "raw_data": {
                "vehicle_K": v.tolist(),
                "dipy_K": d.tolist()
            }
        },
        "der_data": {
            "comparison": {
                "t_stat": t_stat,
                "p_val": p_val
            }
        }
    }
    
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_2_output/7.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    process_data(output_file)
