#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Operating Cashflow,Accruals,Avg Total Assets
2016,20539000000,33325000000,-12786000000,184083000000.0
2017,25489000000,39507000000,-14018000000,217390000000.0
2018,16571000000,43884000000,-27313000000,249967000000.0
2019,39240000000,52185000000,-12945000000,272702000000.0
2020,44281000000,60675000000,-16394000000,293933500000.0
2021,61271000000,76740000000,-15469000000,317545000000.0
2022,72738000000,89035000000,-16297000000,349309500000.0
2023,72361000000,87582000000,-15221000000,388408000000.0
2024,88136000000,118548000000,-30412000000,462069500000.0
"""

INDICATOR_NAME = "斯隆比率 (Sloan Ratio / Accruals Ratio)"

def to_native(x):
    if pd.isna(x):
        return None
    # numpy types
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        return float(x)
    # pandas types
    try:
        # try int
        if isinstance(x, (int,)) or (isinstance(x, str) and x.isdigit()):
            return int(x)
        if isinstance(x, float):
            return float(x)
    except Exception:
        pass
    return x

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: convert each row to native python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Calculate Sloan Ratio for each row
    der_records = []
    for _, row in df.iterrows():
        # Use calculation: Accruals = Net Income - Operating Cashflow
        net_income = row["Net Income"]
        cfo = row["Operating Cashflow"]
        avg_total_assets = row["Avg Total Assets"]

        # Ensure numeric types
        try:
            ni = float(net_income)
        except Exception:
            ni = None
        try:
            cfo_v = float(cfo)
        except Exception:
            cfo_v = None
        try:
            ata = float(avg_total_assets)
        except Exception:
            ata = None

        accruals_calc = None
        sloan_ratio = None
        if ni is not None and cfo_v is not None:
            accruals_calc = ni - cfo_v  # Net Income - CFO

        if accruals_calc is not None and ata not in (None, 0.0):
            sloan_ratio = accruals_calc / ata

        rec = {}
        # include Fiscal Year if present
        if "Fiscal Year" in df.columns:
            rec["Fiscal Year"] = to_native(row["Fiscal Year"])
        rec[INDICATOR_NAME] = (None if sloan_ratio is None else float(sloan_ratio))
        der_records.append(rec)

    out_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON with ensure_ascii False to keep Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()