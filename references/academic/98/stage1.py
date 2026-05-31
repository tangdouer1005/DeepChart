import sys
import json
import numpy as np

# Data extracted directly from the provided Source Data table.
# Row: 'Glutathione'
# Columns mapped to groups based on headers (e.g., F0luc -> B16-F0)
data = {
    "B16-F0":     [455236.1786, 374854.507, 500874.4223],
    "LN1-18IL":   [259322.4689, 325788.1275, 369825.6449],
    "LN7-1112AR": [7253.489863, 17490.64321, 207263.7738],
    "LN7-1120BL": [100374.4682, 150631.574, 224441.8039],
    "LN7-1134BL": [129019.3061, 88956.35534, 233707.8501],
    "LN8-1194BR": [131170.1782, 133441.9365, 123497.4119],
    "LN8-1198AR": [229925.4942, 187742.7464, 177946.004],
    "LN8-1205BL": [162259.7645, 155074.2113, 153575.2223],
    "LN9-1315BL": [284545.951, 240852.6389, 222731.4212],
    "LN9-1358IR": [215774.5807, 206790.9562, 196147.948]
}

scr_data = []
for group, values in data.items():
    for v in values:
        scr_data.append({"Group": group, "Value": v})

der_data = []

output_data = {
    "scr_data": scr_data,
    "der_data": der_data
}

import os
os.makedirs("bench/ground_truth_code/nature_1_output", exist_ok=True)

with open("bench/ground_truth_code/nature_1_output/98.json", "w") as f:
    json.dump(output_data, f, indent=4)
