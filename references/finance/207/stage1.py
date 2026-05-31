#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Working Capital,Total Assets,Retained Earnings,Operating Income,Market Value of Equity,Total Liabilities,Revenue,X1 (WC/TA),X2 (RE/TA),X3 (EBIT/TA),X4 (MVE/TL),X5 (S/TA)
2016,47105000000,112180000000,23888000000,12604000000,47289000000,64390000000,37047000000,0.4199055090033874,0.2129434836869317,0.1123551435193439,0.7344152818760677,0.3302460331609912
2017,50337000000,134991000000,27598000000,12913000000,53860000000,80745000000,37728000000,0.3728915261017401,0.2044432591802416,0.095658229067123,0.6670382067001053,0.2794852990199347
2018,56964000000,137264000000,18412000000,13264000000,46224000000,91040000000,39831000000,0.4149959202704278,0.1341356801492015,0.0966313090103741,0.5077328646748682,0.2901780510549015
2019,27756000000,108709000000,-3496000000,13535000000,21785000000,86346000000,39506000000,0.2553238462316827,-0.0321592508439963,0.1245067105759412,0.2522988905102726,0.3634105731816133
2020,34940000000,115438000000,-12696000000,13896000000,12074000000,102721000000,39068000000,0.3026732964881581,-0.1099811154039397,0.1203763058958055,0.1175416905988064,0.3384327517801763
2021,31403000000,131107000000,-20120000000,15213000000,5238000000,125155000000,40479000000,0.2395219172126583,-0.1534624390764795,0.1160349943176184,0.0418521033917941,0.3087478166688277
2022,12122000000,109297000000,-31336000000,10926000000,-6220000000,115065000000,42440000000,0.1109088081100121,-0.2867050330750157,0.0999661472867507,-0.0540564029027071,0.3882997703505128
2023,-2086000000,134384000000,-27620000000,13093000000,1073000000,132828000000,49954000000,-0.0155226812715799,-0.2055304202881295,0.0974297535420883,0.0080781160598668,0.3717258006905584
2024,-8990000000,140976000000,-22628000000,15353000000,8704000000,131737000000,52961000000,-0.063769719668596,-0.1605095902848712,0.1089050618545,0.0660710354721908,0.375673873567132
"""

def py_value(v):
    # Convert numpy/pandas scalar types to native Python types for JSON serialization
    if v is None:
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        # convert NaN to None
        if np.isnan(v):
            return None
        return float(v)
    if pd.isna(v):
        return None
    return v

def compute_altman_z(row):
    # Compute the Altman Z-Score from raw components in the row.
    # Formula:
    # Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
    # where:
    # X1 = (Current Assets - Current Liabilities) / Total Assets  -> Working Capital / Total Assets
    # X2 = Retained Earnings / Total Assets
    # X3 = EBIT / Total Assets  -> Operating Income / Total Assets
    # X4 = Market Value of Equity / Total Liabilities
    # X5 = Revenue / Total Assets
    # Use defensive checks for division by zero.
    try:
        wc = float(row.get("Working Capital")) if row.get("Working Capital") is not None else None
    except Exception:
        wc = None
    try:
        ta = float(row.get("Total Assets")) if row.get("Total Assets") is not None else None
    except Exception:
        ta = None
    try:
        re = float(row.get("Retained Earnings")) if row.get("Retained Earnings") is not None else None
    except Exception:
        re = None
    try:
        ebit = float(row.get("Operating Income")) if row.get("Operating Income") is not None else None
    except Exception:
        ebit = None
    try:
        mve = float(row.get("Market Value of Equity")) if row.get("Market Value of Equity") is not None else None
    except Exception:
        mve = None
    try:
        tl = float(row.get("Total Liabilities")) if row.get("Total Liabilities") is not None else None
    except Exception:
        tl = None
    try:
        s = float(row.get("Revenue")) if row.get("Revenue") is not None else None
    except Exception:
        s = None

    # Compute X1..X5 with safe division
    def safe_div(numer, denom):
        try:
            if numer is None or denom is None:
                return None
            if denom == 0:
                return None
            return numer / denom
        except Exception:
            return None

    X1 = safe_div(wc, ta)          # Working Capital / Total Assets
    X2 = safe_div(re, ta)          # Retained Earnings / Total Assets
    X3 = safe_div(ebit, ta)        # EBIT / Total Assets
    X4 = safe_div(mve, tl)         # Market Value of Equity / Total Liabilities
    X5 = safe_div(s, ta)           # Revenue / Total Assets

    # If any of X1..X5 is None, treat as 0 for the purposes of Z computation
    # (This is a pragmatic choice; alternatively could set Z to None)
    components = []
    for x in (X1, X2, X3, X4, X5):
        components.append(0.0 if x is None else float(x))

    Z = 1.2 * components[0] + 1.4 * components[1] + 3.3 * components[2] + 0.6 * components[3] + 1.0 * components[4]
    return float(Z)

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA), dtype=object)

    # Convert numeric-like strings to numeric types where possible
    # We'll attempt to coerce columns to numbers except the 'Fiscal Year' which should be int.
    for col in df.columns:
        if col.strip().lower() == "fiscal year":
            try:
                df[col] = df[col].astype(int)
            except Exception:
                # leave as-is
                pass
        else:
            # coerce numeric values
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Prepare scr_data: exact rows from input CSV, values converted to native Python types
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = py_value(row[col])
        scr_data.append(rec)

    # Prepare der_data: calculate Altman Z-Score for each row
    der_data = []
    for _, row in df.iterrows():
        row_dict = {}
        # include Fiscal Year if present
        if "Fiscal Year" in df.columns:
            fy_val = py_value(row["Fiscal Year"])
            row_dict["Fiscal Year"] = fy_val
        z = compute_altman_z(row)
        # Name as required
        row_dict["奥特曼破产预测模型 (Altman Z-Score)"] = z
        der_data.append(row_dict)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()