#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numbers

CSV_DATA = """Fiscal Year,Operating Income,Income Tax,Pretax Income,Effective Tax Rate,NOPAT,Avg Invested Capital
2016,12660000000,2181000000,12920000000,0.1688080495356037,10522890092.879255,81386500000.0
2017,11973000000,2678000000,12287000000,0.2179539350533083,9363437535.60674,86372000000.0
2018,12309000000,12929000000,13039000000,0.9915637702277782,103841552.26627818,73992500000.0
2019,14219000000,2950000000,14571000000,0.2024569350078923,11340264841.122778,53163000000.0
2020,13620000000,2756000000,13970000000,0.1972798854688618,10933047959.9141,43590500000.0
2021,12833000000,2671000000,13262000000,0.2014025033931533,10248401673.955664,42160000000.0
2022,13969000000,2665000000,14477000000,0.1840851005042481,11397515231.056158,43078500000.0
2023,15031000000,2705000000,15318000000,0.1765896331113722,12376681224.702965,42576000000.0
2024,12181000000,1914000000,12234000000,0.1564492398234428,10275291809.710644,55190500000.0
"""

INDICATOR_NAME = "投入资本回报率 (Return on Invested Capital, ROIC)"

def to_json_serializable(val):
    # Handle pandas/numpy scalars and NaN
    try:
        if pd.isnull(val):
            return None
    except Exception:
        pass
    # convert numbers with .item() if available (numpy, pandas scalars)
    if isinstance(val, numbers.Number) and hasattr(val, "item"):
        try:
            return val.item()
        except Exception:
            pass
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure required columns exist
    required_cols = ["Fiscal Year", "Operating Income", "Effective Tax Rate", "Avg Invested Capital"]
    for c in required_cols:
        if c not in df.columns:
            raise ValueError(f"Required column missing: {c}")

    # Calculate NOPAT according to reference: NOPAT = Operating Income * (1 - Effective Tax Rate)
    # Use the calculated NOPAT rather than trusting the provided NOPAT column
    df["Calculated_NOPAT"] = df["Operating Income"] * (1.0 - df["Effective Tax Rate"])

    # Invested Capital: we don't have breakdown (debt, equity, cash) in CSV, but Avg Invested Capital is provided.
    # We'll use Avg Invested Capital as the proxy for Invested Capital per-row.
    df["Invested_Capital_Proxy"] = df["Avg Invested Capital"]

    # ROIC = NOPAT / Invested Capital
    def safe_div(n, d):
        try:
            if pd.isnull(n) or pd.isnull(d):
                return None
        except Exception:
            pass
        try:
            if float(d) == 0.0:
                return None
        except Exception:
            return None
        return float(n) / float(d)

    df["ROIC"] = df.apply(lambda r: safe_div(r["Calculated_NOPAT"], r["Invested_Capital_Proxy"]), axis=1)

    # Prepare scr_data: original CSV rows (use original columns)
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            # Only include original CSV columns in scr_data (not intermediate computed ones)
            if col in ["Calculated_NOPAT", "Invested_Capital_Proxy", "ROIC"]:
                continue
            val = row[col]
            rec[col] = to_json_serializable(val)
        scr_records.append(rec)

    # Prepare der_data: one dict per row containing Fiscal Year and the calculated ROIC
    der_records = []
    for _, row in df.iterrows():
        rec = {}
        # Include year if present
        if "Fiscal Year" in df.columns:
            rec["Fiscal Year"] = to_json_serializable(row["Fiscal Year"])
        rec[INDICATOR_NAME] = to_json_serializable(row["ROIC"])
        der_records.append(rec)

    out_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON output
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()