import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Interest Expense,Income Tax,Depreciation & Amortization
2016,2737600000,185200000,636400000,1496600000
2017,-204100000,225000000,2391200000,1567300000
2018,3232000000,242500000,529500000,1609000000
2019,8318400000,400600000,628000000,1232600000
2020,6193700000,359600000,1036200000,1323900000
2021,5581700000,339800000,573800000,1547600000
2022,6244800000,331600000,561600000,1522500000
2023,5240400000,485900000,1314200000,1527300000
2024,10590000000,780600000,2090400000,1766600000
"""

INDICATOR_NAME = "息税折旧摊销前利润 (Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)"

def to_json_serializable(value):
    # Convert numpy/pandas scalars to native Python types for JSON serialization
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        # If it's an integer in float form, convert to int to keep numbers clean
        if float(value).is_integer():
            return int(value)
        return float(value)
    if isinstance(value, (np.ndarray,)):
        return value.tolist()
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are numeric
    # (pandas should infer correctly, but enforce)
    numeric_cols = ["Net Income", "Interest Expense", "Income Tax", "Depreciation & Amortization"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Calculate EBITDA dynamically per reference:
    # EBITDA = Net Income + Interest Expense + Income Tax + Depreciation + Amortization
    df["EBITDA_calculated"] = (
        df["Net Income"]
        + df["Interest Expense"]
        + df["Income Tax"]
        + df["Depreciation & Amortization"]
    )

    # Prepare scr_data: original rows as list of dicts with original column names
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            if col == "EBITDA_calculated":
                continue  # do not include derived column in scr_data
            rec[col] = to_json_serializable(row[col])
        scr_records.append(rec)

    # Prepare der_data: for each row, include Fiscal Year and the calculated indicator
    der_records = []
    for _, row in df.iterrows():
        rec = {}
        # Include Fiscal Year if present
        if "Fiscal Year" in df.columns:
            rec["Fiscal Year"] = to_json_serializable(row["Fiscal Year"])
        rec[INDICATOR_NAME] = to_json_serializable(row["EBITDA_calculated"])
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON with ensure_ascii=False to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()