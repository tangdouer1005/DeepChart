#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Net Income,Interest Expense,Income Tax,Depreciation & Amortization
2016,5953000000,1047000000,1931000000,1189000000
2017,5309000000,1150000000,2418000000,1501000000
2018,5687000000,1348000000,490000000,1765000000
2019,7882000000,1784000000,544000000,2017000000
2020,4616000000,2454000000,1224000000,6471000000
2021,11542000000,2423000000,1440000000,8521000000
2022,11836000000,2230000000,1632000000,8467000000
2023,4863000000,2224000000,1377000000,8698000000
2024,4278000000,2808000000,570000000,8386000000
"""

INDICATOR_NAME = "息税折旧摊销前利润 (Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)"

def to_native(value):
    # Convert numpy types to native Python types for JSON serialization
    if pd.isna(value):
        return None
    try:
        if isinstance(value, (pd.Timestamp,)):
            return str(value)
        if hasattr(value, 'item'):
            return value.item()
    except Exception:
        pass
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows as dictionaries with native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Calculate EBITDA dynamically for each row
    der_records = []
    for _, row in df.iterrows():
        # Extract components; rely on column names from CSV
        net_income = row["Net Income"]
        interest = row["Interest Expense"]
        income_tax = row["Income Tax"]
        da = row["Depreciation & Amortization"]

        # EBITDA = Net Income + Interest Expense + Income Tax + Depreciation + Amortization
        ebitda = net_income + interest + income_tax + da

        der_rec = {
            "Fiscal Year": to_native(row["Fiscal Year"]),
            INDICATOR_NAME: to_native(ebitda)
        }
        der_records.append(der_rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON with ensure_ascii=False to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()