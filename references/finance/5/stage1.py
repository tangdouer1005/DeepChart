#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Pretax Income,Operating Income,Revenue,Avg Total Assets,Avg Total Equity,Tax Burden,Interest Burden,Operating Margin,Asset Turnover,Equity Multiplier,RESULT_DuPont_ROE
2016,5953000000,7884000000,9340000000,25638000000,59574500000.0,4290500000.0,0.7550735667174023,0.8441113490364026,0.3643029877525548,0.4303519123114755,13.88521151380958,1.3874839762265474
2017,5309000000,7727000000,9545000000,28216000000,68442500000.0,4866500000.0,0.68707130839912,0.8095337873232059,0.338283243549759,0.4122584651349673,14.064009041405528,1.0909277714990242
2018,5687000000,5197000000,6383000000,32753000000,65069000000.0,-1674500000.0,1.0942851645179912,0.8141939526868244,0.1948829114890239,0.5033579738431511,-38.85876381009256,-3.396237682890414
2019,7882000000,8426000000,12983000000,33266000000,74233500000.0,-8309000000.0,0.935437930215998,0.6490025417854117,0.3902783622918295,0.44812651969798,-8.934107594174991,-0.948609941027801
2020,4616000000,3398000000,11363000000,45804000000,119840000000.0,2452000000.0,1.3584461447910536,0.2990407462817918,0.2480787704130643,0.3822096128170894,48.874388254486135,1.882544861337684
2021,11542000000,12989000000,17924000000,56197000000,148547000000.0,14242000000.0,0.8885980444991917,0.7246708324034814,0.31894941011086,0.3783112415599103,10.430206431680944,0.8104198848476338
2022,11836000000,13477000000,18117000000,58054000000,142667000000.0,16331000000.0,0.878236996364176,0.7438869570017111,0.3120715196196644,0.4069196100009112,8.735962280325761,0.7247565978813301
2023,4863000000,6250000000,12757000000,54318000000,136758000000.0,13807000000.0,0.77808,0.4899270988476915,0.2348576899002172,0.3971833457640503,9.904975736945028,0.3522126457593974
2024,4278000000,3716000000,9137000000,56334000000,134936000000.0,6842500000.0,1.151237890204521,0.4066980409324723,0.1621933468242979,0.4174868085610956,19.720277676287907,0.6252100840336134
"""

INDICATOR_NAME = "净资产收益率-杜邦分析 (Return on Equity - DuPont Analysis, ROE)"

def safe_div(a, b):
    try:
        if a is None or b is None:
            return None
        if isinstance(a, (int, float, np.number)) and isinstance(b, (int, float, np.number)):
            if b == 0:
                return None
        return a / b
    except Exception:
        return None

def to_py_scalar(x):
    # Convert numpy types to native Python types for JSON serialization
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        return float(x)
    if pd.isna(x):
        return None
    return x

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: convert DataFrame rows to JSON-serializable dicts
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_py_scalar(row[col])
        scr_records.append(rec)

    der_records = []
    for _, row in df.iterrows():
        # Extract raw inputs (ensure Python native types)
        net_income = to_py_scalar(row["Net Income"])
        pretax_income = to_py_scalar(row["Pretax Income"])
        operating_income = to_py_scalar(row["Operating Income"])  # treated as EBIT
        revenue = to_py_scalar(row["Revenue"])
        avg_total_assets = to_py_scalar(row["Avg Total Assets"])
        avg_total_equity = to_py_scalar(row["Avg Total Equity"])

        # Compute DuPont five components safely
        tax_burden = safe_div(net_income, pretax_income)               # Net Income / Pretax Income
        interest_burden = safe_div(pretax_income, operating_income)   # Pretax Income / EBIT (Operating Income)
        operating_margin = safe_div(operating_income, revenue)        # EBIT / Revenue
        asset_turnover = safe_div(revenue, avg_total_assets)          # Revenue / Total Assets
        equity_multiplier = safe_div(avg_total_assets, avg_total_equity)  # Total Assets / Equity

        # Multiply components to get ROE; if any component is None, result is None
        components = [tax_burden, interest_burden, operating_margin, asset_turnover, equity_multiplier]
        if any(c is None for c in components):
            roe = None
        else:
            roe = 1.0
            for c in components:
                roe *= float(c)

        der_rec = {
            "Fiscal Year": to_py_scalar(row["Fiscal Year"]),
            INDICATOR_NAME: to_py_scalar(roe) if roe is not None else None
        }
        der_records.append(der_rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()