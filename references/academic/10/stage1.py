import sys
import io
import json
import pandas as pd
from scipy import stats

def process_data(output_filename):
    csv_data = """K5|DCK5|K10|DCK10
11.2415|22.4507|17.7663|40.1504
8.60784|14.6416|11.6146|35.3579
5.80698|21.3465|20.4368|31.5678
4.37638|22.6102|11.9981|31.5956
8.25921|12.2284|21.3436|39.3495
6.33075|19.2196|23.2706|32.4771
7.57759|26.028|18.3738|34.131
6.90356|23.0144|19.8777|nan
11.2284|nan|21.0958|nan
11.5802|nan|21.2376|nan
7.55002|nan|14.488|nan
12.2143|nan|15.5358|nan
5.02523|nan|11.0808|nan"""

    df = pd.read_csv(io.StringIO(csv_data), sep='|')

    data_k5 = df['K5'].dropna().tolist()
    data_dck5 = df['DCK5'].dropna().tolist()
    data_k10 = df['K10'].dropna().tolist()
    data_dck10 = df['DCK10'].dropna().tolist()

    t_stat_5, p_val_5 = stats.ttest_ind(data_k5, data_dck5)
    t_stat_10, p_val_10 = stats.ttest_ind(data_k10, data_dck10)

    output_data = {
        "scr_data": {
            "data": {
                "K5": data_k5,
                "DCK5": data_dck5,
                "K10": data_k10,
                "DCK10": data_dck10
            }
        },
        "der_data": {
            "comparisons": [
                {'name': 'K5 vs DCK5', 'p_val': p_val_5},
                {'name': 'K10 vs DCK10', 'p_val': p_val_10}
            ]
        }
    }
    
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_2_output/10.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    process_data(output_file)
