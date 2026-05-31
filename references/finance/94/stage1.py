#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Operating Income,Income Tax,Pretax Income,Effective Tax Rate,NOPAT,Avg Invested Capital
2016,23716000000,4672000000,24150000000,0.1934575569358178,19127960579.710144,119804500000.0
2017,26178000000,14531000000,27193000000,0.5343654616997021,12189380943.625198,146538500000.0
2018,27524000000,4177000000,34913000000,0.1196402486179933,24231021797.038357,163708000000.0
2019,34231000000,5282000000,39625000000,0.1332996845425867,29668018498.42271,176523500000.0
2020,41224000000,7813000000,48082000000,0.1624932407137806,34525378644.8151,199903000000.0
2021,78714000000,14701000000,90734000000,0.1620230564066392,65960517138.007805,229700500000.0
2022,74842000000,11356000000,71328000000,0.1592081650964558,62926542507.85105,248647500000.0
2023,84293000000,11922000000,85717000000,0.1390855956228052,72569057888.16687,261795500000.0
2024,112390000000,19697000000,119815000000,0.1643951091265701,93913633685.2648,294690000000.0
"""

def to_native(val):
    # Convert pandas/numpy scalars to native Python types for JSON serialization
    if pd.isna(val):
        return None
    # numpy/pandas scalar have .item()
    try:
        return val.item()
    except Exception:
        return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are numeric
    numeric_cols = ["Operating Income", "Income Tax", "Pretax Income", "Effective Tax Rate", "NOPAT", "Avg Invested Capital"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Calculation for 投入资本回报率 (Return on Invested Capital, ROIC)
    # According to reference:
    # NOPAT is provided in the CSV as 'NOPAT'
    # Invested Capital is provided as 'Avg Invested Capital'
    # ROIC = NOPAT / Invested Capital
    roic_values = []
    for idx, row in df.iterrows():
        invested_cap = row.get("Avg Invested Capital")
        nopat = row.get("NOPAT")

        # Avoid division by zero / invalid
        roic = None
        try:
            if pd.notna(invested_cap) and invested_cap != 0 and pd.notna(nopat):
                roic = float(nopat) / float(invested_cap)
            else:
                roic = None
        except Exception:
            roic = None

        roic_values.append(roic)

    # Build scr_data (original scraped/input data) with native Python types
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_data.append(rec)

    # Build der_data with calculated ROIC values; include Fiscal Year if present
    der_data = []
    for i, roic in enumerate(roic_values):
        rec = {}
        if "Fiscal Year" in df.columns:
            rec["Fiscal Year"] = to_native(df.at[i, "Fiscal Year"])
        rec["投入资本回报率 (Return on Invested Capital, ROIC)"] = to_native(roic)
        der_data.append(rec)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()