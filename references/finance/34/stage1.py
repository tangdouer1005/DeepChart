#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Net Income,Interest Expense,Income Tax,Depreciation & Amortization
2016,2371000000,484000000,1425000000,8116000000
2017,3033000000,848000000,1558000000,11478000000
2018,10073000000,1417000000,1354000000,15341000000
2019,11588000000,1600000000,2374000000,22824000000
2020,21331000000,1647000000,2863000000,25180000000
2021,33364000000,1809000000,4791000000,34433000000
2022,-2722000000,2367000000,3217000000,41921000000
2023,30425000000,3182000000,7120000000,48663000000
2024,59248000000,2406000000,9265000000,52795000000
"""

INDICATOR_NAME = "息税折旧摊销前利润 (Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)"

def load_data(csv_text: str) -> pd.DataFrame:
    return pd.read_csv(io.StringIO(csv_text))

def to_python_value(v):
    # Convert numpy types to native Python types for JSON serialization
    if pd.isna(v):
        return None
    try:
        if isinstance(v, (pd.Timestamp, )):
            return str(v)
        # numpy integer/float types
        if hasattr(v, "item"):
            return v.item()
    except Exception:
        pass
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = load_data(CSV_DATA)

    # Build scr_data preserving original column names and converting types for JSON
    scr_data = []
    for _, row in df.iterrows():
        entry = {}
        for col in df.columns:
            entry[col] = to_python_value(row[col])
        scr_data.append(entry)

    # Calculate EBITDA for each row:
    # EBITDA = Net Income + Interest Expense + Income Tax + Depreciation & Amortization
    der_data = []
    for _, row in df.iterrows():
        # fetch values
        net_income = row["Net Income"]
        interest = row["Interest Expense"]
        income_tax = row["Income Tax"]
        da = row["Depreciation & Amortization"]

        # perform calculation dynamically
        ebitda = net_income + interest + income_tax + da

        der_entry = {
            "Fiscal Year": to_python_value(row["Fiscal Year"]),
            INDICATOR_NAME: to_python_value(ebitda)
        }
        der_data.append(der_entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()