import sys
import json

# ---------------------------------------------------------
# 1. Data Preparation
# ---------------------------------------------------------
# Data extracted exactly from the provided Source Data table.

# Column: Fig. 1j (Parental)
parental_data = [
    1, 
    1.000328, 
    1.000005, 
    0.861667, 
    1.003191, 
    1.136075, 
    1
]

# Column: Unnamed: 1 (Lymph node / LN)
ln_data = [
    0.587407, 0.932256, 0.847907, 0.563434468, 1.054753, 
    1.447167, 1.117306, 0.270697051, 0.731263444, 0.744321601, 
    0.463934401, 0.179749188, 0.782426964, 0.479145444, 0.70873371, 
    1.548417104, 1.414139626, 0.485153079, 1.03000271, 0.782000195, 
    0.492599693, 0.953486003, 0.618357257, 0.371824586, 0.625783402, 
    0.705343274, 0.451463534, 0.33207914, 0.455197984, 0.453811153, 
    0.537530998, 0.160409973, 0.327652464, 0.318659655
]

output_data = {
    "parental_data": parental_data,
    "ln_data": ln_data
}

final_output = {
    "scr_data": {
        "parental_raw": parental_data,
        "ln_raw": ln_data
    },
    "der_data": output_data
}

with open("bench/ground_truth_code/nature_1_output/93.json", "w") as f:
    json.dump(final_output, f, indent=4)
