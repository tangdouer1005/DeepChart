#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Operating Income,Income Tax,Pretax Income,Effective Tax Rate,NOPAT,Avg Invested Capital
2016,20891000000,3263000000,19803000000,0.1647730141897692,17448726960.56153,77925500000.0
2017,18897000000,16373000000,17673000000,0.9264414643806936,1390035647.5980303,77744500000.0
2018,21175000000,2702000000,17999000000,0.1501194510806155,17996220623.367966,74521000000.0
2019,20970000000,2209000000,17328000000,0.1274815327793167,18296712257.61773,70993500000.0
2020,19733000000,1783000000,16497000000,0.1080802570164272,17600252288.29484,77210500000.0
2021,20943000000,1377000000,19178000000,0.07180102200438,19439271196.16227,88923000000.0
2022,21013000000,2989000000,19359000000,0.1543984709954026,17768624928.973602,98423000000.0
2023,21853000000,1736000000,15062000000,0.1152569379896428,19334290134.11233,89903000000.0
2024,22149000000,2621000000,16687000000,0.1570683765805717,18670092527.11692,80133000000.0
"""

INDICATOR_NAME = "投入资本回报率 (Return on Invested Capital, ROIC)"

def sanitize_value(v):
    # Convert numpy/pandas scalar types to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    # For other types (str, int, float), return as-is
    return v

def sanitize_record(rec):
    return {k: sanitize_value(v) for k, v in rec.items()}

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Calculation for ROIC:
    # Based on reference: NOPAT / Invested Capital
    # Use provided NOPAT and Avg Invested Capital (treated as Invested Capital)
    # Ensure numeric types
    if 'NOPAT' not in df.columns or 'Avg Invested Capital' not in df.columns:
        raise KeyError("Required columns 'NOPAT' and 'Avg Invested Capital' not found in CSV data.")

    # Compute ROIC per row
    # Avoid division by zero
    invested_cap = df['Avg Invested Capital'].astype(float)
    nopat = df['NOPAT'].astype(float)
    with np.errstate(divide='ignore', invalid='ignore'):
        roic_series = nopat / invested_cap

    # Prepare scr_data (original data) and der_data (derived ROIC)
    scr_records = df.to_dict(orient='records')
    scr_records = [sanitize_record(r) for r in scr_records]

    der_records = []
    for i, row in df.iterrows():
        year_val = row.get('Fiscal Year', None)
        roic_val = roic_series.iloc[i]
        # Convert possible nan/inf to None
        if pd.isna(roic_val) or np.isinf(roic_val):
            roic_json = None
        else:
            roic_json = float(roic_val)
        rec = {}
        # Include year if present in source
        if 'Fiscal Year' in df.columns:
            rec['Fiscal Year'] = sanitize_value(year_val)
        rec[INDICATOR_NAME] = roic_json
        der_records.append(rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()