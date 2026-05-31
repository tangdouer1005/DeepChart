#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,CFO,Operating Income,D&A,Denominator (OpInc+D&A)
2016,36036000000,23716000000,6144000000,29860000000
2017,37091000000,26178000000,6915000000,33093000000
2018,47971000000,27524000000,9035000000,36559000000
2019,54520000000,34231000000,11781000000,46012000000
2020,65124000000,41224000000,13697000000,54921000000
2021,91652000000,78714000000,12441000000,91155000000
2022,91495000000,74842000000,13475000000,88317000000
2023,101746000000,84293000000,11946000000,96239000000
2024,125299000000,112390000000,15311000000,127701000000
"""

INDICATOR_NAME = "自由现金流收益质量 (Quality of Income Ratio)"

def normalize_value(v):
    # Convert pandas/numpy types to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, (pd.Timestamp,)):
        return v.isoformat()
    try:
        if hasattr(v, "item"):
            v = v.item()
    except Exception:
        pass
    if isinstance(v, (int, float, str, bool)) or v is None:
        return v
    # Fallback conversions
    try:
        return int(v)
    except Exception:
        try:
            return float(v)
        except Exception:
            return str(v)

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric types
    numeric_cols = ["CFO", "Operating Income", "D&A"]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Compute denominator as Operating Income + D&A per specification
    df["Computed_Denominator"] = df["Operating Income"] + df["D&A"]

    # Calculate the Quality of Income Ratio for each row
    # Ratio = CFO / (Operating Income + D&A)
    def compute_ratio(row):
        denom = row["Computed_Denominator"]
        cfo = row["CFO"]
        if pd.isna(denom) or denom == 0 or pd.isna(cfo):
            return None
        return float(cfo) / float(denom)

    df["Quality_of_Income_Ratio"] = df.apply(compute_ratio, axis=1)

    # Prepare scr_data: original CSV rows (use original headers)
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        # include original CSV columns only
        for col in ["Fiscal Year", "CFO", "Operating Income", "D&A", "Denominator (OpInc+D&A)"]:
            rec[col] = normalize_value(row.get(col))
        scr_records.append(rec)

    # Prepare der_data: calculated indicator per year
    der_records = []
    for _, row in df.iterrows():
        rec = {}
        # include Year if present
        rec["Fiscal Year"] = normalize_value(row.get("Fiscal Year"))
        rec[INDICATOR_NAME] = normalize_value(row.get("Quality_of_Income_Ratio"))
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to specified output path
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()