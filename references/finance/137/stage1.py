#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Net Income,Total Assets,Avg Total Assets,CFO per Asset,NI per Asset
2016,4851000000,2737600000,38805900000,37187400000.0,0.1304474096064796,0.073616332413667
2017,5615600000,-204100000,44981000000,41893450000.0,0.1340448208490826,-0.0048718833135012
2018,5524500000,3232000000,43908400000,44444700000.0,0.1243005352719221,0.0727195818624042
2019,4836600000,8318400000,39286100000,41597250000.0,0.1162721093341506,0.1999747579467392
2020,6499600000,6193700000,46633100000,42959600000.0,0.1512956358997756,0.1441749923183642
2021,7260700000,5581700000,48806000000,47719550000.0,0.1521535722780286,0.1169688314328194
2022,7084400000,6244800000,49489800000,49147900000.0,0.1441445107522396,0.1270613800386181
2023,4240100000,5240400000,64006300000,56748050000.0,0.0747179859043614,0.0923450233091709
2024,8817900000,10590000000,78714900000,71360600000.0,0.1235681874872128,0.1484012185996194
"""

INDICATOR_NAME = "盈余-现金质量剪刀差 (Earnings Quality Spread)"

def numpy_to_native(x):
    if pd.isna(x):
        return None
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        return float(x)
    if isinstance(x, (np.ndarray, list, tuple)):
        return [numpy_to_native(v) for v in x]
    return x

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the hardcoded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: mirror input rows with native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = numpy_to_native(row[col])
        scr_records.append(rec)

    # Calculate Earnings Quality Spread for each row:
    # Spread = (CFO / Total Assets) - (Net Income / Total Assets)
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = numpy_to_native(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None
        cfo = row.get("CFO", None)
        ni = row.get("Net Income", None)
        total_assets = row.get("Total Assets", None)

        # Safely convert to floats for calculation, handle missing/zero Total Assets
        try:
            cfo_val = float(cfo) if not pd.isna(cfo) else None
        except Exception:
            cfo_val = None
        try:
            ni_val = float(ni) if not pd.isna(ni) else None
        except Exception:
            ni_val = None
        try:
            ta_val = float(total_assets) if not pd.isna(total_assets) else None
        except Exception:
            ta_val = None

        if ta_val in (0, None):
            spread = None
        else:
            # Calculate spread dynamically; do not hardcode results
            spread = (cfo_val / ta_val) - (ni_val / ta_val)

        rec = {}
        if fiscal_year is not None:
            rec["Fiscal Year"] = fiscal_year
        rec[INDICATOR_NAME] = numpy_to_native(spread)
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file with UTF-8 encoding and preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()