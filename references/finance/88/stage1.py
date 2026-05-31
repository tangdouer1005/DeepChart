#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Working Capital,Total Assets,Retained Earnings,Operating Income,Market Value of Equity,Total Liabilities,Revenue,X1 (WC/TA),X2 (RE/TA),X3 (EBIT/TA),X4 (MVE/TL),X5 (S/TA)
2016,15900000000,365200000000,139532000000,14178000000,75800000000,287700000000,119468000000,0.0435377875136911,0.3820700985761227,0.0388225629791894,0.2634688912061175,0.3271303395399781
2017,24936000000,382615000000,117245000000,-2739000000,56030000000,305726000000,99279000000,0.0651725624975497,0.3064307463115664,-0.0071586320452674,0.1832686784898896,0.2594749291062818
2018,6700000000,309100000000,93109000000,6761000000,31000000000,257600000000,97012000000,0.0216758330637334,0.301226140407635,0.0218731802005823,0.1203416149068323,0.313853121967001
2019,35400000000,266000000000,87732000000,5151000000,28300000000,236200000000,90221000000,0.1330827067669173,0.3298195488721804,0.0193646616541353,0.119813717188823,0.3391766917293233
2020,30240000000,256211000000,92247000000,409000000,35552000000,218651000000,75834000000,0.1180277193406996,0.3600430894848386,0.0015963405162151,0.1625970153349401,0.2959826080847426
2021,14395000000,198874000000,85110000000,1058000000,40310000000,157114000000,56469000000,0.0723825135512937,0.4279594114866699,0.0053199513259651,0.256565296536273,0.2839436024819735
2022,8954000000,188851000000,82983000000,1858000000,33696000000,153939000000,76555000000,0.0474130399097701,0.4394099051633298,0.0098384440643682,0.2188918987391109,0.4053724894228783
2023,10453000000,176106000000,86553000000,4717000000,27403000000,147501000000,35348000000,0.0593562967758054,0.4914824026438622,0.0267850044859346,0.1857817913098894,0.2007200208965055
2024,3243000000,125761000000,80488000000,6761000000,19342000000,106196000000,38702000000,0.0257870086910886,0.6400076335270871,0.053760704829001,0.1821349203359825,0.3077424638798992
"""

INDICATOR_NAME = "奥特曼破产预测模型 (Altman Z-Score)"

def to_native_value(v):
    # Convert numpy / pandas scalar types to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    if isinstance(v, (str,)):
        return v
    # For plain python numbers
    try:
        if isinstance(v, int) or isinstance(v, float):
            return v
    except Exception:
        pass
    # Fallback to string
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: list of dicts representing original rows
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native_value(row[col])
        scr_records.append(rec)

    # Calculate Altman Z-Score for each row
    der_records = []
    for _, row in df.iterrows():
        # Use provided raw columns to compute the five X ratios
        # X1 = (Current Assets - Current Liabilities) / Total Assets
        # The CSV provides 'Working Capital' which equals (Current Assets - Current Liabilities)
        total_assets = row["Total Assets"]
        working_capital = row["Working Capital"]
        retained_earnings = row["Retained Earnings"]
        ebit = row["Operating Income"]  # Using Operating Income as EBIT
        market_value_equity = row["Market Value of Equity"]
        total_liabilities = row["Total Liabilities"]
        revenue = row["Revenue"]

        # Guard against division by zero
        def safe_div(numer, denom):
            try:
                if pd.isna(numer) or pd.isna(denom):
                    return float("nan")
                denom = float(denom)
                if denom == 0:
                    return float("nan")
                return float(numer) / denom
            except Exception:
                return float("nan")

        X1 = safe_div(working_capital, total_assets)
        X2 = safe_div(retained_earnings, total_assets)
        X3 = safe_div(ebit, total_assets)
        X4 = safe_div(market_value_equity, total_liabilities)
        X5 = safe_div(revenue, total_assets)

        Z = 1.2 * X1 + 1.4 * X2 + 3.3 * X3 + 0.6 * X4 + 1.0 * X5

        rec = {
            "Fiscal Year": to_native_value(row["Fiscal Year"]),
            INDICATOR_NAME: to_native_value(Z)
        }
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()