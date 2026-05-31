#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Operating Income,D&A,Denominator (OpInc+D&A)
2016,17203000000,4186000000,8116000000,12302000000
2017,18365000000,4106000000,11478000000,15584000000
2018,30723000000,12421000000,15341000000,27762000000
2019,38514000000,14541000000,22824000000,37365000000
2020,66064000000,22899000000,25180000000,48079000000
2021,46327000000,24879000000,34433000000,59312000000
2022,46752000000,12248000000,41921000000,54169000000
2023,84946000000,36852000000,48663000000,85515000000
2024,115877000000,68593000000,52795000000,121388000000
"""

INDICATOR_NAME = "自由现金流收益质量 (Quality of Income Ratio)"

def numpy_to_native(value):
    """Convert numpy/pandas scalar types to native Python types for JSON serialization."""
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        # convert nan/inf to None
        if np.isfinite(value):
            return float(value)
        else:
            return None
    # handle pandas Timestamp if any
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are numeric types
    numeric_cols = ['CFO', 'Operating Income', 'D&A']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Calculate denominator as Operating Income + D&A (per reference)
    df['CalculatedDenominator'] = df['Operating Income'] + df['D&A']

    # Calculate Quality of Income Ratio = CFO / (Operating Income + D&A)
    # If denominator is zero or NaN, result will be None
    def compute_ratio(row):
        denom = row['CalculatedDenominator']
        num = row['CFO']
        if pd.isna(num) or pd.isna(denom) or denom == 0:
            return None
        return float(num) / float(denom)

    df['QualityOfIncomeRatio'] = df.apply(compute_ratio, axis=1)

    # Prepare scr_data: original CSV rows (preserve original column names)
    scr_records = []
    original_cols = df.columns.tolist()
    # We want scr_data to reflect the original CSV columns only.
    # The original CSV columns are the first five columns in CSV_DATA.
    original_csv_cols = ["Fiscal Year", "CFO", "Operating Income", "D&A", "Denominator (OpInc+D&A)"]
    for _, row in df.iterrows():
        rec = {}
        for col in original_csv_cols:
            # Some columns might not exist if parsing changed; guard against that
            if col in df.columns:
                rec[col] = numpy_to_native(row[col])
            else:
                rec[col] = None
        scr_records.append(rec)

    # Prepare der_data: calculated indicator per row. Include Fiscal Year if present.
    der_records = []
    for _, row in df.iterrows():
        rec = {}
        # include year if present
        if 'Fiscal Year' in df.columns:
            rec['Fiscal Year'] = numpy_to_native(row['Fiscal Year'])
        # Include the calculated indicator (do not hardcode results)
        rec[INDICATOR_NAME] = numpy_to_native(row['QualityOfIncomeRatio'])
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON file with UTF-8 and keep Chinese characters
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()