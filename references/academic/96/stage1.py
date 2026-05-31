import sys
import io
import pandas as pd
import numpy as np
import json

# 1. Source Data Embedding
# We embed the raw markdown table data as a string to ensure data integrity.
csv_data = """
| Fig. 2d-k                                 | Unnamed: 1         | Unnamed: 2         | Unnamed: 3                          | Unnamed: 4         | Unnamed: 5         | Unnamed: 6         | Unnamed: 7         | Unnamed: 8         | Unnamed: 9         | Unnamed: 10        | Unnamed: 11       | Unnamed: 12                             | Unnamed: 13        | Unnamed: 14        | Unnamed: 15        | Unnamed: 16        | Unnamed: 17        | Unnamed: 18        | Unnamed: 19        | Unnamed: 20        | Unnamed: 21        | Unnamed: 22        | Unnamed: 23        | Unnamed: 24        | Unnamed: 25        | Unnamed: 26        | Unnamed: 27        | Unnamed: 28        | Unnamed: 29        | Unnamed: 30        | Unnamed: 31        | Unnamed: 32        | Unnamed: 33        | Unnamed: 34        | Unnamed: 35        |
|:------------------------------------------|:-------------------|:-------------------|:------------------------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:------------------|:----------------------------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|
| Peak intensity                            | nan                | nan                | nan                                 | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan               | nan                                     | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| Data normalized                           | F0luc-2            | F0luc-3            | F0luc-1                             | F0luc-2            | F0luc-3            | F018IL-1           | F018IL-2           | F018IL-3           | F018IL-1           | F018IL-2           | F018IL-3          | LN7 1112AR-1                            | LN7 1112AR-2       | LN7 1112AR-3       | LN7 1120BL-1       | LN7 1120BL-2       | LN7 1120BL-3       | LN7 1134BL-1       | LN7 1134BL-2       | LN7 1134BL-3       | LN8 1194BR-1       | LN8 1194BR-2       | LN8 1194BR-3       | LN8 1198AR-1       | LN8 1198AR-2       | LN8 1198AR-3       | LN8 1205BL-1       | LN8 1205BL-2       | LN8 1205BL-3       | LN9 1315BL-1       | LN9 1315BL-2       | LN9 1315BL-3       | LN9 1358IR-1       | LN9 1358IR-2       | LN9 1358IR-3       |
| Glutamate                                 | 6204616.859286747  | 6031719.639947483  | 6442731.7845764635                  | 6859345.48128456   | 6764765.683211772  | 5488684.552477316  | 5918369.731594182  | 6200610.378068406  | 4942033.196682305  | 4714026.530272788  | 5095178.247521065 | 1478381.7987170925                      | 1081751.8498301418 | 3928401.4065465294 | 3922032.1950288094 | 3110395.9232401457 | 3495866.48103521   | 2662220.3343282263 | 1907977.6288138991 | 2795104.0071977014 | 3534860.737689079  | 3006628.029078749  | 3037851.004063388  | 4632932.147138998  | 3595460.617386489  | 3721260.394931968  | 3859800.6117266854 | 3909206.586895387  | 3731577.4010725464 | 4910662.424020618  | 4314128.730348152  | 4225639.093779526  | 3720654.2353181    | 3489159.2704787264 | 3663818.5393517087 |
| Glutathione                               | 455236.17862429336 | 374854.50703331234 | 500874.4223320226                   | 466937.56824526587 | 526218.035058101   | 259322.46890358912 | 325788.12749423034 | 369825.64488186385 | 320443.13257528073 | 394602.5657019295  | 528401.2831849745 | 7253.489863424753                       | 17490.643208638903 | 207263.77376446282 | 100374.46817310246 | 150631.5739676901  | 224441.8038986802  | 129019.30608176917 | 88956.35533622571  | 233707.8500794956  | 131170.17823033908 | 133441.93648697663 | 123497.4118948018  | 229925.4941502907  | 187742.7464008859  | 177946.0039862014  | 162259.7645429363  | 155074.21131701427 | 153575.2223311653  | 284545.9510167087  | 240852.638916042   | 222731.42120165497 | 215774.5807455938  | 206790.9561720754  | 196147.94800028956 |
| Glutathione disulfide                     | 21863.712354984018 | 24875.51895888996  | 22016.88534472098                   | 25814.18797596233  | 27246.77866410799  | 18036.00175694034  | 18830.5712372072   | 19307.194332221385 | 16733.692576658657 | 16079.186418829011 | 17297.56781852486 | 5248.1946577061535                      | 4320.354879247093  | 15541.987943068676 | 13139.913582885727 | 14483.39717982995  | 13964.363297837686 | 10780.695635644199 | 8743.865759079777  | 13898.341508026346 | 10198.568416990754 | 12314.923007748532 | 11617.386425505598 | 17421.548254970465 | 15474.152131782945 | 16688.727498423043 | 14176.337430747923 | 13151.321576226404 | 15637.465129727156 | 14238.328096084297 | 13632.089870994174 | 13037.781395889358 | 14076.181229212425 | 13737.782678088366 | 14613.457395722215 |
| nan                                       | nan                | nan                | nan                                 | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan               | nan                                     | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| nan                                       | nan                | nan                | nan                                 | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan               | nan                                     | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| Stadistical test                          | nan                | nan                | nan                                 | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan               | nan                                     | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| Table Analyzed                            | Fig. 2d            | nan                | Dunnett's multiple comparisons test | Mean diff.         | 95.00% CI of diff. | Below threshold?   | Summary            | Adjusted P Value   | A-?                | nan                | nan               | Table Analyzed                          | nan                | Fig. 2e            | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| Data sets analyzed                        | A-J                | nan                | B16-F0 vs. LN1 18IL                 | 1067485            | 8231 to 2126740    | Yes                | *                  | 0.047510547790651  | B                  | LN1 18IL           | nan               | nan                                     | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| Distribution assumption                   | Normal (Gaussian)  | nan                | B16-F0 vs. LN7 1112AR               | 4297791            | 3020282 to 5575300 | Yes                | ****               | 3.623749e-09       | C                  | LN7 1112AR         | nan               | Column B                                | nan                | Lymph node         | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| nan                                       | nan                | nan                | B16-F0 vs. LN7 1120BL               | 2951204            | 1673695 to 4228713 | Yes                | ****               | 3.594651952e-06    | D                  | LN7 1120BL         | nan               | vs.                                     | nan                | vs.                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| ANOVA summary                             | nan                | nan                | B16-F0 vs. LN7 1134BL               | 4005535            | 2728026 to 5283044 | Yes                | ****               | 1.4586543e-08      | E                  | LN7 1134BL         | nan               | Column A                                | nan                | Parental           | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| F                                         | 19.38              | nan                | B16-F0 vs. LN8 1194BR               | 3267523            | 1990013 to 4545032 | Yes                | ****               | 6.3676645e-07      | F                  | LN8 1194BR         | nan               | nan                                     | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| P value                                   | 3.640803e-09       | nan                | B16-F0 vs. LN8 1198AR               | 2477418            | 1199909 to 3754927 | Yes                | ****               | 5.3467408461e-05   | G                  | LN8 1198AR         | nan               | Unpaired t test with Welch's correction | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| P value summary                           | ****               | nan                | B16-F0 vs. LN8 1205BL               | 2627108            | 1349599 to 3904617 | Yes                | ****               | 2.2519176402e-05   | H                  | LN8 1205BL         | nan               | P value                                 | nan                | 4.96471e-10        | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| Significant diff. among means (P < 0.05)? | Yes                | nan                | B16-F0 vs. LN9 1315BL               | 1977159            | 699650 to 3254668  | Yes                | **                 | 0.001000242673301  | I                  | LN9 1315BL         | nan               | P value summary                         | nan                | ****               | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| R squared                                 | 0.8746             | nan                | B16-F0 vs. LN9 1358IR               | 2836092            | 1558583 to 4113601 | Yes                | ****               | 6.852518877e-06    | J                  | LN9 1358IR         | nan               | Significantly different (P < 0.05)?     | nan                | Yes                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
"""

