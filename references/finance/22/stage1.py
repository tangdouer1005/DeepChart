#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Operating Income,Income Tax,Pretax Income,Effective Tax Rate,NOPAT,Avg Invested Capital
2016,4810445000,1253969000,5603572000,0.2237802958541444,3733962194.70991,2238638500.0
2017,5191402000,981100000,4616032000,0.2125418541292608,4088011793.389648,3762285000.0
2018,5898779000,1593499000,5808093000,0.2743583823468391,4280399535.7384944,5088046500.0
2019,6305074000,1405556000,6251797000,0.2248243185119414,4887540034.78264,6816609500.0
2020,6513644000,1589018000,6774331000,0.234564564382815,4985773932.595264,8853974000.0
2021,7621529000,1770571000,7761116000,0.2281335570812238,5882802478.832297,10787066000.0
2022,9367181000,2207207000,9196167000,0.2400138014022581,7118928279.766994,13574963500.0
2023,8809889000,2135802000,9139332000,0.2336934471797282,6751075670.319231,16232528500.0
2024,9595847000,2280126000,9699323000,0.2350809432782061,7340046235.686655,21260681500.0
"""

INDICATOR_NAME = "投入资本回报率 (Return on Invested Capital, ROIC)"

def to_native(value):
    # Convert pandas/numpy types to native Python types for JSON serialization
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_ ,)):
        return bool(value)
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows as list of dicts with native types
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_data.append(rec)

    # Calculate ROIC for each row:
    der_data = []
    for _, row in df.iterrows():
        # Use Operating Income and Effective Tax Rate to compute NOPAT per reference:
        # NOPAT = Operating Income * (1 - Effective Tax Rate)
        try:
            operating_income = float(row["Operating Income"]) if not pd.isna(row["Operating Income"]) else None
        except Exception:
            operating_income = None
        try:
            eff_tax_rate = float(row["Effective Tax Rate"]) if not pd.isna(row["Effective Tax Rate"]) else None
        except Exception:
            eff_tax_rate = None

        if operating_income is None or eff_tax_rate is None:
            nopat_calc = None
        else:
            nopat_calc = operating_income * (1.0 - eff_tax_rate)

        # Invested Capital: use provided Avg Invested Capital column as the invested capital proxy
        try:
            invested_cap = float(row["Avg Invested Capital"]) if not pd.isna(row["Avg Invested Capital"]) else None
        except Exception:
            invested_cap = None

        if nopat_calc is None or invested_cap is None or invested_cap == 0:
            roic = None
        else:
            roic = nopat_calc / invested_cap

        der_rec = {
            "Fiscal Year": to_native(row["Fiscal Year"]),
            INDICATOR_NAME: to_native(roic)
        }
        der_data.append(der_rec)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()