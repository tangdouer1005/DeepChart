#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Current Assets,Cash & Equiv,Current Liabilities,Short Term Debt,CapEx,NOPAT,NCWC,Change in NCWC,Reinvestment
2016,45781000000,19334000000,43816000000,5197000000.0,7804000000,2653356115.107913,-12172000000.0,1662000000.0,9466000000.0
2017,60197000000,20522000000,57883000000,6182000000.0,11955000000,2425193904.3615346,-12026000000.0,146000000.0,12101000000.0
2018,75101000000,31750000000,68391000000,9502000000.0,13427000000,10927523932.155226,-15538000000.0,-3512000000.0,9915000000.0
2019,96334000000,36092000000,87812000000,1307000000.0,16861000000,12071027618.775042,-26263000000.0,-10725000000.0,6136000000.0
2020,132733000000,42122000000,126385000000,16115000000.0,40140000000,20187450781.702374,-19659000000.0,6604000000.0,46744000000.0
2021,161580000000,36220000000,142266000000,15923000000.0,61053000000,21754696862.467564,-983000000.0,18676000000.0,79729000000.0
2022,146791000000,53888000000,155393000000,14854000000.0,63645000000,12248000000.0,-47636000000.0,-46653000000.0,16992000000.0
2023,172351000000,73387000000,164917000000,18945000000.0,52729000000,29865652847.67153,-47008000000.0,628000000.0,53357000000.0
2024,190867000000,78779000000,179431000000,151000000.0,82999000000,59317181615.16792,-67192000000.0,-20184000000.0,62815000000.0
"""

def py_scalar(v):
    """Convert pandas/numpy scalar to native Python type where possible, keep None for NaN."""
    try:
        if pd.isna(v):
            return None
    except Exception:
        pass
    # many numpy scalars have .item()
    try:
        return v.item()
    except Exception:
        return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Calculation: Reinvestment Rate = (CapEx + Change in NCWC) / NOPAT
    # Ensure numeric columns exist
    required_cols = ['CapEx', 'Change in NCWC', 'NOPAT']
    for c in required_cols:
        if c not in df.columns:
            raise KeyError(f"Required column '{c}' not found in input data")

    # Compute, handling division by zero / missing NOPAT
    def compute_row_reinvestment(row):
        nopat = row['NOPAT']
        capex = row['CapEx']
        change_ncwc = row['Change in NCWC']
        # If nopat is missing or zero, return None to avoid division error
        try:
            if pd.isna(nopat):
                return None
            if nopat == 0:
                return None
            value = (capex + change_ncwc) / nopat
            # Convert numpy scalar to python scalar
            return py_scalar(value)
        except Exception:
            return None

    reinvestment_values = df.apply(compute_row_reinvestment, axis=1)

    # Prepare scr_data: original input rows as list of dicts with native python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = py_scalar(row[col])
        scr_records.append(rec)

    # Prepare der_data: list of dicts with Fiscal Year (if present) and calculated indicator
    der_records = []
    for idx, row in df.iterrows():
        rec = {}
        # include Year if present
        if 'Fiscal Year' in df.columns:
            rec['Fiscal Year'] = py_scalar(row['Fiscal Year'])
        rec['资本再投资率 (Reinvestment Rate)'] = py_scalar(reinvestment_values.iloc[idx])
        der_records.append(rec)

    out_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()