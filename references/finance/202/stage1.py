#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import math

CSV_DATA = """Fiscal Year,Operating Income,Income Tax,Pretax Income,Effective Tax Rate,NOPAT,Avg Invested Capital
2016,12604000000,2541000000,11442000000,0.2220765600419507,9804947037.231253,69948500000.0
2017,12913000000,2228000000,11680000000,0.1907534246575342,10449801027.39726,80488500000.0
2018,13264000000,8837000000,12424000000,0.7112846104314231,3829520927.237604,87604000000.0
2019,13535000000,1185000000,12268000000,0.0965927616563417,12227616970.981417,71330500000.0
2020,13896000000,1928000000,12063000000,0.1598275719141175,11675036060.681423,51935000000.0
2021,15213000000,747000000,12999000000,0.0574659589199169,14338770366.951303,52908500000.0
2022,10926000000,932000000,7649000000,0.1218459929402536,9594710681.134789,53820500000.0
2023,13093000000,623000000,9126000000,0.0682664913434144,12199186828.840675,65022500000.0
2024,15353000000,1274000000,11741000000,0.1085086449195128,13687066774.55072,84104000000.0
"""

def to_native(val):
    # Convert pandas/numpy scalar to native Python types, handle NaN as None
    if val is None:
        return None
    try:
        # pandas/numpy scalars have .item()
        return val.item()
    except Exception:
        # Check for NaN
        try:
            if isinstance(val, float) and math.isnan(val):
                return None
        except Exception:
            pass
        return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    output_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: raw input rows as native Python types
    raw_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        raw_records.append(rec)

    # Calculate ROIC for each row using:
    # NOPAT = Operating Income * (1 - Effective Tax Rate)
    # Invested Capital = Avg Invested Capital (provided)
    # ROIC = NOPAT / Invested Capital
    der_records = []
    indicator_name = "投入资本回报率 (Return on Invested Capital, ROIC)"
    for _, row in df.iterrows():
        fiscal_year = to_native(row["Fiscal Year"])
        # Extract raw inputs
        operating_income = to_native(row["Operating Income"])
        effective_tax_rate = to_native(row["Effective Tax Rate"])
        invested_capital = to_native(row["Avg Invested Capital"])

        # Defensive conversions
        try:
            op_inc = float(operating_income) if operating_income is not None else None
        except Exception:
            op_inc = None
        try:
            etr = float(effective_tax_rate) if effective_tax_rate is not None else None
        except Exception:
            etr = None
        try:
            inv_cap = float(invested_capital) if invested_capital is not None else None
        except Exception:
            inv_cap = None

        # Compute NOPAT per reference (use Operating Income and Effective Tax Rate)
        if op_inc is None or etr is None:
            nopat_calc = None
        else:
            nopat_calc = op_inc * (1.0 - etr)

        # Compute ROIC, guarding against zero or missing invested capital
        if nopat_calc is None or inv_cap is None or inv_cap == 0:
            roic = None
        else:
            roic = nopat_calc / inv_cap

        der_rec = {"Fiscal Year": fiscal_year, indicator_name: to_native(roic)}
        der_records.append(der_rec)

    output_obj = {
        "scr_data": raw_records,
        "der_data": der_records
    }

    # Write JSON to specified output file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()