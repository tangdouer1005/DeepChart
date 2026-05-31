#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Net Income,Operating Cashflow,Accruals,Avg Total Assets
2016,4111892000,4575115000,-463223000,19405825500.0
2017,3445149000,4973039000,-1527890000,21649447000.0
2018,4059907000,6026688000,-1966781000,23569486500.0
2019,4779112000,6626953000,-1847841000,27119481500.0
2020,5107839000,8215152000,-3107313000,33434236500.0
2021,5906809000,8975148000,-3068339000,40127218000.0
2022,6877169000,9541129000,-2663960000,45219616500.0
2023,6871557000,9524268000,-2652711000,49254347500.0
2024,7264787000,9131027000,-1866240000,53588834000.0
"""

INDICATOR_NAME = "斯隆比率 (Sloan Ratio / Accruals Ratio)"

def load_data(csv_text):
    df = pd.read_csv(io.StringIO(csv_text))
    return df

def to_python_native(value):
    # Convert numpy types to native Python types for JSON serialization
    if pd.isna(value):
        return None
    if isinstance(value, (pd.Timestamp,)):
        return str(value)
    try:
        if float(value).is_integer():
            # but avoid converting large floats that represent ints incorrectly
            return int(value)
    except Exception:
        pass
    try:
        return float(value)
    except Exception:
        return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = load_data(CSV_DATA)

    # Prepare scr_data: mirror input CSV rows with native Python types
    scr_data = []
    for _, row in df.iterrows():
        rec = {
            "Fiscal Year": to_python_native(row["Fiscal Year"]),
            "Net Income": to_python_native(row["Net Income"]),
            "Operating Cashflow": to_python_native(row["Operating Cashflow"]),
            "Accruals": to_python_native(row["Accruals"]),
            "Avg Total Assets": to_python_native(row["Avg Total Assets"]),
        }
        scr_data.append(rec)

    # Calculate Sloan Ratio per reference:
    # Accruals = Net Income - Operating Cashflow
    # Sloan Ratio = Accruals / Avg Total Assets (using average total assets provided)
    der_data = []
    for _, row in df.iterrows():
        net_income = float(row["Net Income"])
        operating_cf = float(row["Operating Cashflow"])
        avg_total_assets = float(row["Avg Total Assets"])

        accruals_calc = net_income - operating_cf
        # Avoid division by zero; if zero, set None
        if avg_total_assets == 0:
            sloan_ratio = None
        else:
            sloan_ratio = accruals_calc / avg_total_assets

        der_rec = {
            "Fiscal Year": to_python_native(row["Fiscal Year"]),
            INDICATOR_NAME: to_python_native(sloan_ratio) if sloan_ratio is not None else None
        }
        der_data.append(der_rec)

    out_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON with ensure_ascii=False to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()