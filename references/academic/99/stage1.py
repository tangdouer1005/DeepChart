import sys
import json
import numpy as np

# ---------------------------------------------------------
# 1. Source Data Extraction
# ---------------------------------------------------------
# Data extracted directly from the provided Markdown table.
# Row: "Glutathione"
# Group 1: "Parental" (Columns F0luc-1 to F0luc-3)
# Group 2: "LN" (Columns LN7... to LN9...)

parental_data = [
    455236.17862429336, 
    374854.50703331234, 
    500874.4223320226, 
    466937.56824526587, 
    526218.035058101
]

ln_data = [
    # LN7 1112AR
    7253.489863424753, 17490.643208638903, 207263.77376446282,
    # LN7 1120BL
    100374.46817310246, 150631.5739676901, 224441.8038986802,
    # LN7 1134BL
    129019.30608176917, 88956.35533622571, 233707.8500794956,
    # LN8 1194BR
    131170.17823033908, 133441.93648697663, 123497.4118948018,
    # LN8 1198AR
    229925.4941502907, 187742.7464008859, 177946.0039862014,
    # LN8 1205BL
    162259.7645429363, 155074.21131701427, 153575.2223311653,
    # LN9 1315BL
    284545.9510167087, 240852.638916042, 222731.42120165497,
    # LN9 1358IR
    215774.5807455938, 206790.9561720754, 196147.94800028956
]

scr_data = []
for val in parental_data:
    scr_data.append({"Group": "Parental", "Value": val})
for val in ln_data:
    scr_data.append({"Group": "LN", "Value": val})

der_data = []

output_data = {
    "scr_data": scr_data,
    "der_data": der_data
}

import os
os.makedirs("bench/ground_truth_code/nature_1_output", exist_ok=True)

with open("bench/ground_truth_code/nature_1_output/99.json", "w") as f:
    json.dump(output_data, f, indent=4)
