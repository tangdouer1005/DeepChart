#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    csv_data = """Fiscal Year,CFO,Net Income,Total Assets,Avg Total Assets,CFO per Asset,NI per Asset
2016,17203000000,2371000000,83402000000,74074500000.0,0.2322391646248034,0.0320083159521832
2017,18365000000,3033000000,131310000000,107356000000.0,0.1710663586571779,0.0282517977569954
2018,30723000000,10073000000,162648000000,146979000000.0,0.2090298614087727,0.0685336000381006
2019,38514000000,11588000000,225248000000,193948000000.0,0.1985790005568503,0.0597479736836677
2020,66064000000,21331000000,321195000000,273221500000.0,0.2417964911253323,0.0780721868520595
2021,46327000000,33364000000,420549000000,370872000000.0,0.1249137168618822,0.0899609568800017
2022,46752000000,-2722000000,462675000000,441612000000.0,0.1058666884052063,-0.0061637817812921
2023,84946000000,30425000000,527854000000,495264500000.0,0.1715164321286908,0.0614318207745558
2024,115877000000,59248000000,624894000000,576374000000.0,0.2010448077116594,0.1027943661580848
"""

    df = pd.read_csv(io.StringIO(csv_data))

    # Calculation:
    # Spread = (CFO / Total Assets) - (Net Income / Total Assets)
    # Ensure numeric division
    df['EarningsQualitySpread'] = (df['CFO'].astype(float) / df['Total Assets'].astype(float)) - \
                                  (df['Net Income'].astype(float) / df['Total Assets'].astype(float))

    # Helper to convert numpy/pandas types to native Python types for JSON serialization
    def convert_value(v):
        if isinstance(v, (np.integer, np.int64, np.int32)):
            return int(v)
        if isinstance(v, (np.floating, np.float64, np.float32)):
            return float(v)
        if isinstance(v, (np.bool_,)):
            return bool(v)
        if pd.isna(v):
            return None
        return v

    # Prepare scr_data: original CSV rows as list of dicts
    scr_records_raw = df.drop(columns=['EarningsQualitySpread']).to_dict(orient='records')
    scr_data = []
    for row in scr_records_raw:
        converted = {k: convert_value(v) for k, v in row.items()}
        scr_data.append(converted)

    # Prepare der_data: calculated indicator per row. Include Fiscal Year if present.
    der_data = []
    for _, row in df.iterrows():
        year_key = 'Fiscal Year'
        entry = {}
        if year_key in df.columns:
            entry[year_key] = convert_value(row[year_key])
        entry["盈余-现金质量剪刀差 (Earnings Quality Spread)"] = convert_value(row['EarningsQualitySpread'])
        der_data.append(entry)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to output file (ensure Chinese keys are preserved)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()