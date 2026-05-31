#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,NOPAT,Avg Invested Capital,WACC,Capital Charge
2016,3141099845.880261,19307100000.0,0.1,1930710000.0
2017,0.0,19216950000.0,0.1,1921695000.0
2018,5158796087.062851,16976500000.0,0.1,1697650000.0
2019,5283924354.811144,15418250000.0,0.1,1541825000.0
2020,6177337440.351872,17083200000.0,0.1,1708320000.0
2021,7193505986.516124,20312600000.0,0.1,2031260000.0
2022,7939311212.976023,23433400000.0,0.1,2343340000.0
2023,8624441906.44738,29000000000.0,0.1,2900000000.0
2024,14616494984.38535,38873250000.0,0.1,3887325000.0
"""

INDICATOR_NAME = "经济增加值 (Economic Value Added, EVA) - 简化版"

def load_data(csv_text):
    df = pd.read_csv(io.StringIO(csv_text))
    return df

def to_native_types(record):
    # Convert pandas/numpy scalars to native python types for JSON serialization
    out = {}
    for k, v in record.items():
        if pd.isna(v):
            out[k] = None
            continue
        try:
            # try to cast to float first
            fv = float(v)
            # if it is an integer value, store as int
            if fv.is_integer():
                out[k] = int(fv)
            else:
                out[k] = fv
        except Exception:
            # fallback to string
            out[k] = v
    return out

def calculate_eva(df):
    der_rows = []
    for _, row in df.iterrows():
        # Use the simplified EVA formula:
        # EVA = NOPAT - (Avg Invested Capital * WACC)
        nopat = float(row["NOPAT"])
        invested_capital = float(row["Avg Invested Capital"])
        wacc = float(row["WACC"])
        eva = nopat - (invested_capital * wacc)

        # Prepare output record, include Fiscal Year if present
        rec = {}
        if "Fiscal Year" in row.index:
            # ensure native type
            fy = row["Fiscal Year"]
            try:
                fy = int(float(fy))
            except Exception:
                fy = str(fy)
            rec["Fiscal Year"] = fy
        rec[INDICATOR_NAME] = eva
        der_rows.append(rec)
    return der_rows

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = load_data(CSV_DATA)

    # Prepare scr_data as list of native-typed dicts
    scr_data = []
    for _, row in df.iterrows():
        scr_data.append(to_native_types(row.to_dict()))

    der_data = calculate_eva(df)

    # Ensure numbers in der_data are native types (not numpy)
    for d in der_data:
        for k, v in list(d.items()):
            if v is None:
                continue
            try:
                fv = float(v)
                if fv.is_integer():
                    d[k] = int(fv)
                else:
                    d[k] = fv
            except Exception:
                d[k] = v

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()