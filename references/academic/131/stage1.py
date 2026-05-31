import sys
import io
import json
import pandas as pd

# ------------------------------------------------------------
# Embed source data (2012) as CSV text
# ------------------------------------------------------------
csv_data = """UF,Total,Domestic,China,EU,Other_countries,Biome
RO,104544,35817.7,0,57250,11407.5,AMAZÔNIA
AC,0,0,0,0,0,AMAZÔNIA
AM,220,220,0,0,0,AMAZÔNIA
RR,5000,4980.36,0,0,19.6429,AMAZÔNIA
PA,114236,13023.4,21351.7,56283.6,15902,AMAZÔNIA
AP,0,0,0,0,0,AMAZÔNIA
TO,1200,0,159.104,1040.9,0,AMAZÔNIA
MA,230,0,108.028,35.2987,49.0519,AMAZÔNIA
MT,2119394,291382,657731,248767,227804,AMAZÔNIA
RO,41600,0,0,36303.1,5296.85,CERRADO
PA,5450,0,2113.03,1936.16,1307.19,CERRADO
TO,417263,20300,90331.5,194297,77197,CERRADO
MA,555948,41510.9,138095,241907,112746,CERRADO
PI,444856,82862.4,38389,202655,42853.4,CERRADO
BA,1109707,226868,270394,382775,185891,CERRADO
MG,923495,147609,485775,155029,94509,CERRADO
SP,210101,18904.3,109001,22801.2,40341.7,CERRADO
PR,67710,0,67224.5,0,0,CERRADO
MS,1344063,414899,301225,321885,242245,CERRADO
MT,4861296,829534,1767640,1130350,817372,CERRADO
GO,2669474,1067810,907128,374156,257666,CERRADO
DF,55050,42799.7,8434.56,921.681,2874.59,CERRADO
PI,0,0,0,0,0,CAATINGA
CE,1145,0,0,925.012,219.968,CAATINGA
RN,0,0,0,0,0,CAATINGA
PB,0,0,0,0,0,CAATINGA
PE,0,0,0,0,0,CAATINGA
AL,0,0,0,0,0,CAATINGA
SE,0,0,0,0,0,CAATINGA
BA,2920,0,0,1952.15,134.126,CAATINGA
MG,356,0,0,63.8419,56.5327,CAATINGA
RN,0,0,0,0,0,MATA ATLÂNTICA
PB,0,0,0,0,0,MATA ATLÂNTICA
PE,0,0,0,0,0,MATA ATLÂNTICA
AL,0,0,0,0,0,MATA ATLÂNTICA
SE,0,0,0,0,0,MATA ATLÂNTICA
BA,0,0,0,0,0,MATA ATLÂNTICA
MG,104570,55294.7,35852.3,1252.17,3800.04,MATA ATLÂNTICA
ES,0,0,0,0,0,MATA ATLÂNTICA
RJ,0,0,0,0,0,MATA ATLÂNTICA
SP,352547,106095,175838,20391.3,14687.8,MATA ATLÂNTICA
PR,4389095,1514110,1478420,806281,472127,MATA ATLÂNTICA
SC,452349,152374,144839,61724.7,59489.9,MATA ATLÂNTICA
RS,1554512,763246,342919,255955,156319,MATA ATLÂNTICA
MS,470073,151631,209782,42153.7,49993,MATA ATLÂNTICA
GO,420,0,417.675,0,0,MATA ATLÂNTICA
RS,2714735,1034250,659237,539522,364054,PAMPA
MS,0,0,0,0,0,PANTANAL
MT,0,0,0,0,0,PANTANAL
"""

df = pd.read_csv(io.StringIO(csv_data))

# Drop rows with zero Total (no bar to show)
df = df[df["Total"] > 0].copy()

stack_cols = ["Domestic", "China", "EU", "Other_countries"]

# Normalize heights to millions of hectares for easier scaling
scale = 1e6
df["Total_million"] = df["Total"] / scale
for c in stack_cols:
    df[c + "_million"] = df[c] / scale

# Save to JSON
original_cols = ["UF", "Total", "Domestic", "China", "EU", "Other_countries", "Biome"]
scr_data = df[original_cols].to_dict(orient="records")

million_cols = [c for c in df.columns if c.endswith("_million")]
der_data = df[["UF", "Biome"] + million_cols].to_dict(orient="records")

final_data = {
    "scr_data": scr_data,
    "der_data": der_data
}

with open("bench/ground_truth_code/nature_1_output/131.json", 'w') as f:
    json.dump(final_data, f, indent=4)
