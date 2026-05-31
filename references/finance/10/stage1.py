#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Current Assets,Cash & Equiv,Current Liabilities,Short Term Debt,CapEx,NOPAT,NCWC,Change in NCWC,Reinvestment
2016,16187000000.0,5100000000.0,9781000000.0,402000000.0,479000000,7052387113.140538,1708000000.0,2256000000.0,2735000000.0
2017,21223000000.0,9303000000.0,16641000000.0,6415000000.0,529000000,6558095638.6696005,1694000000.0,-14000000.0,515000000.0
2018,16945000000.0,7289000000.0,17239000000.0,5308000000.0,638000000,5781177794.881662,-2275000000.0,-3969000000.0,-3331000000.0
2019,49519000000.0,39924000000.0,15585000000.0,3753000000.0,552000000,12144790647.994305,-2237000000.0,38000000.0,590000000.0
2020,24173000000.0,8449000000.0,28661000000.0,8677000000.0,798000000,7269912301.353737,-4260000000.0,-2023000000.0,-1225000000.0
2021,27928000000.0,9746000000.0,35194000000.0,12673000000.0,787000000,15936890907.691124,-4339000000.0,-79000000.0,708000000.0
2022,28463000000.0,9201000000.0,29538000000.0,4302000000.0,695000000,15923118275.580618,-5974000000.0,-1635000000.0,-940000000.0
2023,33002000000.0,12814000000.0,37841000000.0,7191000000.0,777000000,9946377760.0,-10462000000.0,-4488000000.0,-3711000000.0
2024,25582000000.0,5524000000.0,38749000000.0,6804000000.0,974000000,7735468783.638321,-11887000000.0,-1425000000.0,-451000000.0
"""

def to_native(val):
    # Convert numpy / pandas scalar types to native Python types for JSON serialization
    if pd.isnull(val):
        return None
    if isinstance(val, (np.integer, )):
        return int(val)
    if isinstance(val, (np.floating, )):
        return float(val)
    if isinstance(val, (np.bool_, )):
        return bool(val)
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure columns used in calculation exist
    # We'll use the raw 'CapEx', 'Change in NCWC', and 'NOPAT' columns from the CSV as inputs.
    required_cols = ['CapEx', 'Change in NCWC', 'NOPAT']
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Required column missing in input data: {col}")

    # Calculate 资本再投资率 (Reinvestment Rate) for each row:
    # Reinvestment Rate = (CapEx + Change in NCWC) / NOPAT
    # Use the provided Change in NCWC column (raw data).
    reinvestment_rates = []
    for idx, row in df.iterrows():
        capex = row['CapEx']
        change_ncwc = row['Change in NCWC']
        nopat = row['NOPAT']

        # Defensive handling: if NOPAT is zero or null, set result to None to avoid division by zero
        if pd.isnull(nopat) or nopat == 0:
            rr = None
        else:
            # Compute using raw inputs; do not hardcode results.
            rr = (capex + change_ncwc) / nopat

        reinvestment_rates.append(rr)

    # Prepare scr_data: original rows as list of dicts with native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Prepare der_data: calculated values per row. Include Fiscal Year and calculated metric.
    der_records = []
    metric_name = "资本再投资率 (Reinvestment Rate)"
    year_col = 'Fiscal Year' if 'Fiscal Year' in df.columns else None
    for idx, rr in enumerate(reinvestment_rates):
        rec = {}
        if year_col:
            rec[year_col] = to_native(df.iloc[idx][year_col])
        # Convert rr to native numeric if not None
        rec[metric_name] = to_native(rr)
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()