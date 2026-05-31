import json
import numpy as np

def save_data(output_filename):
    # ---------------------------------------------------------
    # 1. Source Data
    # ---------------------------------------------------------
    # Data extracted directly from the provided table
    vehicle_data = [
        0.6362426544252882, 
        1.3637573455747118, 
        1.3186889049497537, 
        0.7234410435525506, 
        0.6335460026377365, 
        1.2396240761070576, 
        0.7431799017428403, 
        1.4644298527637458, 
        0.8770902182463151
    ]
    
    fsen1_data = [
        0.642841400598503, 
        0.35865193141724816, 
        0.2055757563149134, 
        0.7189498587703381, 
        0.6489407265757056, 
        0.6164231377015815, 
        0.6317029164814143, 
        0.48835837703325524
    ]

    data = {
        "scr_data": {
            "vehicle_data": vehicle_data,
            "fsen1_data": fsen1_data
        },
        "der_data": {}
    }

    with open(output_filename, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    output_file = 'bench/ground_truth_code/nature_1_output/111.json'
    save_data(output_file)
