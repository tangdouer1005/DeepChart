import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Net Income,Interest Expense,Income Tax,Depreciation & Amortization
2017,13643000000,2367000000,6204000000,10080000000
2018,9862000000,2330000000,4600000000,10529000000
2019,6670000000,2346000000,4281000000,10678000000
2020,14881000000,2599000000,4915000000,10987000000
2021,13510000000,2315000000,6858000000,11152000000
2022,13673000000,1994000000,4756000000,10658000000
2023,11680000000,2128000000,5724000000,10945000000
2024,15511000000,2683000000,5578000000,11853000000
"""

INDICATOR_NAME = "息税折旧摊销前利润 (Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)"

def py_cast(x):
    # Convert pandas/numpy scalars and strings to native Python types for JSON serialization
    if pd.isna(x):
        return None
    # If already int or float (Python), return appropriately
    if isinstance(x, int):
        return x
    if isinstance(x, float):
        if x.is_integer():
            return int(x)
        return x
    s = str(x)
    # handle numeric strings
    try:
        if '.' in s:
            v = float(s)
            if v.is_integer():
                return int(v)
            return v
        else:
            return int(s)
    except Exception:
        return s

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data (raw data) ensuring native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = py_cast(row[col])
        scr_records.append(rec)

    # Calculate EBITDA for each row dynamically
    der_records = []
    for _, row in df.iterrows():
        # Extract and convert numeric components
        ni = py_cast(row["Net Income"])
        ie = py_cast(row["Interest Expense"])
        tax = py_cast(row["Income Tax"])
        da = py_cast(row["Depreciation & Amortization"])

        # Ensure values are numbers (int/float) before summing
        def num(x):
            if x is None:
                return 0
            return x

        ebitda = num(ni) + num(ie) + num(tax) + num(da)

        der_rec = {
            "Fiscal Year": py_cast(row["Fiscal Year"]),
            INDICATOR_NAME: py_cast(ebitda)
        }
        der_records.append(der_rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()