#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,CFO,Net Income,Total Assets,Avg Total Assets,CFO per Asset,NI per Asset
2016,3292000000,2350000000,33163000000,33090000000.0,0.0994862496222423,0.0710184345723783
2017,6726000000,2679000000,36347000000,34755000000.0,0.1935261113508847,0.077082434182132
2018,5774000000,3134000000,40830000000,38588500000.0,0.1496300711351827,0.0812159062933257
2019,6356000000,3659000000,45400000000,43115000000.0,0.1474196915226719,0.0848660558970196
2020,8861000000,4002000000,55556000000,50478000000.0,0.1755418201988985,0.0792820634731962
2021,8958000000,5007000000,59268000000,57412000000.0,0.1560300982373023,0.0872117327388002
2022,7392000000,5844000000,64166000000,61717000000.0,0.1197725100053469,0.0946902798256558
2023,11068000000,6292000000,68994000000,66580000000.0,0.1662361069390207,0.0945028537098227
2024,11339000000,7367000000,69831000000,69412500000.0,0.163356744102287,0.1061336214658743
"""

INDICATOR_NAME = "盈余-现金质量剪刀差 (Earnings Quality Spread)"

def to_python_value(val):
    # Convert pandas/numpy scalar types to native Python types, preserve None for NaN
    try:
        if pd.isna(val):
            return None
    except Exception:
        pass
    # numpy scalar has .item()
    try:
        if hasattr(val, "item"):
            return val.item()
    except Exception:
        pass
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: list of dicts with original CSV columns, converted to native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_value(row[col])
        scr_records.append(rec)

    # Calculate Earnings Quality Spread for each row:
    # Spread = (CFO / Total Assets) - (Net Income / Total Assets)
    der_records = []
    for _, row in df.iterrows():
        fiscal = to_python_value(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None
        cfo = row.get("CFO", None)
        ni = row.get("Net Income", None)
        total_assets = row.get("Total Assets", None)

        # Convert to float for calculation, handle missing or zero total assets
        try:
            ta_val = float(total_assets) if pd.notna(total_assets) else None
        except Exception:
            ta_val = None
        try:
            cfo_val = float(cfo) if pd.notna(cfo) else None
        except Exception:
            cfo_val = None
        try:
            ni_val = float(ni) if pd.notna(ni) else None
        except Exception:
            ni_val = None

        if ta_val is None or ta_val == 0 or cfo_val is None or ni_val is None:
            spread = None
        else:
            spread = (cfo_val / ta_val) - (ni_val / ta_val)

        rec = {}
        if fiscal is not None:
            rec["Fiscal Year"] = to_python_value(fiscal)
        rec[INDICATOR_NAME] = to_python_value(spread)
        der_records.append(rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON with ensure_ascii=False to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()