# 2. Data Parsing
# Read the markdown table format
df_raw = pd.read_csv(io.StringIO(csv_data), sep="|", header=None, skipinitialspace=True)

# Clean up column names and whitespace
df_raw = df_raw.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

# Extract Data Values (Row with "Glutamate")
# The row index for "Glutamate" is 3 (0-based index in the provided snippet, but let's find it dynamically)
glutamate_row_idx = df_raw[df_raw[1] == 'Glutamate'].index[0]
header_row_idx = df_raw[df_raw[1] == 'Data normalized'].index[0]

# Extract headers (Group names) and Values
# Columns 2 to 36 contain the data (indices 1 to 35 in 0-based pandas, but read_csv with | creates empty first/last cols)
# Let's inspect the dataframe structure. The markdown | creates an empty column at 0 and at the end.
# Data starts at column 2 (index 2) which corresponds to 'Unnamed: 1' in the source.

headers = df_raw.iloc[header_row_idx, 2:-1].values
values = df_raw.iloc[glutamate_row_idx, 2:-1].values

# Create a clean DataFrame for plotting
current_group = None
group_map = {} # To store list of values for each group
group_order = []

for h, v in zip(headers, values):
    if pd.isna(h) or pd.isna(v):
        continue
        
    # Determine Group Name based on header prefix
    if "F0luc" in h:
        group_name = "B16-F0"
    elif "F018IL" in h:
        group_name = "LN1-18IL"
    else:
        # Extract the main part, e.g., "LN7 1112AR" from "LN7 1112AR-1"
        # Split by '-' and take everything before the last part if it ends in digit
        parts = h.rsplit('-', 1)
        group_name = parts[0].strip()
        # Fix spacing if necessary (Source has "LN7 1112AR", Image has "LN7-1112AR")
        # The source data has space, image has hyphen. Let's convert space to hyphen for LN groups
        if "LN" in group_name and " " in group_name:
            group_name = group_name.replace(" ", "-")
    
    if group_name not in group_order:
        group_order.append(group_name)
        group_map[group_name] = []
    
    group_map[group_name].append(float(v))

