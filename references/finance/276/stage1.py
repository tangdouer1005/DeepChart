#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Pretax Income,Operating Income,Revenue,Avg Total Assets,Avg Total Equity,Tax Burden,Interest Burden,Operating Margin,Asset Turnover,Equity Multiplier,RESULT_DuPont_ROE
2017,13643000000,20497000000,22764000000,485873000000,199203000000.0,79172000000.0,0.6656096014050836,0.9004129327007556,0.046851749325441,2.439084752739668,2.516078916788764,0.1723210225837417
2018,9862000000,15123000000,20437000000,500343000000,201673500000.0,77833500000.0,0.6521192885009588,0.7399814062729363,0.0408459796579546,2.480955603983667,2.5910886700456746,0.1267063667957884
2019,6670000000,11460000000,21957000000,514405000000,211908500000.0,75182500000.0,0.5820244328097731,0.5219292253040033,0.0426842662882359,2.4274863915321943,2.818588102284441,0.0887174541947926
2020,14881000000,20116000000,20568000000,523964000000,227895000000.0,73582500000.0,0.7397593955060648,0.9780241151302996,0.0392546052782252,2.29914653678229,3.097135867903374,0.2022355859069751
2021,13510000000,20564000000,22548000000,559151000000,244495500000.0,77983500000.0,0.6569733514880374,0.9120099343622494,0.0403254219343254,2.286958246675297,3.1352209121160244,0.1732417755037924
2022,13673000000,18696000000,25942000000,572754000000,248678000000.0,82275500000.0,0.7313329054343175,0.7206846041168761,0.045293441861602,2.303195296729104,3.022503661478812,0.1661855594921939
2023,11680000000,17016000000,20428000000,611289000000,244158500000.0,79973000000.0,0.686412787964269,0.8329743489328373,0.0334179087142088,2.5036564362903606,3.053011641428982,0.1460492916359271
2024,15511000000,21848000000,27012000000,648125000000,247928000000.0,80277000000.0,0.7099505675576712,0.8088257070931438,0.0416771456123433,2.6141662095447065,3.088406392864706,0.1932184810095046
"""

INDICATOR_NAME = "净资产收益率-杜邦分析 (Return on Equity - DuPont Analysis, ROE)"

def to_native(val):
    # convert numpy/pandas types to native Python types for JSON serialization
    if val is None:
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        # convert nan to None
        if np.isnan(val):
            return None
        return float(val)
    if pd.isna(val):
        return None
    return val

def compute_dupont_roe(row):
    # Using formula:
    # ROE = (Net Income / Pretax Income) *
    #       (Pretax Income / EBIT) *
    #       (EBIT / Revenue) *
    #       (Revenue / Total Assets) *
    #       (Total Assets / Equity)
    # We'll treat Operating Income as EBIT, Avg Total Assets as Total Assets, Avg Total Equity as Equity.
    try:
        net_income = float(row["Net Income"])
    except Exception:
        net_income = None
    try:
        pretax = float(row["Pretax Income"])
    except Exception:
        pretax = None
    try:
        ebit = float(row["Operating Income"])
    except Exception:
        ebit = None
    try:
        revenue = float(row["Revenue"])
    except Exception:
        revenue = None
    try:
        assets = float(row["Avg Total Assets"])
    except Exception:
        assets = None
    try:
        equity = float(row["Avg Total Equity"])
    except Exception:
        equity = None

    # If any of the denominators are zero or missing, return None (cannot compute)
    # Compute factors safely
    def safe_div(a, b):
        if a is None or b is None:
            return None
        if b == 0:
            return None
        return a / b

    f1 = safe_div(net_income, pretax)       # Net Income / Pretax Income
    f2 = safe_div(pretax, ebit)             # Pretax Income / EBIT
    f3 = safe_div(ebit, revenue)            # EBIT / Revenue
    f4 = safe_div(revenue, assets)          # Revenue / Total Assets
    f5 = safe_div(assets, equity)           # Total Assets / Equity

    # If any factor is None, final ROE is None
    factors = (f1, f2, f3, f4, f5)
    if any(f is None for f in factors):
        return None

    roe = f1 * f2 * f3 * f4 * f5
    return float(roe)

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: raw input rows as dictionaries with native types
    raw_records = df.to_dict(orient="records")
    scr_data = []
    for rec in raw_records:
        native_rec = {}
        for k, v in rec.items():
            native_rec[k] = to_native(v)
        scr_data.append(native_rec)

    # Compute der_data
    der_data = []
    for rec in raw_records:
        roe = compute_dupont_roe(rec)
        der_rec = {}
        # include Fiscal Year if present
        if "Fiscal Year" in rec:
            der_rec["Fiscal Year"] = to_native(rec["Fiscal Year"])
        der_rec[INDICATOR_NAME] = to_native(roe)
        der_data.append(der_rec)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON with ensure_ascii=False to keep Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()