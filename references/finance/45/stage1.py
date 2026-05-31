#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Pretax Income,Operating Income,Revenue,Avg Total Assets,Avg Total Equity,Tax Burden,Interest Burden,Operating Margin,Asset Turnover,Equity Multiplier,RESULT_DuPont_ROE
2016,2350000000,3619000000,3672000000,118719000000,33090000000.0,11348000000.0,0.6493506493506493,0.9855664488017428,0.0309301796679554,3.5877606527651857,2.915932322876278,0.2070849488896722
2017,2679000000,4039000000,4111000000,129025000000,34755000000.0,11428500000.0,0.6632829908393166,0.98248601313549,0.0318620422398759,3.712415479787081,3.041081506759417,0.2344139650872818
2018,3134000000,4442000000,4480000000,141576000000,38588500000.0,11788500000.0,0.7055380459252589,0.9915178571428572,0.0316437814318811,3.66886507638286,3.2734020443652714,0.2658523136955508
2019,3659000000,4765000000,4737000000,152703000000,43115000000.0,14021000000.0,0.767890870933893,1.0059109140806417,0.0310210015520323,3.5417604082106,3.075030311675344,0.2609656943156694
2020,4002000000,5367000000,5435000000,166761000000,50478000000.0,16763500000.0,0.7456679709334824,0.9874885004599816,0.0325915531808996,3.30363722809937,3.011185015062487,0.2387329614937215
2021,5007000000,6680000000,6708000000,195929000000,57412000000.0,17924000000.0,0.7495508982035928,0.9958258795468098,0.0342368919353439,3.412683759492789,3.203079669716581,0.2793461280964071
2022,5844000000,7840000000,7793000000,226954000000,61717000000.0,19103000000.0,0.7454081632653061,1.0060310535095598,0.03433735470624,3.677333635789167,3.230749097000471,0.3059205360414594
2023,6292000000,8487000000,8114000000,242290000000,66580000000.0,22850000000.0,0.741369152821963,1.0459699285186097,0.03348879441991,3.63908080504656,2.9137855579868708,0.2753610503282275
2024,7367000000,9740000000,9285000000,254453000000,69412500000.0,24340000000.0,0.7563655030800821,1.0490037695207324,0.0364900394178885,3.665809472357284,2.851787181594084,0.3026705012325389
"""

INDICATOR_NAME = "净资产收益率-杜邦分析 (Return on Equity - DuPont Analysis, ROE)"

def to_python_scalar(val):
    # Convert numpy/scalar types to native Python types for JSON serialization
    if isinstance(val, (np.generic,)):
        return val.item()
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure required raw columns exist
    required_cols = [
        "Fiscal Year",
        "Net Income",
        "Pretax Income",
        "Operating Income",
        "Revenue",
        "Avg Total Assets",
        "Avg Total Equity",
    ]
    for c in required_cols:
        if c not in df.columns:
            raise KeyError(f"Required column missing from input CSV: {c}")

    # Calculate DuPont ROE using raw accounting line items (do NOT use precomputed RESULT_DuPont_ROE)
    # Formula:
    # ROE = (Net Income / Pretax Income) *
    #       (Pretax Income / Operating Income) *
    #       (Operating Income / Revenue) *
    #       (Revenue / Avg Total Assets) *
    #       (Avg Total Assets / Avg Total Equity)
    # We compute each component defensively to avoid division by zero.
    ni = df["Net Income"].astype(float)
    pretax = df["Pretax Income"].astype(float)
    op_income = df["Operating Income"].astype(float)
    revenue = df["Revenue"].astype(float)
    avg_assets = df["Avg Total Assets"].astype(float)
    avg_equity = df["Avg Total Equity"].astype(float)

    # Small epsilon to avoid division by zero where theoretically impossible with given data, but keep logic robust
    eps = 1e-18

    comp1 = ni / (pretax + eps)                # Net Income / Pretax Income (Tax burden)
    comp2 = pretax / (op_income + eps)        # Pretax Income / Operating Income (Interest burden)
    comp3 = op_income / (revenue + eps)       # Operating Income / Revenue (Operating margin)
    comp4 = revenue / (avg_assets + eps)      # Revenue / Avg Total Assets (Asset turnover)
    comp5 = avg_assets / (avg_equity + eps)   # Avg Total Assets / Avg Total Equity (Equity multiplier)

    roe = comp1 * comp2 * comp3 * comp4 * comp5

    # Prepare scr_data: original scraped data as list of dicts
    scr_records = df.where(pd.notnull(df), None).to_dict(orient="records")
    # Convert numpy types to native Python types
    scr_records = [
        {k: to_python_scalar(v) for k, v in rec.items()}
        for rec in scr_records
    ]

    # Prepare der_data: one dict per row with Fiscal Year and calculated ROE
    der_records = []
    for year, val in zip(df["Fiscal Year"].tolist(), roe.tolist()):
        der_records.append({
            "Fiscal Year": to_python_scalar(year),
            INDICATOR_NAME: to_python_scalar(val)
        })

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to specified output path
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()