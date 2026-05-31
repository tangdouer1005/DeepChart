#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Dividends,Net Income,Avg Total Assets,ROA(Avg),Retention Ratio
2016,2158500000,2737600000,37187400000.0,0.073616332413667,0.2115356516656925
2017,2192100000,-204100000,41893450000.0,-0.0048718833135012,11.74032337089662
2018,2311800000,3232000000,44444700000.0,0.0727195818624042,0.2847153465346534
2019,2409800000,8318400000,41597250000.0,0.1999747579467392,0.7103048663204463
2020,2687100000,6193700000,42959600000.0,0.1441749923183642,0.5661559326412322
2021,3086800000,5581700000,47719550000.0,0.1169688314328194,0.4469785190891664
2022,3535800000,6244800000,49147900000.0,0.1270613800386181,0.4338009223674096
2023,4069300000,5240400000,56748050000.0,0.0923450233091709,0.2234753072284558
2024,4680400000,10590000000,71360600000.0,0.1484012185996194,0.5580358829084042
"""

INDICATOR_NAME = "内部增长率 (Internal Growth Rate, IGR)"

def to_native(obj):
    # Convert numpy and pandas scalar types to native Python types for JSON serialization
    if obj is None:
        return None
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        # convert NaN to None
        if np.isnan(obj):
            return None
        return float(obj)
    if isinstance(obj, (pd.Timestamp,)):
        return str(obj)
    if pd.isna(obj):
        return None
    return obj

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Build scr_data: raw input rows as dictionaries with native Python types
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_data.append(rec)

    # Calculate Internal Growth Rate (IGR) for each row
    der_data = []
    for _, row in df.iterrows():
        fiscal_year = to_native(row.get("Fiscal Year"))
        dividends = row.get("Dividends")
        net_income = row.get("Net Income")
        avg_assets = row.get("Avg Total Assets")

        # Compute retention ratio b = 1 - (Dividends / Net Income)
        b = None
        try:
            if net_income == 0 or pd.isna(net_income):
                b = None
            else:
                b = 1.0 - (float(dividends) / float(net_income))
        except Exception:
            b = None

        # Compute ROA = Net Income / Avg Total Assets
        roa = None
        try:
            if avg_assets == 0 or pd.isna(avg_assets):
                roa = None
            else:
                roa = float(net_income) / float(avg_assets)
        except Exception:
            roa = None

        # Compute IGR = (ROA * b) / (1 - (ROA * b))
        igr = None
        try:
            if b is None or roa is None:
                igr = None
            else:
                numerator = roa * b
                denom = 1.0 - numerator
                if denom == 0:
                    igr = None
                else:
                    igr = numerator / denom
        except Exception:
            igr = None

        der_rec = {"Fiscal Year": fiscal_year, INDICATOR_NAME: to_native(igr)}
        der_data.append(der_rec)

    output = {"scr_data": scr_data, "der_data": der_data}

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()