# Extract P-values from the table
# Look for rows starting with "B16-F0 vs." in column 3 (index 3)
p_values = {}

# Iterate through rows to find statistical comparisons
for idx, row in df_raw.iterrows():
    comp = row[4] # Column 'Unnamed: 3' -> Index 4 due to empty first col
    if isinstance(comp, str) and "B16-F0 vs." in comp:
        target_group = comp.split("vs.")[1].strip()
        # Convert target group format to match our keys (Space to Hyphen)
        if " " in target_group:
            target_group = target_group.replace(" ", "-")
        
        p_val_raw = row[9] # Column 'Unnamed: 8' -> Index 9
        try:
            p_values[target_group] = float(p_val_raw)
        except:
            pass

# Global P-value (ANOVA)
# Found in row with "P value" in column 1
global_p_row = df_raw[df_raw[1] == 'P value'].index[0]
global_p = float(df_raw.iloc[global_p_row, 2]) # Column 2

scr_data = []
for group in group_order:
    for val in group_map[group]:
        scr_data.append({
            "Group": group,
            "Value": val
        })

der_data = []
der_data.append({
    "Metric": "Global ANOVA P-value",
    "Value": global_p
})

for target_group, p_val in p_values.items():
    der_data.append({
        "Metric": "Adjusted P Value",
        "Comparison": f"B16-F0 vs. {target_group}",
        "Value": p_val
    })

output_data = {
    "scr_data": scr_data,
    "der_data": der_data
}

import os
os.makedirs("bench/ground_truth_code/nature_1_output", exist_ok=True)

with open("bench/ground_truth_code/nature_1_output/96.json", "w") as f:
    json.dump(output_data, f, indent=4)
