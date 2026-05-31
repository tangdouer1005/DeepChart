import sys
import json
import numpy as np

# 1. Data Preparation
# Extracted directly from the provided Markdown table under "Glutathione disulfide"
# and mapped to the groups shown in Fig 2h.

data = {
    'B16-F0':     [21863.71235, 24875.51896, 22016.88534, 25814.18798, 27246.77866],
    'LN1-18IL':   [18036.00176, 18830.57124, 19307.19433, 16733.69258, 16079.18642, 17297.56782],
    'LN7-1112AR': [5248.194658, 4320.354879, 15541.98794],
    'LN7-1120BL': [13139.91358, 14483.39718, 13964.36330],
    'LN7-1134BL': [10780.69564, 8743.865759, 13898.34151],
    'LN8-1194BR': [10198.56842, 12314.92301, 11617.38643],
    'LN8-1198AR': [17421.54825, 15474.15213, 16688.72750],
    'LN8-1205BL': [14176.33743, 13151.32158, 15637.46513],
    'LN9-1315BL': [14238.32810, 13632.08987, 13037.78140],
    'LN9-1358IR': [14076.18123, 13737.78268, 14613.45740]
}

# P-values extracted from the image and the "Table Analyzed: Fig 2h" section
p_values = [
    None, # B16-F0
    None, # LN1-18IL
    r"$P = 6.7 \times 10^{-9}$", # LN7-1112AR
    r"$P = 1.2 \times 10^{-5}$", # LN7-1120BL
    r"$P = 2.5 \times 10^{-7}$", # LN7-1134BL
    r"$P = 3.4 \times 10^{-7}$", # LN8-1194BR
    r"$P = 0.0007$",             # LN8-1198AR
    r"$P = 2.4 \times 10^{-5}$", # LN8-1205BL
    r"$P = 8.6 \times 10^{-6}$", # LN9-1315BL
    r"$P = 1.8 \times 10^{-5}$"  # LN9-1358IR
]

scr_data = []
der_data = []

groups = list(data.keys())

for i, group in enumerate(groups):
    # Add source data
    for v in data[group]:
        scr_data.append({"Group": group, "Value": v})
    
    # Add derived data if available
    if i < len(p_values) and p_values[i] is not None:
        der_data.append({
            "Metric": "P-Value", 
            "Group": group, 
            "Value": p_values[i]
        })

output_data = {
    "scr_data": scr_data,
    "der_data": der_data
}

import os
os.makedirs("bench/ground_truth_code/nature_1_output", exist_ok=True)

with open("bench/ground_truth_code/nature_1_output/100.json", "w") as f:
    json.dump(output_data, f, indent=4)
