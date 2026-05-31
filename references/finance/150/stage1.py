#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Current Assets,Cash & Equiv,Current Liabilities,Short Term Debt,CapEx,NOPAT,NCWC,Change in NCWC,Reinvestment
2016,13228000000,6721000000,7206000000,5180000000.0,382000000,4141675345.377258,4481000000.0,2244000000.0,2626000000.0
2017,13797000000,5933000000,8793000000,5424000000.0,423000000,3975027598.8960447,4495000000.0,14000000.0,437000000.0
2018,16171000000,6682000000,11593000000,500000000.0,504000000,5922437257.0794,-1604000000.0,-6099000000.0,-5595000000.0
2019,16902000000,6988000000,11904000000,1370000000.0,728000000,8062105847.292159,-620000000.0,984000000.0,1712000000.0
2020,19113000000,10113000000,11847000000,649000000.0,708000000,6676197293.814432,-2198000000.0,-1578000000.0,-870000000.0
2021,16949000000,7421000000,13162000000,792000000.0,814000000,8497364315.513729,-2842000000.0,-644000000.0,170000000.0
2022,16606000000,7008000000,14171000000,274000000.0,1097000000,10380286396.181383,-4299000000.0,-1457000000.0,-360000000.0
2023,18961000000,8588000000,16264000000,1337000000.0,371000000,11497878143.55891,-4554000000.0,-255000000.0,116000000.0
2024,19724000000,8442000000,19220000000,750000000.0,474000000,13150823915.038675,-7188000000.0,-2634000000.0,-2160000000.0
"""

INDICATOR_NAME = "资本再投资率 (Reinvestment Rate)"

def to_python_native(val):
    if pd.isna(val):
        return None
    # numpy integer/floats handling
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    # regular python numeric types
    if isinstance(val, (int, float, str, bool)):
        return val
    # timestamps etc.
    try:
        return val.item()
    except Exception:
        return str(val)

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: list of dicts with original CSV columns, converted to native types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_native(row[col])
        scr_records.append(rec)

    # Calculate Reinvestment Rate for each row:
    # Reinvestment Rate = (CapEx + Change in NCWC) / NOPAT
    der_records = []
    for _, row in df.iterrows():
        # extract raw inputs (use columns as provided in CSV)
        capex = row.get("CapEx", np.nan)
        change_ncwc = row.get("Change in NCWC", np.nan)
        nopat = row.get("NOPAT", np.nan)

        # ensure numeric
        try:
            capex_v = float(capex) if not pd.isna(capex) else None
        except Exception:
            capex_v = None
        try:
            change_ncwc_v = float(change_ncwc) if not pd.isna(change_ncwc) else None
        except Exception:
            change_ncwc_v = None
        try:
            nopat_v = float(nopat) if not pd.isna(nopat) else None
        except Exception:
            nopat_v = None

        reinvestment_rate = None
        if nopat_v is not None and nopat_v != 0.0:
            comp_capex = capex_v if capex_v is not None else 0.0
            comp_change = change_ncwc_v if change_ncwc_v is not None else 0.0
            reinvestment_rate = (comp_capex + comp_change) / nopat_v
            # cast to native float
            reinvestment_rate = float(reinvestment_rate)
        else:
            reinvestment_rate = None

        der_rec = {
            "Fiscal Year": to_python_native(row["Fiscal Year"]) if "Fiscal Year" in row else None,
            INDICATOR_NAME: reinvestment_rate
        }
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()