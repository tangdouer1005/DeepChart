#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Working Capital,Total Assets,Retained Earnings,Operating Income,Market Value of Equity,Total Liabilities,Revenue,X1 (WC/TA),X2 (RE/TA),X3 (EBIT/TA),X4 (MVE/TL),X5 (S/TA)
2016,3012000000,127136000000,87953000000,13441000000,57341000000,69153000000,65299000000,0.0236911653662219,0.6918024792348352,0.1057214321671281,0.8291903460442787,0.5136153410521017
2017,-3716000000,120406000000,96124000000,13766000000,55184000000,64628000000,65058000000,-0.0308622493895653,0.7983323090211452,0.1143298506718934,0.8538713870149162,0.5403219108682291
2018,-4917000000,118310000000,98641000000,13363000000,52293000000,65427000000,66832000000,-0.0415603076663003,0.8337503169639083,0.1129490322035331,0.7992571873996974,0.5648888513227961
2019,-7538000000,115095000000,94918000000,5487000000,47194000000,67516000000,67684000000,-0.0654937225770016,0.8246926452061341,0.0476736608888309,0.69900468037206,0.5880707241843695
2020,-4989000000,120700000000,100239000000,15706000000,46521000000,73822000000,70950000000,-0.0413338856669428,0.8304805302402651,0.1301242750621375,0.6301779957194332,0.5878210439105219
2021,-10041000000,119307000000,106374000000,17986000000,46378000000,72653000000,76118000000,-0.0841610299479494,0.8915989841333702,0.1507539373213642,0.6383494143393941,0.6380011231528745
2022,-11428000000,117208000000,112429000000,17813000000,46589000000,70354000000,80187000000,-0.0975018770049826,0.9592263326735376,0.1519776807043887,0.6622082610796828,0.6841427206334039
2023,-13108000000,120829000000,118170000000,18134000000,46777000000,73764000000,82006000000,-0.1084838904567612,0.9779936935669415,0.1500798649330872,0.6341440268965891,0.6786946842231584
2024,-8918000000,122370000000,123811000000,18545000000,50286000000,71812000000,84039000000,-0.0728773392171283,1.011775762033178,0.1515485821688322,0.7002450843870105,0.6867614611424369
"""

def to_native(val):
    """Convert pandas/numpy types to native Python types for JSON serialization."""
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        # convert NaN/inf handled above
        return float(val)
    return val

def compute_altman_z(row):
    """
    Compute Altman Z-Score:
    Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
    where:
      X1 = (Current Assets - Current Liabilities) / Total Assets  -> Working Capital / Total Assets
      X2 = Retained Earnings / Total Assets
      X3 = EBIT / Total Assets  -> Operating Income / Total Assets
      X4 = Market Value of Equity / Total Liabilities
      X5 = Sales / Total Assets
    """
    try:
        wc = row.get("Working Capital", None)
        ta = row.get("Total Assets", None)
        re = row.get("Retained Earnings", None)
        ebit = row.get("Operating Income", None)
        mve = row.get("Market Value of Equity", None)
        tl = row.get("Total Liabilities", None)
        s = row.get("Revenue", None)

        # Convert to floats for calculation, handle missing
        def to_float(x):
            if x is None:
                return None
            try:
                if pd.isna(x):
                    return None
            except Exception:
                pass
            try:
                return float(x)
            except Exception:
                return None

        wc = to_float(wc)
        ta = to_float(ta)
        re = to_float(re)
        ebit = to_float(ebit)
        mve = to_float(mve)
        tl = to_float(tl)
        s = to_float(s)

        # Compute components, guarding division by zero
        if ta in (0, None):
            x1 = None
            x2 = None
            x3 = None
            x5 = None
        else:
            x1 = wc / ta
            x2 = re / ta
            x3 = ebit / ta
            x5 = s / ta

        if tl in (0, None):
            x4 = None
        else:
            x4 = mve / tl

        comps = [x1, x2, x3, x4, x5]
        if any(c is None for c in comps):
            # If any required component is missing, return None (JSON null)
            return None

        z = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5
        return float(z)
    except Exception:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))
    # Prepare scr_data: list of dicts with native Python types
    raw_records = df.to_dict(orient='records')
    scr_data = []
    for rec in raw_records:
        converted = {}
        for k, v in rec.items():
            converted[k] = to_native(v)
        scr_data.append(converted)

    # Prepare der_data by computing Altman Z-Score for each row
    der_data = []
    for rec in scr_data:
        year_key = "Fiscal Year" if "Fiscal Year" in rec else None
        z_val = compute_altman_z(rec)
        der_entry = {}
        if year_key is not None:
            der_entry[year_key] = rec.get(year_key)
        der_entry["奥特曼破产预测模型 (Altman Z-Score)"] = to_native(z_val)
        der_data.append(der_entry)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()