#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,NOPAT,Avg Invested Capital,WACC,Capital Charge
2016,20890676001.40411,114477000000.0,0.1,11447700000.0
2017,24742256947.92816,135049500000.0,0.1,13504950000.0
2018,15927677743.049845,148968500000.0,0.1,14896850000.0
2019,38585221571.140816,155082000000.0,0.1,15508200000.0
2020,44216710894.48676,165603500000.0,0.1,16560350000.0
2021,60248983657.28109,176982500000.0,0.1,17698250000.0
2022,72448667566.53447,194151000000.0,0.1,19415100000.0
2023,71722551566.99623,210574000000.0,0.1,21057400000.0
2024,89481912364.19975,260274000000.0,0.1,26027400000.0
"""

INDICATOR_NAME = "经济增加值 (Economic Value Added, EVA) - 简化版"

def convert_value(v):
    # Convert pandas/numpy scalar types to native Python types for JSON serialization
    if pd.isna(v):
        return None
    # Common native types
    if isinstance(v, (int, float, str, bool)):
        return v
    # Pandas/numpy scalars
    try:
        return v.item()
    except Exception:
        try:
            return float(v)
        except Exception:
            return str(v)

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data as list of dicts with native python types
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = convert_value(row[col])
        scr_data.append(rec)

    # Calculate EVA for each row dynamically:
    # EVA = NOPAT - (Invested Capital * WACC)
    der_data = []
    for _, row in df.iterrows():
        nopat = float(row["NOPAT"])
        invested_capital = float(row["Avg Invested Capital"])
        wacc = float(row["WACC"])
        eva = nopat - (invested_capital * wacc)
        der_rec = {
            "Fiscal Year": convert_value(row["Fiscal Year"]),
            INDICATOR_NAME: convert_value(eva)
        }
        der_data.append(der_rec)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()