#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

USAGE = "Usage: python this.py output.json"

CSV_DATA = """Fiscal Year,CFO,Net Income,Total Assets,Avg Total Assets,CFO per Asset,NI per Asset
2016,16108000000,10217000000,64961000000.0,57184000000.0,0.2816871852266368,0.1786688584219362
2017,24216000000,15934000000,84524000000.0,74742500000.0,0.3239923738167709,0.2131852694250259
2018,29274000000,22112000000,97334000000.0,90929000000.0,0.3219434943747319,0.2431787438550957
2019,36314000000,18485000000,133376000000.0,115355000000.0,0.3148021325473538,0.160244462745438
2020,38747000000,29146000000,159316000000.0,146346000000.0,0.2647629590149372,0.199158159430391
2021,57683000000,39370000000,165987000000.0,162651500000.0,0.3546416725329923,0.2420512568282493
2022,50475000000,23200000000,185727000000.0,175857000000.0,0.287022978897627,0.1319253711822674
2023,71113000000,39098000000,229623000000.0,207675000000.0,0.3424244612977007,0.1882653184061634
2024,91328000000,62360000000,276054000000.0,252838500000.0,0.3612108124356061,0.2466396533755737
"""

def to_python_scalar(val):
    # Convert numpy/pandas scalars to native Python types for JSON serialization
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, (np.bool_, bool)):
        return bool(val)
    return val

def main():
    if len(sys.argv) != 2:
        print(USAGE, file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows as dictionaries with native types
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_scalar(row[col])
        scr_data.append(rec)

    # Calculate 盈余-现金质量剪刀差 (Earnings Quality Spread)
    indicator_name = "盈余-现金质量剪刀差 (Earnings Quality Spread)"
    der_data = []
    for _, row in df.iterrows():
        fiscal_year = to_python_scalar(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None

        cfo = row.get("CFO", None)
        net_income = row.get("Net Income", None)
        total_assets = row.get("Total Assets", None)

        # Ensure numeric types and handle possible division by zero
        spread = None
        try:
            if pd.isna(cfo) or pd.isna(net_income) or pd.isna(total_assets):
                spread = None
            else:
                # Cast to float to avoid integer division issues and to produce floating result
                cfo_f = float(cfo)
                ni_f = float(net_income)
                ta_f = float(total_assets)
                if ta_f == 0:
                    spread = None
                else:
                    spread = (cfo_f / ta_f) - (ni_f / ta_f)
        except Exception:
            spread = None

        rec = {}
        if fiscal_year is not None:
            rec["Fiscal Year"] = fiscal_year
        rec[indicator_name] = to_python_scalar(spread)
        der_data.append(rec)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON with ensure_ascii=False to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()