#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Net Income,Total Assets,Avg Total Assets,CFO per Asset,NI per Asset
2016,22082000000,7840000000,330314000000,333536000000.0,0.0662057469058812,0.0235057085292142
2017,30066000000,19710000000,348691000000,339502500000.0,0.0885589944109395,0.0580555371462654
2018,36014000000,20840000000,346196000000,347443500000.0,0.1036542632111408,0.0599809753240454
2019,29716000000,14340000000,362597000000,354396500000.0,0.0838495865506572,0.040463153558232
2020,14668000000,-22440000000,332750000000,347673500000.0,0.042189007790355,-0.0645433143452118
2021,48129000000,23040000000,338923000000,335836500000.0,0.1433108074911452,0.0686048121630615
2022,76797000000,55740000000,369067000000,353995000000.0,0.2169437421432506,0.1574598511278407
2023,55369000000,36010000000,376317000000,372692000000.0,0.1485650349350133,0.0966213387998669
2024,55022000000,33680000000,453475000000,414896000000.0,0.1326163665111256,0.0811769696502256
"""

INDICATOR_NAME = "盈余-现金质量剪刀差 (Earnings Quality Spread)"

def to_python_native(value):
    """
    Convert numpy/pandas scalar types to native Python types for JSON serialization.
    """
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    # For plain Python numeric types or strings, return as-is
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are numeric
    numeric_cols = ["CFO", "Net Income", "Total Assets"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Calculation:
    # Spread = (CFO / Total Assets) - (Net Income / Total Assets)
    # -> handle division safely (avoid division by zero)
    def compute_spread(row):
        ta = row["Total Assets"]
        if ta is None or ta == 0 or pd.isna(ta):
            return None
        cfo = row["CFO"]
        ni = row["Net Income"]
        # Convert to float to ensure floating division
        try:
            return float(cfo) / float(ta) - float(ni) / float(ta)
        except Exception:
            return None

    df[INDICATOR_NAME] = df.apply(compute_spread, axis=1)

    # Prepare scr_data: original input rows (with original headers)
    scr_records = df.drop(columns=[INDICATOR_NAME]).to_dict(orient="records")
    # Convert values to native Python types
    scr_data = []
    for rec in scr_records:
        converted = {}
        for k, v in rec.items():
            converted[k] = to_python_native(v)
        scr_data.append(converted)

    # Prepare der_data: calculated indicator per row. Include Year (Fiscal Year) if present.
    der_data = []
    for _, row in df.iterrows():
        entry = {}
        # If Fiscal Year column exists, include "Year" for clarity
        if "Fiscal Year" in row and not pd.isna(row["Fiscal Year"]):
            entry["Year"] = to_python_native(row["Fiscal Year"])
        # Add the calculated indicator value (ensure native type)
        entry[INDICATOR_NAME] = to_python_native(row[INDICATOR_NAME])
        der_data.append(entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to the specified output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()