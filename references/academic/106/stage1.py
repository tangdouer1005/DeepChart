import sys
import json
import numpy as np

def compute_data():
    # Raw data extracted directly from the provided Markdown table
    data_dict = {
        'B16-F0 21%O2': [1, 1, 1, 1],
        'B16-F0 1%O2': [1.48403264, 1.68837926, 1.21210873, 1.34768451],
        'B16-F0 1%O2 + Liprox': [1.34308934, 1.43866036, 1.32754921, np.nan],
        
        'B16-F0 FSP1 KO 21%O2': [1, 1, 1, 1],
        'B16-F0 FSP1 KO 1%O2': [2.13260939, 2.40660031, 1.73214387, 1.75709602],
        'B16-F0 FSP1 KO 1%O2 + Liprox': [1.19117817, 1.18719077, 1.18639812, np.nan],
        
        'LN71134BL 21%O2': [1, 1, 1, 1],
        'LN71134BL 1%O2': [2.25799359, 1.9494307, 1.90228148, 2.19323958],
        'LN71134BL 1%O2 + Liprox': [1.15397846, 1.40481629, 1.449258435, np.nan],
        
        'LN71134BL FSP1 KO 21%O2': [1, 1, 1, 1],
        'LN71134BL FSP1 KO 1%O2': [2.78758832, 2.77704055, 2.66783802, 2.87541627],
        'LN71134BL FSP1 KO 1%O2 + Liprox': [1.23286389, 1.24515659, 1.036090783, np.nan]
    }

    # Convert to list of arrays, filtering nans
    # Also keep structure for stats
    cleaned_data = {}
    stats = {}
    
    # We need to maintain order of keys as well for plotting
    keys_order = [
        'B16-F0 21%O2', 'B16-F0 1%O2', 'B16-F0 1%O2 + Liprox',
        'B16-F0 FSP1 KO 21%O2', 'B16-F0 FSP1 KO 1%O2', 'B16-F0 FSP1 KO 1%O2 + Liprox',
        'LN71134BL 21%O2', 'LN71134BL 1%O2', 'LN71134BL 1%O2 + Liprox',
        'LN71134BL FSP1 KO 21%O2', 'LN71134BL FSP1 KO 1%O2', 'LN71134BL FSP1 KO 1%O2 + Liprox'
    ]
    
    data_values_list = []
    means_list = []
    stds_list = []
    
    for key in keys_order:
        raw_vals = data_dict[key]
        clean_vals = [x for x in raw_vals if not np.isnan(x)]
        
        cleaned_data[key] = clean_vals
        data_values_list.append(clean_vals)
        
        mean_val = np.mean(clean_vals)
        std_val = np.std(clean_vals, ddof=1) if len(clean_vals) > 1 else 0
        
        means_list.append(mean_val)
        stds_list.append(std_val)
        
        stats[key] = {
            "mean": mean_val,
            "std": std_val
        }

    output_data = {
        "scr_data": {
            "data_dict": data_dict,
            "keys_order": keys_order
        },
        "der_data": {
            "means": means_list,
            "stds": stds_list
        }
    }
    return output_data

if __name__ == "__main__":
    output_path = "bench/ground_truth_code/nature_1_output/106.json"
    try:
        data = compute_data()
        
        # Need to handle NaN for JSON
        # replace NaN with None in data_dict
        for k, v in data["scr_data"]["data_dict"].items():
            data["scr_data"]["data_dict"][k] = [x if not np.isnan(x) else None for x in v]
            
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to {output_path}")
    except Exception as e:
        print(f"Error computing data: {e}")
        sys.exit(1)
