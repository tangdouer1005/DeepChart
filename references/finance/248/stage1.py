#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Working Capital,Total Assets,Retained Earnings,Operating Income,Market Value of Equity,Total Liabilities,Revenue,X1 (WC/TA),X2 (RE/TA),X3 (EBIT/TA),X4 (MVE/TL),X5 (S/TA)
2016,432791000.0,22664076000.0,-2997237000.0,-667340000,4752911000.0,16758951000.0,7000132000.0,0.019095903137635,-0.1322461590757108,-0.0294448359597805,0.2836043258316108,0.3088646543543182
2017,-1104150000.0,28655372000.0,-4974299000.0,-1632000000,4237242000.0,23023050000.0,11759000000.0,-0.0385320420896996,-0.1735904527779294,-0.0569526719108724,0.1840434694794999,0.4103593560048705
2018,-1686000000.0,29740000000.0,-5318000000.0,-388000000,4923000000.0,23427000000.0,21461268000.0,-0.0566913248150638,-0.1788164088769334,-0.0130464021519838,0.2101421436803688,0.721629724277068
2019,1436000000.0,34309000000.0,-6083000000.0,-69000000,6618000000.0,26199000000.0,24578000000.0,0.0418549068757468,-0.1773004168002565,-0.0020111341047538,0.2526050612618802,0.7163717974875398
2020,12469000000.0,52148000000.0,-5399000000.0,1994000000,22225000000.0,28469000000.0,31536000000.0,0.2391079236020556,-0.1035322543529953,0.0382373245378538,0.7806737152692402,0.6047403543760067
2021,7395000000.0,62131000000.0,331000000.0,6687000000,30189000000.0,31116000000.0,53823000000.0,0.1190227100803141,0.0053274532841898,0.1076274323606573,0.970208252988816,0.8662825320693374
2022,14208000000.0,82338000000.0,12885000000.0,13656000000,44704000000.0,36440000000.0,81462000000.0,0.172557021059535,0.1564891058806383,0.1658529476062085,1.2267837541163558,0.9893609269110252
2023,20868000000.0,106618000000.0,27882000000.0,8891000000,62634000000.0,43009000000.0,96773000000.0,0.1957268003526609,0.2615130653360595,0.0833911722223264,1.456299844218652,0.9076609953291188
2024,29539000000.0,122070000000.0,35209000000.0,7076000000,72913000000.0,48390000000.0,97690000000.0,0.2419841074793151,0.288432866388138,0.0579667403948554,1.5067782599710684,0.8002785287130335
"""

INDICATOR_NAME = "奥特曼破产预测模型 (Altman Z-Score)"

def py_value(v):
    # Convert pandas/numpy scalars to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, (np.generic,)):
        return v.item()
    # For plain python numeric types, just return
    return v

def compute_altman_z(row):
    # Based on reference formula:
    # Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
    # X1 = (Current Assets - Current Liabilities) / Total Assets  -> Working Capital / Total Assets
    # X2 = Retained Earnings / Total Assets
    # X3 = EBIT / Total Assets  (use Operating Income)
    # X4 = Market Value of Equity / Total Liabilities
    # X5 = Revenue / Total Assets
    try:
        wc = float(row.get("Working Capital", np.nan))
        ta = float(row.get("Total Assets", np.nan))
        re = float(row.get("Retained Earnings", np.nan))
        ebit = float(row.get("Operating Income", np.nan))
        mve = float(row.get("Market Value of Equity", np.nan))
        tl = float(row.get("Total Liabilities", np.nan))
        rev = float(row.get("Revenue", np.nan))
    except Exception:
        return None

    # Guard against division by zero
    def safe_div(a, b):
        try:
            if b == 0 or pd.isna(b):
                return None
            return a / b
        except Exception:
            return None

    X1 = safe_div(wc, ta)
    X2 = safe_div(re, ta)
    X3 = safe_div(ebit, ta)
    X4 = safe_div(mve, tl)
    X5 = safe_div(rev, ta)

    # If any of the required X's is None (due to division by zero), treat them as 0 in the sum? 
    # We'll follow a conservative approach: if an X is None, return None for Z to indicate can't compute.
    if any(x is None for x in (X1, X2, X3, X4, X5)):
        return None

    Z = 1.2 * X1 + 1.4 * X2 + 3.3 * X3 + 0.6 * X4 + 1.0 * X5
    return Z

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA), dtype=object)

    # Convert numeric-like columns to floats where possible
    for col in df.columns:
        # Try to convert to numeric; if fails, leave as-is
        df[col] = pd.to_numeric(df[col], errors='ignore')

    # Prepare scr_data (original scraped data) ensuring JSON-serializable native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for k, v in row.items():
            rec[k] = py_value(v)
        scr_records.append(rec)

    # Prepare der_data with Altman Z-Score calculated per row
    der_records = []
    for _, row in df.iterrows():
        z = compute_altman_z(row)
        # Use the Fiscal Year column if present for clarity
        der_rec = {}
        if "Fiscal Year" in df.columns:
            der_rec["Fiscal Year"] = py_value(row.get("Fiscal Year"))
        der_rec[INDICATOR_NAME] = py_value(z)
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