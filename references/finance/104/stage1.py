#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

def to_native(value):
    if pd.isna(value):
        return None
    # numpy integer
    if isinstance(value, (np.integer,)):
        return int(value)
    # numpy floating
    if isinstance(value, (np.floating,)):
        return float(value)
    # native python types
    if isinstance(value, (int, float, bool, str)):
        return value
    # fallback
    return str(value)

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    csv_data = """Fiscal Year,Operating Income,Income Tax,Pretax Income,Effective Tax Rate,NOPAT,Avg Invested Capital
2016,11774000000,4012000000,11021000000,0.3640323019689683,7487883676.617366,26543500000.0
2017,13427000000,4534000000,12491000000,0.3629813465695301,8553249459.61092,26843500000.0
2018,14681000000,5068000000,13698000000,0.3699810191268798,9249308658.198277,25141500000.0
2019,15530000000,3435000000,14556000000,0.2359851607584501,11865150453.42127,25216500000.0
2020,15843000000,3473000000,14715000000,0.2360176690451919,12103772069.317024,26304000000.0
2021,18278000000,4112000000,16978000000,0.2421957827777123,13851145482.388971,30266000000.0
2022,23040000000,5304000000,21737000000,0.244007912775452,17418057689.653587,35173500000.0
2023,24039000000,5372000000,22477000000,0.2389998665302309,18293682208.479782,39910000000.0
2024,21689000000,4781000000,19924000000,0.2399618550491869,16484467325.838186,42694000000.0
"""

    df = pd.read_csv(io.StringIO(csv_data))

    # Calculation for ROIC per reference:
    # 1. NOPAT = Operating Income * (1 - Effective Tax Rate)
    # 2. Invested Capital = Avg Invested Capital (provided in CSV as raw input)
    # 3. ROIC = NOPAT / Invested Capital

    # Compute NOPAT from Operating Income and Effective Tax Rate to follow the reference formula
    nopat_calc = df['Operating Income'] * (1.0 - df['Effective Tax Rate'])
    invested_capital = df['Avg Invested Capital']

    # Avoid division by zero
    roic = []
    for ni, ic in zip(nopat_calc, invested_capital):
        if pd.isna(ni) or pd.isna(ic) or ic == 0:
            roic.append(None)
        else:
            roic.append(float(ni) / float(ic))

    # Prepare scr_data: raw input rows (converted to native Python types)
    scr_records = []
    for _, row in df.iterrows():
        row_dict = {}
        for k, v in row.items():
            row_dict[k] = to_native(v)
        scr_records.append(row_dict)

    # Prepare der_data: calculated ROIC per year
    der_records = []
    for idx, r in enumerate(roic):
        rec = {}
        # include Fiscal Year if present in input
        if 'Fiscal Year' in df.columns:
            fiscal = df.at[idx, 'Fiscal Year']
            rec['Fiscal Year'] = to_native(fiscal)
        rec['投入资本回报率 (Return on Invested Capital, ROIC)'] = to_native(r)
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()