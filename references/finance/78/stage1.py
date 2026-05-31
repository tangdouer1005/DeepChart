#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,CFO,Net Income,Total Assets,Avg Total Assets,CFO per Asset,NI per Asset
2016,12846000000,-497000000,260078000000,262309000000.0,0.0489727763820532,-0.0018947119618465
2017,20338000000,9195000000,253806000000,256942000000.0,0.0791540503304247,0.0357862863992652
2018,30618000000,14824000000,253863000000,253834500000.0,0.120621901278195,0.058400256860277
2019,27300000000,2924000000,237428000000,245645500000.0,0.1111357627149693,0.0119033322409732
2020,10600000000,-5543000000,239790000000,238609000000.0,0.0444241415872829,-0.0232304732847461
2021,29200000000,15625000000,239535000000,239662500000.0,0.1218380013560736,0.0651958483283784
2022,49600000000,35465000000,257709000000,248622000000.0,0.199499642026852,0.1426462662194013
2023,35609000000,21369000000,261632000000,259670500000.0,0.1371314800872644,0.0822927517758081
2024,31492000000,17661000000,256938000000,259285000000.0,0.1214570839038124,0.0681142372293036
"""

INDICATOR_NAME = "盈余-现金质量剪刀差 (Earnings Quality Spread)"

def py_convert_value(v):
    # Convert pandas/numpy scalars to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, str):
        return v
    # Try numeric conversion
    try:
        f = float(v)
    except Exception:
        return v
    # If f is integer-valued, return int
    if f.is_integer():
        # Use int conversion (safe in Python for large ints)
        return int(f)
    return f

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Keep a copy of the original scraped data for scr_data
    df_scr = df.copy()

    # Calculation for Earnings Quality Spread:
    # Spread = (CFO / Total Assets) - (Net Income / Total Assets)
    # Ensure using the raw CFO, Net Income, and Total Assets columns
    df['__spread_calc'] = (df['CFO'] / df['Total Assets']) - (df['Net Income'] / df['Total Assets'])

    # Prepare scr_data: list of dicts mirroring the input CSV columns
    scr_records = []
    for row in df_scr.to_dict(orient='records'):
        rec = {k: py_convert_value(v) for k, v in row.items()}
        scr_records.append(rec)

    # Prepare der_data: list of dicts with Fiscal Year (if present) and calculated indicator
    der_records = []
    for idx, row in df.iterrows():
        rec = {}
        # include year if present in original CSV
        if 'Fiscal Year' in df.columns:
            rec['Fiscal Year'] = py_convert_value(row['Fiscal Year'])
        rec[INDICATOR_NAME] = py_convert_value(row['__spread_calc'])
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()