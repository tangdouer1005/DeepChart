#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Working Capital,Total Assets,Retained Earnings,Operating Income,Market Value of Equity,Total Liabilities,Revenue,X1 (WC/TA),X2 (RE/TA),X3 (EBIT/TA),X4 (MVE/TL),X5 (S/TA)
2016,2155000000,45908000000,13926900000,2858900000,21539300000,24368000000,18274100000,0.0469417095059684,0.3033654265051843,0.0622745490981963,0.8839174326986211,0.3980591618018646
2017,2373000000,56669000000,15914000000,3267000000,25413000000,31256000000,20918000000,0.0418747463339744,0.2808237307875558,0.0576505673295805,0.8130598925006399,0.3691259771656461
2018,4478000000,56232000000,18696000000,3872000000,27586000000,28646000000,24358000000,0.079634371887893,0.332479726845924,0.0688575899843505,0.9629965789289954,0.4331697254232465
2019,5696000000,58381000000,22092000000,4259000000,29675000000,28706000000,25542000000,0.0975659889347561,0.3784107843305185,0.0729518165156472,1.0337560091966835,0.4375053527688803
2020,11653000000,69052000000,28116000000,7897000000,34507000000,34535000000,32218000000,0.1687568788738921,0.4071714070555523,0.1143630886867867,0.9991892283190966,0.4665759138040897
2021,6677000000,95123000000,35431000000,10318000000,40793000000,54146000000,39211000000,0.0701933286376586,0.3724756368070813,0.1084700860990507,0.7533889853359436,0.4122136602083618
2022,8219000000,97154000000,41910000000,8525000000,43978000000,53006000000,44915000000,0.0845976490931922,0.4313769891100726,0.087747287811104,0.8296796589065388,0.4623072647549252
2023,10577000000,98726000000,47364000000,6859000000,46735000000,51884000000,42857000000,0.1071348986082693,0.4797520410023702,0.0694751129388408,0.9007593863233366,0.4341004396005105
2024,8805000000,97321000000,53102000000,7662000000,49584000000,47650000000,42879000000,0.0904737929121155,0.5456376321657196,0.0787291540366416,1.0405876180482687,0.4405934998612837
"""

INDICATOR_NAME = "奥特曼破产预测模型 (Altman Z-Score)"

def to_native(v):
    # Convert numpy/pandas types to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    return v

def compute_altman_z_score(row):
    # Compute components from raw inputs:
    # X1 = (Current Assets - Current Liabilities) / Total Assets
    # Here Working Capital = Current Assets - Current Liabilities
    wc = row.get("Working Capital", None)
    ta = row.get("Total Assets", None)
    re = row.get("Retained Earnings", None)
    ebit = row.get("Operating Income", None)  # EBIT
    mve = row.get("Market Value of Equity", None)
    tl = row.get("Total Liabilities", None)
    s = row.get("Revenue", None)

    # Safety: convert to floats to avoid integer division issues and handle missing values
    try:
        wc_f = float(wc) if wc is not None else None
        ta_f = float(ta) if ta is not None else None
        re_f = float(re) if re is not None else None
        ebit_f = float(ebit) if ebit is not None else None
        mve_f = float(mve) if mve is not None else None
        tl_f = float(tl) if tl is not None else None
        s_f = float(s) if s is not None else None
    except Exception:
        # If any conversion fails, return None
        return None

    # Compute X1..X5 with guards against division by zero
    X1 = (wc_f / ta_f) if (ta_f and ta_f != 0.0) else None
    X2 = (re_f / ta_f) if (ta_f and ta_f != 0.0) else None
    X3 = (ebit_f / ta_f) if (ta_f and ta_f != 0.0) else None
    X4 = (mve_f / tl_f) if (tl_f and tl_f != 0.0) else None
    X5 = (s_f / ta_f) if (ta_f and ta_f != 0.0) else None

    # If any component is None, we cannot compute Z reliably
    if None in (X1, X2, X3, X4, X5):
        return None

    Z = 1.2 * X1 + 1.4 * X2 + 3.3 * X3 + 0.6 * X4 + 1.0 * X5
    return Z

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: raw rows as list of dicts with native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Prepare der_data: compute Altman Z-Score per row
    der_records = []
    for _, row in df.iterrows():
        # Build a plain dict for computation using raw column names
        row_dict = {col: (None if pd.isna(row[col]) else row[col]) for col in df.columns}
        z = compute_altman_z_score(row_dict)
        entry = {}
        # Preserve fiscal year if present
        if "Fiscal Year" in df.columns:
            entry["Fiscal Year"] = to_native(row["Fiscal Year"])
        # Store computed indicator (ensure numeric native type)
        entry[INDICATOR_NAME] = to_native(z) if z is not None else None
        der_records.append(entry)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()