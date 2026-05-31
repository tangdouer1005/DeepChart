#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Current Assets,Cash & Equiv,Current Liabilities,Short Term Debt,CapEx,NOPAT,NCWC,Change in NCWC,Reinvestment
2016,30614000000,6515000000,17204000000,568000000,1614000000,4651547327.752737,7463000000,2854000000.0,4468000000.0
2017,24766000000,6092000000,18614000000,3057000000,1888000000,2520341358.687318,3117000000,-4346000000.0,-2458000000.0
2018,25875000000,7965000000,22206000000,5308000000,2615000000,6356704171.93426,1012000000,-2105000000.0,510000000.0
2019,27483000000,9676000000,22220000000,3610000000,3473000000,6196228698.92623,-803000000,-1815000000.0,1658000000.0
2020,27764000000,8050000000,27327000000,6722000000,4684000000,4279993859.798738,-891000000,-88000000.0,4596000000.0
2021,30266000000,8096000000,23872000000,2716000000,4448000000,11752521219.108006,1014000000,1905000000.0,6353000000.0
2022,35722000000,12694000000,24239000000,2227000000,4388000000,16149618827.53588,1016000000,2000000.0,4390000000.0
2023,32168000000,6841000000,25694000000,1657000000,3863000000,589548967.7077819,1290000000,274000000.0,4137000000.0
2024,38782000000,13242000000,28420000000,2931000000,3372000000,17377929022.87319,51000000,-1239000000.0,2133000000.0
"""

INDICATOR_NAME = "资本再投资率 (Reinvestment Rate)"

def to_builtin(val):
    """Convert numpy/pandas scalar types to Python built-ins for JSON serialization."""
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    return val

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: list of dicts using original CSV headers and values converted to python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_builtin(row[col])
        scr_records.append(rec)

    # Calculate Reinvestment Rate per row:
    # Reinvestment Rate = (CapEx + Change in NCWC) / NOPAT
    der_records = []
    for _, row in df.iterrows():
        fiscal = to_builtin(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None

        # Extract required fields, convert to python floats/None
        capex = row.get("CapEx", None)
        change_ncwc = row.get("Change in NCWC", None)
        nopat = row.get("NOPAT", None)

        # Convert possible pandas/numpy types to Python numeric or None
        capex_v = None if pd.isna(capex) else float(capex)
        change_ncwc_v = None if pd.isna(change_ncwc) else float(change_ncwc)
        nopat_v = None if pd.isna(nopat) else float(nopat)

        # Compute numerator and denominator
        numerator = None
        if capex_v is not None and change_ncwc_v is not None:
            numerator = capex_v + change_ncwc_v
        elif capex_v is not None:
            numerator = capex_v
        elif change_ncwc_v is not None:
            numerator = change_ncwc_v

        reinvestment_rate = None
        if numerator is not None and nopat_v not in (None, 0):
            reinvestment_rate = numerator / nopat_v
            # keep as float

        rec = {}
        if fiscal is not None:
            rec["Fiscal Year"] = fiscal
        rec[INDICATOR_NAME] = None if reinvestment_rate is None else float(reinvestment_rate)
        der_records.append(rec)

    out_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON with ensure_ascii=False to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()