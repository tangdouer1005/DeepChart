#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Operating Income,Income Tax,Pretax Income,Effective Tax Rate,NOPAT,Avg Invested Capital
2016,2771000000,406000000,7969000000,0.0509474212573723,2629824695.6958213,204880000000.0
2017,13819000000,1174000000,18674000000,0.0628681589375602,12950224911.641855,215362500000.0
2018,22124000000,9532000000,30953000000,0.3079507640616418,15310897295.900234,225382500000.0
2019,12766000000,5282000000,20056000000,0.2633625847626645,9403913242.919825,229528000000.0
2020,-29448000000,5632000000,-28883000000,0.0,-29448000000.0,226278500000.0
2021,24019000000,7636000000,31234000000,0.2444771723122238,18146902798.232697,213232000000.0
2022,64028000000,20176000000,77753000000,0.259488379869587,47413478013.71008,207160000000.0
2023,44461000000,15429000000,52783000000,0.2923100240607771,31464604020.233784,208800000000.0
2024,39652000000,13810000000,48873000000,0.2825691076872711,28447569741.984325,244716500000.0
"""

INDICATOR_NAME = "投入资本回报率 (Return on Invested Capital, ROIC)"

def to_native(v):
    if v is None:
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        # convert nan to None
        if np.isnan(v):
            return None
        return float(v)
    if isinstance(v, (int, float, str, bool)):
        return v
    # fallback for pandas types like Timestamp
    try:
        return v.item()
    except Exception:
        return str(v)

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure columns expected exist
    # We compute NOPAT from Operating Income and Effective Tax Rate per reference:
    # NOPAT = Operating Income * (1 - Effective Tax Rate)
    # Invested Capital: use Avg Invested Capital column from the data as proxy for Invested Capital
    if 'Operating Income' not in df.columns or 'Effective Tax Rate' not in df.columns or 'Avg Invested Capital' not in df.columns:
        raise ValueError("Input CSV missing required columns.")

    # Calculate NOPAT per reference (do not use the provided NOPAT column directly to derive ROIC)
    df['Calculated_NOPAT'] = df['Operating Income'] * (1.0 - df['Effective Tax Rate'])

    # Use Avg Invested Capital as Invested Capital
    df['Invested_Capital'] = df['Avg Invested Capital']

    # Compute ROIC = NOPAT / Invested Capital
    def compute_roic(nopat, invcap):
        try:
            if pd.isna(nopat) or pd.isna(invcap):
                return None
            if invcap == 0:
                return None
            return float(nopat) / float(invcap)
        except Exception:
            return None

    df[INDICATOR_NAME] = df.apply(lambda row: compute_roic(row['Calculated_NOPAT'], row['Invested_Capital']), axis=1)

    # Prepare scr_data: original CSV rows as list of dicts (use original columns)
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in ['Fiscal Year', 'Operating Income', 'Income Tax', 'Pretax Income', 'Effective Tax Rate', 'NOPAT', 'Avg Invested Capital']:
            if col in df.columns:
                rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Prepare der_data: for each row, include Year (Fiscal Year) if present and the calculated ROIC
    der_records = []
    for _, row in df.iterrows():
        rec = {}
        if 'Fiscal Year' in df.columns:
            rec['Fiscal Year'] = to_native(row['Fiscal Year'])
        rec[INDICATOR_NAME] = to_native(row[INDICATOR_NAME])
        der_records.append(rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()