#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Operating Income,Income Tax,Pretax Income,Effective Tax Rate,NOPAT,Avg Invested Capital
2016,9340000000,1931000000,7884000000,0.2449264332825976,7052387113.140538,31797500000.0
2017,9545000000,2418000000,7727000000,0.31292869160088,6558095638.6696005,34770000000.0
2018,6383000000,490000000,5197000000,0.0942851645179911,5781177794.881662,28868500000.0
2019,12983000000,544000000,8426000000,0.0645620697840019,12144790647.994305,21603500000.0
2020,11363000000,1224000000,3398000000,0.3602118893466745,7269912301.353737,54745000000.0
2021,17924000000,1440000000,12989000000,0.1108630379551928,15936890907.691124,86691000000.0
2022,18117000000,1632000000,13477000000,0.1210951992283149,15923118275.580618,77007000000.0
2023,12757000000,1377000000,6250000000,0.22032,9946377760.0,64210500000.0
2024,9137000000,570000000,3716000000,0.1533907427341227,7735468783.638321,60938000000.0
"""

INDICATOR_NAME = "投入资本回报率 (Return on Invested Capital, ROIC)"

def to_py_value(v):
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    # For plain python numeric types
    if isinstance(v, (int, float, bool, str)):
        return v
    # Fallback: try to convert to float or str
    try:
        return float(v)
    except Exception:
        return str(v)

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(2)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Calculate NOPAT dynamically using the provided Operating Income and Effective Tax Rate:
    # NOPAT = Operating Income * (1 - Effective Tax Rate)
    # Use Avg Invested Capital as the Invested Capital denominator.
    # ROIC = NOPAT / Avg Invested Capital
    # Handle division by zero by returning None for that year.
    operating_income = df["Operating Income"].astype(float)
    effective_tax_rate = df["Effective Tax Rate"].astype(float)
    invested_capital = df["Avg Invested Capital"].astype(float)

    nopat_calc = operating_income * (1.0 - effective_tax_rate)

    roic_values = []
    for idx in df.index:
        ic = invested_capital.iloc[idx]
        np_calc = nopat_calc.iloc[idx]
        if ic == 0 or pd.isna(ic):
            roic = None
        else:
            roic = np_calc / ic
        roic_values.append(roic)

    # Prepare scr_data: original scraped data as list of plain Python dicts
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_py_value(row[col])
        scr_records.append(rec)

    # Prepare der_data: list of dicts with Fiscal Year and calculated ROIC
    der_records = []
    for idx, roic in enumerate(roic_values):
        rec = {}
        # Include Fiscal Year if present in input
        if "Fiscal Year" in df.columns:
            rec["Fiscal Year"] = to_py_value(df.loc[idx, "Fiscal Year"])
        # ROIC value as float (or null)
        rec[INDICATOR_NAME] = to_py_value(roic)
        der_records.append(rec)

    out_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()