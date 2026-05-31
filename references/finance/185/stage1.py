#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Pretax Income,Operating Income,Revenue,Avg Total Assets,Avg Total Equity,Tax Burden,Interest Burden,Operating Margin,Asset Turnover,Equity Multiplier,RESULT_DuPont_ROE
2016,186678000,260507000,379793000,8830669000,11894740500.0,2451613000.0,0.7165949475445957,0.6859183818553791,0.0430084062713708,0.742401147801417,4.851801854534138,0.076144970678488
2017,558929000,485321000,838679000,11692713000,16299676000.0,3130878000.0,1.1516686893829031,0.5786731276209373,0.0717266386338226,0.7173586149810586,5.206103846908119,0.1785214882215149
2018,1211242000,1226458000,1605226000,15794341000,22493571000.0,4410360500.0,0.9875935417274786,0.7640407020569067,0.1016329836110287,0.702171344870052,5.1001660748594135,0.2746355995161846
2019,1866916000,2062231000,2604254000,20156447000,29975056000.0,6410461000.0,0.9052894656321236,0.7918701478427219,0.1292020364501739,0.6724406786762968,4.67595949807666,0.2912296011160508
2020,2761395000,3199349000,4585289000,24996056000,36628035500.0,9323698500.0,0.8631115267512235,0.6977420616235966,0.1834404995732126,0.6824296105096873,3.9284877669521374,0.2961694868189914
2021,5116228000,5840103000,6194509000,29697844000,41932511000.0,13457244000.0,0.8760509874568994,0.9427870715822676,0.208584468286654,0.7082295644064817,3.115980582651247,0.3801839366217928
2022,4491924000,5263929000,5632831000,31615550000,46589715500.0,18313324500.0,0.8533405370779127,0.9345085978968656,0.1781664718785534,0.6785950431485249,2.544033744391959,0.2452817346189655
2023,5407990000,6205405000,6954003000,33723297000,48663380000.0,20682857000.0,0.8714967032772236,0.8923500608210839,0.2062076848535895,0.6929912595467064,2.3528364577485594,0.26147209739931
2024,8711631000,9965657000,10417614000,39000966000,51181183000.0,22665940000.0,0.8741652457033189,0.9566160735078107,0.2671116915411787,0.762017673565693,2.2580657585787307,0.3843489835409429
"""

INDICATOR_NAME = "净资产收益率-杜邦分析 (Return on Equity - DuPont Analysis, ROE)"

def to_python_native(value):
    # Convert numpy/pandas scalar types to native Python types for JSON serialization
    if pd.isna(value):
        return None
    if isinstance(value, (np.generic,)):
        return value.item()
    return value

def compute_dupont_roe(row):
    # ROE = (Net Income / Pretax Income) * (Pretax Income / EBIT) * (EBIT / Revenue) * (Revenue / Total Assets) * (Total Assets / Equity)
    # Using columns: Net Income, Pretax Income, Operating Income (EBIT), Revenue, Avg Total Assets, Avg Total Equity
    try:
        net_income = float(row["Net Income"])
        pretax = float(row["Pretax Income"])
        ebit = float(row["Operating Income"])
        revenue = float(row["Revenue"])
        total_assets = float(row["Avg Total Assets"])
        equity = float(row["Avg Total Equity"])
    except Exception:
        return None

    # Safe divisions: if any denominator is zero, return None for that row
    # Compute each factor
    if pretax == 0 or ebit == 0 or revenue == 0 or total_assets == 0 or equity == 0:
        return None

    try:
        tax_burden = net_income / pretax
        interest_burden = pretax / ebit
        operating_margin = ebit / revenue
        asset_turnover = revenue / total_assets
        equity_multiplier = total_assets / equity

        roe = tax_burden * interest_burden * operating_margin * asset_turnover * equity_multiplier
        return float(roe)
    except Exception:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: convert dataframe rows to list of dicts with native Python types
    records = []
    for _, r in df.iterrows():
        rec = {}
        for c in df.columns:
            rec[c] = to_python_native(r[c])
        records.append(rec)

    # Compute derived ROE per row
    der_records = []
    for _, r in df.iterrows():
        fiscal_year = to_python_native(r["Fiscal Year"]) if "Fiscal Year" in df.columns else None
        roe_value = compute_dupont_roe(r)
        # Build dictionary for this row's derived data
        out_rec = {}
        if fiscal_year is not None:
            out_rec["Fiscal Year"] = fiscal_year
        out_rec[INDICATOR_NAME] = to_python_native(roe_value)
        der_records.append(out_rec)

    output = {
        "scr_data": records,
        "der_data": der_records
    }

    # Write JSON output with ensure_ascii=False to keep Chinese characters readable
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()