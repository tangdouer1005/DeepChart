import sys
import pandas as pd
import numpy as np
import io
import json

def process_data():
    # 1. Source Data Loading
    # Using the exact data provided in the markdown table.
    # We only extract the raw measurement columns (A-J) and the relevant headers.
    csv_data = """
B16-F0,LN1 18IL,LN7 1112AR,LN7 1120BL,LN7 1134BL,LN8 1194BR,LN8 1198AR,LN8 1205BL,LN9 1315BL,LN9 1358IR
0.8299296674003414,1.928546998833788,0.8025826043362723,2.222764945615544,0.37278141648377583,0.6090772699389065,0.5369301638703191,0.13994083686105493,0.5357799907267852,0.5369725529955741
1.0355057637490246,2.146987063268871,0.5586761586545418,1.625153697906596,0.21125251548675206,0.5130045874571015,0.589444402175406,0.10597787396603812,0.7520433000113403,0.735953968614233
1.134564568850634,1.1800532877406624,0.981485217508094,2.496864417961382,0.2840339839626573,0.618016249272412,0.43573465345652695,0.18815322961925368,0.8726564170965828,0.5482852964188359
1.067366156351031,1.139263648683155,0.6828174503771713,1.1651481165731932,0.4938553059954519,0.555341273528883,0.5996181837280969,0.2869213153964222,0.20897275168862095,0.5125056222512814
1.0214732863448737,1.296021888185411,0.8991676521394686,1.54030017361637,0.9079694495974822,0.9781711654635805,0.8639109240152595,0.8911277607591113,1.2240086468234774,1.0522782074088821
0.9111623735995769,0.9354895635383239,0.8518380020755709,1.1177187016815318,0.6916331033068995,0.45367395258469567,1.2218269477581314,0.40339876934736785,0.3036788001925242,0.5448505274112878
0.7882105310868032,1.446763836975741,,,,,,,,
0.9514894525471388,1.7365729543386705,,,,,,,,
1.2603002786479676,1.3206856278467825,,,,,,,,
1.151744305174724,1.5762741597162917,,,,,,,,
0.8150691363293474,1.2557090017283161,,,,,,,,
1.033186952433866,1.2621057179113198,,,,,,,,
1.0000178133667066,1.112049159854708,,,,,,,,
1.0001977922468785,1.3090844939710062,,,,,,,,
1.000081804170821,1.1182582188956112,,,,,,,,
"""
    df = pd.read_csv(io.StringIO(csv_data))

    # 2. Data Preparation
    # Calculate Mean and Std Dev
    means = df.mean().tolist()
    stds = df.std().tolist()
    columns = df.columns.tolist()

    # Rename columns to match the chart labels (adding hyphens)
    # Chart labels: B16-F0, LN1-18IL, LN7-1112AR, etc.
    # Data headers: B16-F0, LN1 18IL, LN7 1112AR, etc.
    new_labels = []
    for col in columns:
        if " " in col:
            new_labels.append(col.replace(" ", "-"))
        else:
            new_labels.append(col)

    # Prepare raw data for JSON (handle NaNs)
    raw_data_dict = {}
    for col in df.columns:
        raw_data_dict[col] = df[col].dropna().tolist()

    output_data = {
        "means": means,
        "stds": stds,
        "columns": columns,
        "new_labels": new_labels,
        "raw_data_points": raw_data_dict # Renamed to avoid confusion with overall raw_data
    }

    # Return both the raw CSV string and the processed data
    # The raw_data in output_data should probably be renamed to raw_data_points or something similar
    return csv_data, output_data

if __name__ == "__main__":
    raw_csv_string, derived_data = process_data()
    
    final_output = {
        "scr_data": raw_csv_string,
        "der_data": derived_data
    }
    
    with open("bench/ground_truth_code/nature_1_output/94.json", "w") as f:
        json.dump(final_output, f, indent=4)
