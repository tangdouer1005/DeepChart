#!/usr/bin/env python3
import sys
import io
import json
import numbers
import pandas as pd

CSV_DATA = """Fiscal Year,Net Income,Interest Expense,Income Tax,Depreciation & Amortization
2016,4111892000,16258000,1253969000,729052000
2017,3445149000,15545000,981100000,801789000
2018,4059907000,19539000,1593499000,926776000
2019,4779112000,22963000,1405556000,892760000
2020,5107839000,33071000,1589018000,1773124000
2021,5906809000,59492000,1770571000,1891242000
2022,6877169000,47320000,2207207000,1030645000
2023,6871557000,47525000,2135802000,1061616000
2024,7264787000,58969000,2280126000,1077997000
"""

INDICATOR_NAME = "息税折旧摊销前利润 (Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)"

def normalize_value(v):
    # Convert pandas / numpy numeric types to native Python types and handle NaN
    try:
        if pd.isna(v):
            return None
    except Exception:
        pass
    if isinstance(v, numbers.Integral):
        return int(v)
    if isinstance(v, numbers.Real):
        return float(v)
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are numeric
    # Columns expected: Fiscal Year, Net Income, Interest Expense, Income Tax, Depreciation & Amortization
    # Calculate EBITDA dynamically per row:
    # EBITDA = Net Income + Interest Expense + Income Tax + Depreciation + Amortization
    # (Depreciation & Amortization column already combines D&A)
    required_cols = ["Fiscal Year", "Net Income", "Interest Expense", "Income Tax", "Depreciation & Amortization"]
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Expected column '{col}' in CSV data")

    # Convert numeric columns to numeric dtype to be safe
    numeric_cols = ["Net Income", "Interest Expense", "Income Tax", "Depreciation & Amortization"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Compute EBITDA
    df[INDICATOR_NAME] = df["Net Income"] + df["Interest Expense"] + df["Income Tax"] + df["Depreciation & Amortization"]

    # Prepare scr_data: original rows (use original column order)
    scr_records = df[required_cols].to_dict(orient="records")
    # Normalize types for JSON
    scr_records_clean = []
    for rec in scr_records:
        clean = {}
        for k, v in rec.items():
            clean[k] = normalize_value(v)
        scr_records_clean.append(clean)

    # Prepare der_data: one dict per row with Fiscal Year and the calculated indicator
    der_records = []
    for _, row in df.iterrows():
        year = normalize_value(row["Fiscal Year"])
        ebitda_val = normalize_value(row[INDICATOR_NAME])
        der_records.append({
            "Fiscal Year": year,
            INDICATOR_NAME: ebitda_val
        })

    output_obj = {
        "scr_data": scr_records_clean,
        "der_data": der_records
    }

    # Write JSON to the output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()