import sys
import json
import numpy as np

# 1. Data Extraction
# Extracted directly from the provided Markdown table (Row: "Glutamate")
# Parental Group: Columns Unnamed: 1 to Unnamed: 5 (F0luc columns)
parental_values = [
    6204616.859286747,
    6031719.639947483,
    6442731.7845764635,
    6859345.48128456,
    6764765.683211772
]

# LN Group: Columns Unnamed: 12 to Unnamed: 35 (LN columns)
ln_values = [
    1478381.7987170925,
    1081751.8498301418,
    3928401.4065465294,
    3922032.1950288094,
    3110395.9232401457,
    3495866.48103521,
    2662220.3343282263,
    1907977.6288138991,
    2795104.0071977014,
    3534860.737689079,
    3006628.029078749,
    3037851.004063388,
    4632932.147138998,
    3595460.617386489,
    3721260.394931968,
    3859800.6117266854,
    3909206.586895387,
    3731577.4010725464,
    4910662.424020618,
    4314128.730348152,
    4225639.093779526,
    3720654.2353181,
    3489159.2704787264,
    3663818.5393517087
]

scr_data = []
for val in parental_values:
    scr_data.append({"Group": "Parental", "Value": val})
for val in ln_values:
    scr_data.append({"Group": "LN", "Value": val})

der_data = []

output_data = {
    "scr_data": scr_data,
    "der_data": der_data
}

import os
os.makedirs("bench/ground_truth_code/nature_1_output", exist_ok=True)

with open("bench/ground_truth_code/nature_1_output/97.json", "w") as f:
    json.dump(output_data, f, indent=4)
