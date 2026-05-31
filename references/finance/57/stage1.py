#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Working Capital,Total Assets,Retained Earnings,Operating Income,Market Value of Equity,Total Liabilities,Revenue,X1 (WC/TA),X2 (RE/TA),X3 (EBIT/TA),X4 (MVE/TL),X5 (S/TA)
2016,-1269678000,12762920000,-653271000,114923000,5002869000,7760051000,6667216000,-0.0994817800315288,-0.0511850736351869,0.0090044441240719,0.6446953763577069,0.5223895472196017
2017,-1261526000,17584923000,-464910000,218000000,7500127000,10084796000,8391984000,-0.071739068746562,-0.0264379889522405,0.0123969834840903,0.7437063674862635,0.4772260873704138
2018,-839147000,21009802000,-337432000,235768000,9392363000,11617439000,10480012000,-0.0399407381373703,-0.0160606939560877,0.0112218097057744,0.8084710408206146,0.4988153624674806
2019,-572000000,30737000000,1735000000,535000000,15605000000,15132000000,13282000000,-0.0186094934443829,0.0564466278426651,0.0174057325047987,1.031258260639704,0.4321176432312847
2020,1118000000,55126000000,1861000000,202000000,33885000000,21241000000,17098000000,0.0202808112324493,0.0337590247795958,0.0036643326198164,1.5952638764653264,0.3101621739288176
2021,4161000000,66301000000,5933000000,-1715000000,41493000000,24808000000,21252000000,0.0627592344006877,0.0894858297763231,-0.0258668798358999,1.67256530151564,0.3205381517624168
2022,1062000000,95209000000,7377000000,-663000000,58131000000,37078000000,26492000000,0.0111544076715436,0.0774821708031803,-0.006963627388167,1.567803009871083,0.2782510056822359
2023,504000000,98849000000,7585000000,2925000000,58359000000,40490000000,31352000000,0.0050986858744145,0.0767331991218929,0.0295905876640127,1.4413188441590516,0.317170633997309
2024,2443000000,99823000000,11721000000,5011000000,59646000000,40177000000,34857000000,0.0244733177724572,0.1174178295583182,0.0501988519679833,1.4845807302685616,0.3491880628712822
"""

INDICATOR_NAME = "奥特曼破产预测模型 (Altman Z-Score)"

def to_native(value):
    # Convert numpy types and pandas NA to native Python types for JSON serialization
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        # convert numpy floats to Python float
        return float(value)
    return value

def compute_altman_z(row):
    # Use raw columns to compute X1..X5
    # X1 = (Current Assets - Current Liabilities) / Total Assets -> Working Capital / Total Assets
    # X2 = Retained Earnings / Total Assets
    # X3 = EBIT / Total Assets (Operating Income is used as EBIT)
    # X4 = Market Value of Equity / Total Liabilities
    # X5 = Revenue / Total Assets
    ta = row.get("Total Assets", None)
    wc = row.get("Working Capital", None)
    re = row.get("Retained Earnings", None)
    ebit = row.get("Operating Income", None)
    mve = row.get("Market Value of Equity", None)
    tl = row.get("Total Liabilities", None)
    rev = row.get("Revenue", None)

    # Safely handle divisions; if denominator is zero or missing, set component to None
    def safe_div(numer, denom):
        try:
            if pd.isna(numer) or pd.isna(denom):
                return None
            if denom == 0:
                return None
            return float(numer) / float(denom)
        except Exception:
            return None

    X1 = safe_div(wc, ta)
    X2 = safe_div(re, ta)
    X3 = safe_div(ebit, ta)
    X4 = safe_div(mve, tl)
    X5 = safe_div(rev, ta)

    # If any Xi is None, we cannot compute Z reliably; propagate None
    components = [X1, X2, X3, X4, X5]
    if any(c is None for c in components):
        return None

    Z = 1.2 * X1 + 1.4 * X2 + 3.3 * X3 + 0.6 * X4 + 1.0 * X5
    return float(Z)

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA), dtype=object)

    # Convert numeric-like columns to numeric types where possible
    numeric_cols = ["Working Capital", "Total Assets", "Retained Earnings", "Operating Income",
                    "Market Value of Equity", "Total Liabilities", "Revenue"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Prepare scr_data (original scraped data) as list of dicts with native types
    scr_records = []
    for _, r in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(r[col])
        scr_records.append(rec)

    # Prepare der_data with computed Altman Z-Score per row
    der_records = []
    for _, r in df.iterrows():
        row = r.to_dict()
        # compute using raw numeric columns
        z = compute_altman_z(row)
        rec = {}
        # include Year if present
        if "Fiscal Year" in df.columns:
            rec["Year"] = to_native(row.get("Fiscal Year"))
        rec[INDICATOR_NAME] = to_native(z)
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()