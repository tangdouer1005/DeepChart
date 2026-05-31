#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Pretax Income,Operating Income,Revenue,Avg Total Assets,Avg Total Equity,Tax Burden,Interest Burden,Operating Margin,Asset Turnover,Equity Multiplier,RESULT_DuPont_ROE
2016,10217000000,12518000000,12427000000,27638000000,57184000000.0,51706000000.0,0.8161846940405816,1.0073227649472922,0.4496345611115131,0.4833170117515389,1.1059451514331025,0.1975979576838278
2017,15934000000,20594000000,20203000000,40653000000,74742500000.0,66770500000.0,0.7737205011168301,1.0193535613522744,0.4969620938184144,0.5439074154597451,1.1193940437768175,0.2386383208153301
2018,22112000000,25361000000,24913000000,55838000000,90929000000.0,79237000000.0,0.871889909703876,1.0179825793762294,0.4461656936136681,0.6140835157100595,1.147557328015952,0.2790615495286293
2019,18485000000,24812000000,23986000000,70697000000,115355000000.0,92590500000.0,0.7450024181847493,1.034436754773618,0.3392788944368219,0.6128646352563825,1.2458621564847363,0.1996425119207694
2020,29146000000,33180000000,32671000000,85965000000,146346000000.0,114672000000.0,0.8784207353827607,1.015579565975942,0.3800500203571221,0.5874092903120003,1.2762138970280452,0.254168410771592
2021,39370000000,47284000000,46753000000,117929000000,162651500000.0,126584500000.0,0.8326283732340749,1.0113575599426774,0.3964504066005817,0.7250409618109885,1.2849242995785424,0.3110175416421442
2022,23200000000,28819000000,28944000000,116609000000,175857000000.0,125296000000.0,0.8050244630278636,0.9956813156440022,0.248214117263676,0.6630898969048715,1.403532435193462,0.1851615374792491
2023,39098000000,47428000000,46751000000,134902000000,207675000000.0,139440500000.0,0.8243653537994433,1.0144809736690124,0.3465552771641636,0.6495822800048152,1.4893449177247644,0.2803919951520541
2024,62360000000,70663000000,69380000000,164501000000,252838500000.0,167902500000.0,0.8824986202114261,1.018492360910925,0.4217603540404009,0.6506168957654788,1.5058650109438514,0.3714060243295961
"""

INDICATOR_NAME = "净资产收益率-杜邦分析 (Return on Equity - DuPont Analysis, ROE)"

def convert_value(v):
    # Convert numpy and pandas scalar types to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    # bool, str, etc. are fine
    return v

def safe_div(numerator, denominator):
    try:
        if denominator is None:
            return None
        if denominator == 0:
            return None
        return numerator / denominator
    except Exception:
        return None

def compute_dupont_roe(row):
    # Extract raw inputs (these are the only hardcoded/raw data sources)
    net_income = row.get("Net Income")
    pretax_income = row.get("Pretax Income")         # EBT
    operating_income = row.get("Operating Income")   # EBIT (as provided)
    revenue = row.get("Revenue")
    total_assets = row.get("Avg Total Assets")
    total_equity = row.get("Avg Total Equity")

    # Compute DuPont components step by step using definitions:
    # tax burden = Net Income / Pretax Income
    tax_burden = safe_div(net_income, pretax_income)

    # interest burden = Pretax Income / EBIT (Operating Income)
    interest_burden = safe_div(pretax_income, operating_income)

    # operating margin = EBIT / Revenue
    operating_margin = safe_div(operating_income, revenue)

    # asset turnover = Revenue / Total Assets
    asset_turnover = safe_div(revenue, total_assets)

    # equity multiplier = Total Assets / Total Equity
    equity_multiplier = safe_div(total_assets, total_equity)

    # If any component is None (due to division by zero), result will be None
    components = [tax_burden, interest_burden, operating_margin, asset_turnover, equity_multiplier]
    if any(c is None for c in components):
        return None

    roe = 1.0
    for c in components:
        roe *= c

    return roe

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: raw input rows (convert types to native Python)
    scr_records = []
    for _, r in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = convert_value(r[col])
        scr_records.append(rec)

    # Prepare der_data: calculated indicator per row
    der_records = []
    for rec in scr_records:
        # Use the raw numeric fields from rec to compute (ensures only raw data used)
        roe_value = compute_dupont_roe(rec)
        # Keep the Fiscal Year if present
        out_rec = {}
        if "Fiscal Year" in rec:
            out_rec["Fiscal Year"] = rec["Fiscal Year"]
        out_rec[INDICATOR_NAME] = roe_value
        der_records.append(out_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()