#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Avg Total Equity,Dividends,ROE(Avg),Retention Ratio
2016,2737600000,14289500000.0,2158500000,0.1915812309737919,0.2115356516656925
2017,-204100000,12799950000.0,2192100000,-0.0159453747866202,11.74032337089662
2018,3232000000,10710450000.0,2311800000,0.3017613639016101,0.2847153465346534
2019,8318400000,6217800000.0,2409800000,1.3378365338222522,0.7103048663204463
2020,6193700000,4124250000.0,2687100000,1.5017760804994849,0.5661559326412322
2021,5581700000,7310400000.0,3086800000,0.7635286714817247,0.4469785190891664
2022,6244800000,9814500000.0,3535800000,0.6362830505884151,0.4338009223674096
2023,5240400000,10710850000.0,4069300000,0.4892608896586172,0.2234753072284558
2024,10590000000,12482000000.0,4680400000,0.8484217272872937,0.5580358829084042
"""

INDICATOR_NAME = "可持续增长率 (Sustainable Growth Rate, SGR)"

def to_py(v):
    # Convert pandas/numpy scalars to native Python types for JSON serialization
    if v is None:
        return None
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        # convert to python float
        return float(v)
    # for Python builtins int/float/str already fine
    return v

def safe_div(numer, denom):
    try:
        if denom is None:
            return None
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

    # Build scr_data preserving original CSV values (converted to native python types)
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_py(row[col])
        scr_data.append(rec)

    # Calculate SGR for each row using:
    # Retention Ratio = 1 - (Dividends / Net Income)
    # ROE = Net Income / Avg Total Equity
    # SGR = ROE * Retention Ratio
    der_data = []
    for _, row in df.iterrows():
        fiscal_year = to_py(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None

        net_income = row.get("Net Income", None)
        dividends = row.get("Dividends", None)
        avg_equity = row.get("Avg Total Equity", None)

        # ensure numpy types handled
        net_income = None if pd.isna(net_income) else float(net_income)
        dividends = None if pd.isna(dividends) else float(dividends)
        avg_equity = None if pd.isna(avg_equity) else float(avg_equity)

        # Retention ratio
        if net_income is None or net_income == 0:
            retention = None
        else:
            retention = 1.0 - (dividends / net_income)

        # ROE
        if avg_equity is None or avg_equity == 0:
            roe = None
        else:
            roe = net_income / avg_equity

        # SGR
        if (retention is None) or (roe is None):
            sgr = None
        else:
            sgr = roe * retention

        # Convert to python native types
        record = {}
        if fiscal_year is not None:
            record["Fiscal Year"] = fiscal_year
        record[INDICATOR_NAME] = to_py(sgr)
        der_data.append(record)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()