#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Pretax Income,Operating Income,Revenue,Avg Total Assets,Avg Total Equity,Tax Burden,Interest Burden,Operating Margin,Asset Turnover,Equity Multiplier,RESULT_DuPont_ROE
2016,10739000000,12920000000,12660000000,49247000000,117512500000.0,61642000000.0,0.8311919504643963,1.0205371248025277,0.2570714967409182,0.4190788214019785,1.9063706563706564,0.1742156321988255
2017,9609000000,12287000000,11973000000,48005000000,125735000000.0,64861500000.0,0.7820460649466916,1.0262256744341436,0.2494115196333715,0.3817950451346085,1.9385151438064183,0.1481464350963206
2018,110000000,13039000000,12309000000,49330000000,119301000000.0,54670500000.0,0.0084362297722217,1.0593061987163863,0.2495236164605716,0.4134919237894066,2.1821823469695723,0.0020120540327964
2019,11621000000,14571000000,14219000000,51904000000,103288500000.0,38387500000.0,0.7975430649921076,1.0247556086925944,0.2739480579531442,0.5025148007764659,2.6906805600781505,0.3027287528492347
2020,11214000000,13970000000,13620000000,49301000000,96323000000.0,35745500000.0,0.8027201145311381,1.025697503671072,0.2762621447840814,0.5118299886839073,2.694688841952134,0.3137178106335063
2021,10591000000,13262000000,12833000000,49818000000,96175000000.0,39597500000.0,0.7985974966068466,1.033429439725707,0.2575976554658958,0.5179932414868729,2.4288149504387904,0.2674663804533114
2022,11812000000,14477000000,13969000000,51557000000,95749500000.0,40524000000.0,0.8159148994957519,1.0363662395303888,0.2709428399635355,0.5384571198805216,2.362785016286645,0.2914815911558583
2023,12613000000,15318000000,15031000000,56998000000,97927000000.0,42063000000.0,0.8234103668886278,1.0190938726631629,0.2637110074037685,0.5820458096337068,2.328103083470033,0.2998597342082116
2024,10320000000,12234000000,12181000000,53803000000,113132500000.0,44905000000.0,0.8435507601765572,1.004351038502586,0.2264000148690593,0.4755750999933706,2.519374234495045,0.229818505734328
"""

INDICATOR_NAME = "净资产收益率-杜邦分析 (Return on Equity - DuPont Analysis, ROE)"

def to_native_value(v):
    # Convert numpy / pandas types to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer, np.int64, np.int32)):
        return int(v)
    if isinstance(v, (np.floating, np.float64, np.float32)):
        return float(v)
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows as list of dicts with native types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native_value(row[col])
        scr_records.append(rec)

    # Calculate DuPont ROE for each row dynamically
    der_records = []
    for _, row in df.iterrows():
        # Extract raw inputs
        net_income = row["Net Income"]
        pretax_income = row["Pretax Income"]
        ebit = row["Operating Income"]  # EBIT interpreted as Operating Income
        revenue = row["Revenue"]
        avg_total_assets = row["Avg Total Assets"]
        avg_total_equity = row["Avg Total Equity"]

        # Compute components with safe checks to avoid ZeroDivisionError
        try:
            tax_burden = net_income / pretax_income if pretax_income != 0 else float("nan")
        except Exception:
            tax_burden = float("nan")
        try:
            interest_burden = pretax_income / ebit if ebit != 0 else float("nan")
        except Exception:
            interest_burden = float("nan")
        try:
            operating_margin = ebit / revenue if revenue != 0 else float("nan")
        except Exception:
            operating_margin = float("nan")
        try:
            asset_turnover = revenue / avg_total_assets if avg_total_assets != 0 else float("nan")
        except Exception:
            asset_turnover = float("nan")
        try:
            equity_multiplier = avg_total_assets / avg_total_equity if avg_total_equity != 0 else float("nan")
        except Exception:
            equity_multiplier = float("nan")

        # ROE is the product of the five components
        roe = tax_burden * interest_burden * operating_margin * asset_turnover * equity_multiplier

        der_rec = {
            "Fiscal Year": to_native_value(row["Fiscal Year"]),
            INDICATOR_NAME: to_native_value(roe)
        }
        der_records.append(der_rec)

    out_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()