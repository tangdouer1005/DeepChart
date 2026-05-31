#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Operating Income,D&A,Denominator (OpInc+D&A)
2016,18767000000,20891000000,3754000000,24645000000
2017,21056000000,18897000000,5642000000,24539000000
2018,22201000000,21175000000,6929000000,28104000000
2019,23416000000,20970000000,7009000000,27979000000
2020,23536000000,19733000000,7231000000,26964000000
2021,23410000000,20943000000,7390000000,28333000000
2022,21194000000,21013000000,6970000000,27983000000
2023,22791000000,21853000000,7486000000,29339000000
2024,24266000000,22149000000,7339000000,29488000000
"""

INDICATOR_NAME = "自由现金流收益质量 (Quality of Income Ratio)"

def to_pyval(v):
    """
    Convert pandas/numpy scalar types to native Python types for JSON serialization.
    """
    if pd.isna(v):
        return None
    # numpy integers
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    # pandas Timestamp etc.
    if isinstance(v, (pd.Timestamp,)):
        return v.isoformat()
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure columns exist
    required_cols = ["Fiscal Year", "CFO", "Operating Income", "D&A"]
    for c in required_cols:
        if c not in df.columns:
            raise KeyError(f"Missing required column: {c}")

    # Calculate denominator as Operating Income + D&A (per specification).
    # Use the explicit sum rather than trusting the provided Denominator column.
    df["Calculated_Denominator"] = df["Operating Income"] + df["D&A"]

    # Compute the Quality of Income Ratio = CFO / (Operating Income + D&A)
    # Handle division by zero by producing None (null in JSON)
    def compute_ratio(row):
        denom = row["Calculated_Denominator"]
        if pd.isna(denom) or denom == 0:
            return None
        # Convert to float for division to get non-integer result
        return float(row["CFO"]) / float(denom)

    df["QualityOfIncomeRatio"] = df.apply(compute_ratio, axis=1)

    # Prepare scr_data: preserve original CSV columns and their raw values
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        # Use original CSV headers as keys
        for col in df.columns:
            if col in ("Calculated_Denominator", "QualityOfIncomeRatio"):
                # Skip internal calculation columns from being included in scr_data
                continue
            # Get original value from row
            rec[col] = to_pyval(row[col])
        scr_records.append(rec)

    # Prepare der_data: one entry per row with Fiscal Year (if present) and calculated indicator
    der_records = []
    for _, row in df.iterrows():
        rec = {}
        # Include Fiscal Year if present
        if "Fiscal Year" in df.columns:
            rec["Fiscal Year"] = to_pyval(row["Fiscal Year"])
        # Indicator value
        rec[INDICATOR_NAME] = to_pyval(row["QualityOfIncomeRatio"])
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output path
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()