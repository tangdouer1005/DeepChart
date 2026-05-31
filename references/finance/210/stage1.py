#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Current Assets,Cash & Equiv,Current Liabilities,Short Term Debt,CapEx,NOPAT,NCWC,Change in NCWC,Reinvestment
2016,64313000000,20152000000,17208000000,3750000000,1189000000,9804947037.231253,30703000000,3106000000.0,4295000000.0
2017,74515000000,21784000000,24178000000,9797000000,2021000000,10449801027.39726,38350000000,7647000000.0,9668000000.0
2018,76159000000,21620000000,19195000000,4491000000,1736000000,3829520927.237604,39835000000,1485000000.0,3221000000.0
2019,46386000000,20514000000,18630000000,4494000000,1660000000,12227616970.981417,11736000000,-28099000000.0,-26439000000.0
2020,52140000000,37239000000,17200000000,2371000000,1564000000,11675036060.681423,72000000,-11664000000.0,-10100000000.0
2021,55567000000,30098000000,24164000000,8250000000,2135000000,14338770366.951303,9555000000,9483000000.0,11618000000.0
2022,31633000000,21383000000,19511000000,3749000000,4511000000,9594710681.134789,-5512000000,-15067000000.0,-10556000000.0
2023,21004000000,9765000000,23090000000,4061000000,8695000000,12199186828.840675,-7790000000,-2278000000.0,6417000000.0
2024,22554000000,10454000000,31544000000,11905000000,6866000000,13687066774.55072,-7539000000,251000000.0,7117000000.0
"""

INDICATOR_NAME = "资本再投资率 (Reinvestment Rate)"

def to_python_scalar(v):
    # convert pandas / numpy scalars to native Python types, keep None for NaN
    if pd.isna(v):
        return None
    if isinstance(v, (np.generic,)):
        return v.item()
    # For pandas Timestamp etc.
    if isinstance(v, pd.Timestamp):
        return v.isoformat()
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Compute non-cash working capital (NCWC) per period using the reference formula:
    # NCWC = (Current Assets - Cash) - (Current Liabilities - Short Term Debt)
    df['NCWC_computed'] = (df['Current Assets'] - df['Cash & Equiv']) - (df['Current Liabilities'] - df['Short Term Debt'])

    # Compute change in NCWC as current NCWC minus prior period NCWC
    df['Change_in_NCWC_computed'] = df['NCWC_computed'] - df['NCWC_computed'].shift(1)

    # For the first period, there is no prior period to compare; set change to None (NaN remains)
    # Compute Reinvestment Rate = (CapEx + Change in NCWC) / NOPAT
    def compute_reinvestment_rate(row):
        nopat = row['NOPAT']
        capex = row['CapEx']
        change_ncwc = row['Change_in_NCWC_computed']
        # If NOPAT is zero or missing, reinvestment rate is undefined (set to None)
        if pd.isna(nopat) or nopat == 0 or pd.isna(change_ncwc) or pd.isna(capex):
            return None
        return (capex + change_ncwc) / nopat

    df['ReinvestmentRate_computed'] = df.apply(compute_reinvestment_rate, axis=1)

    # Prepare scr_data: original scraped data as list of dicts (with native Python types)
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in ["Fiscal Year","Current Assets","Cash & Equiv","Current Liabilities","Short Term Debt","CapEx","NOPAT","NCWC","Change in NCWC","Reinvestment"]:
            # Use original CSV columns (not computed ones) to populate scr_data
            val = row.get(col)
            rec[col] = to_python_scalar(val)
        scr_records.append(rec)

    # Prepare der_data: calculated reinvestment rate per year
    der_records = []
    for _, row in df.iterrows():
        year = to_python_scalar(row['Fiscal Year'])
        rr = row['ReinvestmentRate_computed']
        rr_py = to_python_scalar(rr)
        der_records.append({
            "Fiscal Year": year,
            INDICATOR_NAME: rr_py
        })

    out_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON output
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()