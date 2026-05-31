#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Operating Income,Income Tax,Pretax Income,Effective Tax Rate,NOPAT,Avg Invested Capital
2017,22764000000,6204000000,20497000000,0.3026784407474264,15873827974.825584,113462500000.0
2018,20437000000,4600000000,15123000000,0.3041724525557098,14220627587.118958,110843000000.0
2019,21957000000,4281000000,11460000000,0.3735602094240837,13754738481.675394,113472000000.0
2020,20568000000,4915000000,20116000000,0.2443328693577252,15542561543.05031,116641500000.0
2021,22548000000,6858000000,20564000000,0.3334954289048823,15028345069.052711,113603000000.0
2022,25942000000,4756000000,18696000000,0.2543859649122807,19342719298.245613,109305500000.0
2023,20428000000,5724000000,17016000000,0.3363892806770098,13556239774.330042,108812000000.0
2024,27012000000,5578000000,21848000000,0.2553094104723544,20115582204.320763,112422500000.0
"""

INDICATOR_KEY = "投入资本回报率 (Return on Invested Capital, ROIC)"

def pandas_to_native(records):
    """
    Convert a list of dicts (possibly containing numpy types) to native python types so JSON can serialize them.
    """
    def convert_value(v):
        if isinstance(v, (np.integer,)):
            return int(v)
        if isinstance(v, (np.floating,)):
            return float(v)
        if pd.isna(v):
            return None
        return v

    return [{k: convert_value(v) for k, v in rec.items()} for rec in records]

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are numeric
    numeric_cols = ["Operating Income", "Effective Tax Rate", "Avg Invested Capital"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Calculate NOPAT dynamically as Operating Income * (1 - Effective Tax Rate)
    # (Even though the CSV contains a NOPAT column, we derive it per the required calculation logic.)
    df["Calculated NOPAT"] = df["Operating Income"] * (1.0 - df["Effective Tax Rate"])

    # Use Avg Invested Capital as the Invested Capital proxy (raw data provided)
    df["Invested Capital (Proxy)"] = df["Avg Invested Capital"]

    # Calculate ROIC = NOPAT / Invested Capital
    def compute_roic(nopat, invested):
        try:
            if invested is None or invested == 0 or pd.isna(invested):
                return None
            return nopat / invested
        except Exception:
            return None

    roic_values = []
    for _, row in df.iterrows():
        nopat = row.get("Calculated NOPAT")
        invested = row.get("Invested Capital (Proxy)")
        roic = compute_roic(nopat, invested)
        roic_values.append({
            "Fiscal Year": int(row["Fiscal Year"]) if not pd.isna(row["Fiscal Year"]) else None,
            INDICATOR_KEY: float(roic) if roic is not None else None
        })

    # Prepare scr_data as the raw CSV rows (converted to native python types)
    scr_records = pandas_to_native(df.drop(columns=["Calculated NOPAT", "Invested Capital (Proxy)"]).to_dict(orient="records"))

    output = {
        "scr_data": scr_records,
        "der_data": roic_values
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()