#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Working Capital,Total Assets,Retained Earnings,Operating Income,Market Value of Equity,Total Liabilities,Revenue,X1 (WC/TA),X2 (RE/TA),X3 (EBIT/TA),X4 (MVE/TL),X5 (S/TA)
2016,6406000000.0,66099000000.0,4378000000.0,9340000000,4636000000.0,61463000000.0,25638000000,0.0969152332107898,0.0662339823597936,0.1413031967200714,0.0754274929632461,0.3878727363500204
2017,4582000000.0,70786000000.0,5459000000.0,9545000000,5097000000.0,65689000000.0,28216000000,0.0647303139038793,0.0771197694459356,0.1348430480603509,0.0775928998766916,0.3986098946119289
2018,-294000000.0,59352000000.0,3368000000.0,6383000000,-8446000000.0,67798000000.0,32753000000,-0.0049534977759805,0.0567461922091926,0.1075448173608303,-0.124575946193103,0.5518432403288853
2019,33934000000.0,89115000000.0,4717000000.0,12983000000,-8172000000.0,97287000000.0,33266000000,0.3807888683162206,0.0529316052291982,0.1456881557538012,-0.0839988898825125,0.3732929360938113
2020,-4488000000.0,150565000000.0,1055000000.0,11363000000,13076000000.0,137468000000.0,45804000000,-0.0298077242387008,0.0070069405240261,0.0754690665161226,0.0951203189105828,0.3042141267890944
2021,-7266000000.0,146529000000.0,3127000000.0,17924000000,15408000000.0,131093000000.0,56197000000,-0.0495874536781115,0.0213404855011635,0.1223239085778241,0.1175348798181443,0.3835213507223826
2022,-1075000000.0,138805000000.0,4784000000.0,18117000000,17254000000.0,121518000000.0,58054000000,-0.0077446777853823,0.0344656172328086,0.1305212348258348,0.1419871953126285,0.4182414178163611
2023,-4839000000.0,134711000000.0,-1000000000.0,12757000000,10360000000.0,124314000000.0,54318000000,-0.0359213427262807,-0.0074232987655054,0.0946990223515525,0.0833373554064707,0.4032187423447231
2024,-13167000000.0,135161000000.0,-7900000000.0,9137000000,3325000000.0,131797000000.0,56334000000,-0.0974171543566561,-0.0584488128972114,0.0676008611951672,0.0252281918404819,0.4167918260444951
"""

INDICATOR_NAME = "奥特曼破产预测模型 (Altman Z-Score)"

def normalize_value(v):
    # Convert pandas/numpy scalar types to native python types; convert NaN to None
    if pd.isna(v):
        return None
    # numpy scalars have .item()
    try:
        if hasattr(v, "item"):
            return v.item()
    except Exception:
        pass
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

def compute_altman_z(row):
    # Use raw inputs:
    # X1 = (Current Assets - Current Liabilities) / Total Assets
    # Here Working Capital = Current Assets - Current Liabilities
    wc = row.get("Working Capital")
    ta = row.get("Total Assets")
    re = row.get("Retained Earnings")
    ebit = row.get("Operating Income")  # using Operating Income as EBIT
    mve = row.get("Market Value of Equity")
    tl = row.get("Total Liabilities")
    s = row.get("Revenue")

    # normalize to floats or None
    for k in ["wc","ta","re","ebit","mve","tl","s"]:
        pass

    # Compute Xs with safety
    X1 = safe_div(wc, ta)
    X2 = safe_div(re, ta)
    X3 = safe_div(ebit, ta)
    X4 = safe_div(mve, tl)
    X5 = safe_div(s, ta)

    # Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
    components = []
    # Only include numeric components (None -> treated as 0 would be misleading). If any component is None, result will be None.
    for comp in (X1, X2, X3, X4, X5):
        if comp is None:
            return None
    z = 1.2 * X1 + 1.4 * X2 + 3.3 * X3 + 0.6 * X4 + 1.0 * X5
    return z

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(2)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: raw rows
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = normalize_value(row[col])
        scr_records.append(rec)

    # Prepare der_data: compute Altman Z per row
    der_records = []
    for _, row in df.iterrows():
        # build dict of required raw numeric inputs (convert to native types)
        inputs = {
            "Working Capital": normalize_value(row.get("Working Capital")),
            "Total Assets": normalize_value(row.get("Total Assets")),
            "Retained Earnings": normalize_value(row.get("Retained Earnings")),
            "Operating Income": normalize_value(row.get("Operating Income")),
            "Market Value of Equity": normalize_value(row.get("Market Value of Equity")),
            "Total Liabilities": normalize_value(row.get("Total Liabilities")),
            "Revenue": normalize_value(row.get("Revenue")),
        }
        z = compute_altman_z(inputs)
        entry = {}
        # include Fiscal Year if present
        if "Fiscal Year" in df.columns:
            entry["Fiscal Year"] = normalize_value(row.get("Fiscal Year"))
        entry[INDICATOR_NAME] = z
        der_records.append(entry)

    out_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()