#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Current Assets,Cash & Equiv,Current Liabilities,Short Term Debt,CapEx,NOPAT,NCWC,Change in NCWC,Reinvestment
2016,139660000000,6510000000,59357000000,12904000000,8343000000,20890676001.40411,86697000000,11658000000.0,20001000000.0
2017,159851000000,7663000000,64527000000,10121000000,8129000000,24742256947.92816,97782000000,11085000000.0,19214000000.0
2018,169662000000,11946000000,58488000000,3998000000,11632000000,15927677743.049845,103226000000,5444000000.0,17076000000.0
2019,175552000000,11356000000,69420000000,5516000000,13925000000,38585221571.140816,100292000000,-2934000000.0,10991000000.0
2020,181915000000,13576000000,72310000000,3749000000,15441000000,44216710894.48676,99778000000,-514000000.0,14927000000.0
2021,184406000000,14224000000,88657000000,8072000000,20622000000,60248983657.28109,89597000000,-10181000000.0,10441000000.0
2022,169684000000,13931000000,95082000000,2749000000,23886000000,72448667566.53447,63420000000,-26177000000.0,-2291000000.0
2023,184257000000,34704000000,104149000000,5247000000,28107000000,71722551566.99623,50651000000,-12769000000.0,15338000000.0
2024,159734000000,18315000000,125286000000,8942000000,44477000000,89481912364.19975,25075000000,-25576000000.0,18901000000.0
"""

def to_native(value):
    # Convert numpy and pandas scalar types to native Python types for JSON serialization
    if value is None:
        return None
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA), dtype={
        "Fiscal Year": int
    })

    # Ensure numeric columns are proper numeric types
    numeric_cols = [c for c in df.columns if c != "Fiscal Year"]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    # Calculation for 资本再投资率 (Reinvestment Rate)
    # Reinvestment Rate = (CapEx + Change in NCWC) / NOPAT
    # Use columns 'CapEx', 'Change in NCWC', 'NOPAT' from the CSV
    capex_col = "CapEx"
    change_ncwc_col = "Change in NCWC"
    nopat_col = "NOPAT"
    indicator_name = "资本再投资率 (Reinvestment Rate)"

    der_records = []
    for _, row in df.iterrows():
        capex = row.get(capex_col, np.nan)
        change_ncwc = row.get(change_ncwc_col, np.nan)
        nopat = row.get(nopat_col, np.nan)

        # Handle potential missing data: if NOPAT is zero or NaN, set rate to None
        if pd.isna(nopat) or nopat == 0:
            rate = None
        else:
            # Compute as float
            rate = float((capex if not pd.isna(capex) else 0.0) + (change_ncwc if not pd.isna(change_ncwc) else 0.0)) / float(nopat)

        rec = {
            "Fiscal Year": to_native(row["Fiscal Year"]),
            indicator_name: to_native(rate)
        }
        der_records.append(rec)

    # Prepare scr_data as list of dictionaries matching input CSV columns
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file with UTF-8 and ensure_ascii=False to keep Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()