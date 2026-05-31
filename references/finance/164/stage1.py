#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Pretax Income,Operating Income,Revenue,Avg Total Assets,Avg Total Equity,Tax Burden,Interest Burden,Operating Margin,Asset Turnover,Equity Multiplier,RESULT_DuPont_ROE
2016,3920000000,4659000000,5499000000,39807000000,98527000000.0,42382000000.0,0.841382270873578,0.8472449536279324,0.1381415328962242,0.4040212327585332,2.3247369166155445,0.0924920957010051
2017,2394000000,6521000000,6797000000,40122000000,91624500000.0,37212000000.0,0.3671216071154731,0.9593938502280418,0.1694083046707542,0.4378959776042434,2.462229925830377,0.064334085778781
2018,6220000000,8701000000,8931000000,42294000000,85254500000.0,30518500000.0,0.71486036087806,0.9742470048146904,0.2111647042133635,0.4960911154249922,2.793535068892639,0.2038108032832544
2019,9843000000,7171000000,7926000000,39121000000,83517000000.0,26304000000.0,1.3726119090782318,0.9047438808983094,0.2026021829707829,0.4684196031945591,3.175068430656934,0.3742016423357663
2020,7067000000,5863000000,5548000000,41518000000,87992500000.0,25612000000.0,1.2053556199897664,1.0567772170151406,0.1336287875138494,0.4718356678125976,3.4355965953459315,0.2759253474933624
2021,13049000000,13879000000,13199000000,48704000000,98641000000.0,31750500000.0,0.9401974205634412,1.0515190544738238,0.2710044349540079,0.493750063361077,3.106754224342924,0.4109856537692319
2022,14519000000,16444000000,18282000000,59283000000,107427000000.0,42087500000.0,0.882936025297981,0.8994639536155782,0.3083852031779768,0.5518445083638192,2.5524680724680726,0.3449717849717849
2023,365000000,1889000000,2954000000,60115000000,107917500000.0,41786000000.0,0.193223928004235,0.6394719025050779,0.0491391499625717,0.557045891537517,2.5826233666778347,0.0087349830086631
2024,17117000000,19936000000,20221000000,64168000000,111890500000.0,41947000000.0,0.8585975120385233,0.9859057415558083,0.3151259194614138,0.5734892595886156,2.6674255608267576,0.4080625551290914
"""

INDICATOR_NAME = "净资产收益率-杜邦分析 (Return on Equity - DuPont Analysis, ROE)"

def to_python_value(v):
    # Convert numpy / pandas scalar types to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    return v

def safe_div(numer, denom):
    try:
        if denom is None:
            return None
        # treat zeros and None
        if denom == 0:
            return None
        return numer / denom
    except Exception:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: convert each row to plain Python types
    scr_records_raw = df.to_dict(orient='records')
    scr_records = []
    for r in scr_records_raw:
        conv = {k: to_python_value(v) for k, v in r.items()}
        scr_records.append(conv)

    # Compute DuPont ROE for each row dynamically
    der_records = []
    for idx, row in df.iterrows():
        # Extract raw inputs
        net_income = row.get("Net Income")
        pretax_income = row.get("Pretax Income")
        ebit = row.get("Operating Income")  # treated as EBIT
        revenue = row.get("Revenue")
        total_assets = row.get("Avg Total Assets")
        equity = row.get("Avg Total Equity")

        # Compute five components with safe division
        comp_tax_burden = safe_div(net_income, pretax_income)            # Net Income / Pretax Income
        comp_interest_burden = safe_div(pretax_income, ebit)            # Pretax Income / EBIT
        comp_operating_margin = safe_div(ebit, revenue)                 # EBIT / Revenue
        comp_asset_turnover = safe_div(revenue, total_assets)          # Revenue / Total Assets
        comp_equity_multiplier = safe_div(total_assets, equity)         # Total Assets / Equity

        # If any component is None (due to division by zero), result is None
        components = [comp_tax_burden, comp_interest_burden, comp_operating_margin,
                      comp_asset_turnover, comp_equity_multiplier]

        if any(c is None for c in components):
            roe = None
        else:
            roe = comp_tax_burden * comp_interest_burden * comp_operating_margin * comp_asset_turnover * comp_equity_multiplier

        record = {}
        # include Fiscal Year if present in input
        if "Fiscal Year" in df.columns:
            record["Fiscal Year"] = to_python_value(row["Fiscal Year"])
        record[INDICATOR_NAME] = to_python_value(roe)
        der_records.append(record)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()