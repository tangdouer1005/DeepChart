#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Current Assets,Cash & Equiv,Current Liabilities,Short Term Debt,CapEx,NOPAT,NCWC,Change in NCWC,Reinvestment
2017,5996827000,1606549000,7258353000,19594000.0,463958000,42625698.32402234,-2848481000.0,-435842000.0,28116000.0
2018,9290371000,2543484000,10129518000,1127256000.0,534027000,148708775.03117144,-2255375000.0,593106000.0,1127133000.0
2019,10683000000,2669000000,11255000000,3000000.0,595000000,465879959.30824006,-3238000000.0,-982625000.0,-387625000.0
2020,15963000000,4145000000,14845000000,750000000.0,643000000,36050991.50141644,-2277000000.0,961000000.0,1604000000.0
2021,21889000000,6195000000,17728000000,766000000.0,710000000,-703143303.3971106,-1268000000.0,1009000000.0,1719000000.0
2022,22850000000,5464000000,21788000000,686000000.0,717000000,-624916449.0861619,-3716000000.0,-2448000000.0,-1731000000.0
2023,26395000000,7016000000,25891000000,1772000000.0,798000000,921818181.818182,-4740000000.0,-1024000000.0,-226000000.0
2024,29074000000,8472000000,26631000000,1517000000.0,736000000,4186968888.888889,-4512000000.0,228000000.0,964000000.0
"""

def to_python_scalar(x):
    if pd.isna(x):
        return None
    # numpy scalar types
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        return float(x)
    # plain python types
    if isinstance(x, (int, float, str, bool)):
        return x
    # fallback: try to convert
    try:
        return int(x)
    except Exception:
        try:
            return float(x)
        except Exception:
            return x

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: convert dataframe rows into python-native types
    scr_df = df.copy()
    scr_df = scr_df.where(pd.notnull(scr_df), None)
    scr_records = []
    for _, row in scr_df.iterrows():
        rec = {}
        for col in scr_df.columns:
            rec[col] = to_python_scalar(row[col])
        scr_records.append(rec)

    # Calculate 资本再投资率 (Reinvestment Rate)
    # Formula: Reinvestment Rate = (CapEx + Change in NCWC) / NOPAT
    der_records = []
    for _, row in df.iterrows():
        year = to_python_scalar(row.get('Fiscal Year', None))
        capex = row.get('CapEx', None)
        change_ncwc = row.get('Change in NCWC', None)
        nopat = row.get('NOPAT', None)

        # Ensure numeric or treat missing
        try:
            capex_val = float(capex) if not pd.isna(capex) else None
        except Exception:
            capex_val = None
        try:
            change_ncwc_val = float(change_ncwc) if not pd.isna(change_ncwc) else None
        except Exception:
            change_ncwc_val = None
        try:
            nopat_val = float(nopat) if not pd.isna(nopat) else None
        except Exception:
            nopat_val = None

        reinvestment_rate = None
        # Only compute when NOPAT is a non-zero number
        if nopat_val is not None and nopat_val != 0.0:
            # treat missing capex/change as 0 in aggregation if necessary
            capex_use = capex_val if capex_val is not None else 0.0
            change_ncwc_use = change_ncwc_val if change_ncwc_val is not None else 0.0
            reinvestment_rate = (capex_use + change_ncwc_use) / nopat_val
            # convert to native python float
            reinvestment_rate = float(reinvestment_rate)
        else:
            reinvestment_rate = None

        der_rec = {
            "Fiscal Year": year,
            "资本再投资率 (Reinvestment Rate)": reinvestment_rate
        }
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()