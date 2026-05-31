import pandas as pd
import numpy as np
import json
import os

def process_data(output_filename='bench/ground_truth_code/nature_2_output/86.json'):
    # 2. Source Data Extraction
    # Data manually extracted from the provided Markdown table
    raw_data = {
        0: [22.24282, 24.3151, 33.77154006],
        1: [29.69386628, 35.7741, 26.7349662, 17.4729],
        2: [27.76888379, 31.5131, 34.78990566],
        3: [21.63897886, 18.9419, 24.82969103],
        4: [22.8033279, 18.9751, 16.29963747],
        5: [14.40172411, 15.255, 15.71326136],
        6: [13.65891836, 14.7051, 11.66789317, 26.5091, 12.755],
        7: [9.399249219, 13.8694, 12.82817673],
        8: [9.341106996, 11.7371, 12.8697357],
        9: [13.1699329, 17.5931]
    }

    # Flatten data into a DataFrame
    data_rows = []
    for gen, values in raw_data.items():
        for val in values:
            if not np.isnan(val):
                data_rows.append({'Generation': gen, 'TPM': val})
    
    df = pd.DataFrame(data_rows)

    return raw_data, df

if __name__ == "__main__":
    raw_data, processed_df = process_data()
    
    final_output = {
        "scr_data": raw_data,
        "der_data": processed_df.to_dict(orient='records')
    }
    
    output_filename = 'bench/ground_truth_code/nature_1_output/86.json'
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    with open(output_filename, 'w') as f:
        json.dump(final_output, f, indent=4)
    print(f"Data saved to {output_filename}")