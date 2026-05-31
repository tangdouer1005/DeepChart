#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Current Assets,Cash & Equiv,Current Liabilities,Short Term Debt,CapEx,NOPAT,NCWC,Change in NCWC,Reinvestment
2016,14217000000,5500000000,9022000000,354000000,8670000000,2541039965.620971,49000000,-913000000.0,7757000000.0
2017,8915000000,1219000000,11515000000,1612000000,11065000000,2761774122.1132555,-2207000000,-2256000000.0,8809000000.0
2018,8281000000,1203000000,10267000000,1682000000,5668000000,3914320142.966556,-1507000000,700000000.0,6368000000.0
2019,9305000000,1528000000,12506000000,3269000000,7358000000,4311078861.611992,-1460000000,47000000.0,7405000000.0
2020,23885000000,10385000000,21703000000,9510000000,12367000000,5158409065.155808,1307000000,2767000000.0,15134000000.0
2021,20891000000,6631000000,23499000000,10168000000,21692000000,6219459265.890779,929000000,-378000000.0,21314000000.0
2022,19067000000,4507000000,24742000000,9837000000,17301000000,5386640178.003815,-345000000,-1274000000.0,16027000000.0
2023,19015000000,5135000000,20928000000,9174000000,10811000000,10787373579.416311,2126000000,2471000000.0,13282000000.0
2024,18404000000,5409000000,20174000000,8984000000,12311000000,13880872077.21588,1805000000,-321000000.0,11990000000.0
"""

INDICATOR_NAME = "资本再投资率 (Reinvestment Rate)"

def to_native(val):
    """Convert numpy/pandas types to native Python types for JSON serialization."""
    if val is None:
        return None
    if isinstance(val, (np.integer, )):
        return int(val)
    if isinstance(val, (np.floating, )):
        # preserve floats but avoid NaN/inf issues
        if np.isnan(val) or np.isinf(val):
            return None
        return float(val)
    if isinstance(val, (pd.Timestamp, )):
        return str(val)
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA), dtype=object)

    # Convert numeric columns to floats where possible
    numeric_cols = [
        "Current Assets", "Cash & Equiv", "Current Liabilities", "Short Term Debt",
        "CapEx", "NOPAT", "NCWC", "Change in NCWC", "Reinvestment"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Calculation of Reinvestment Rate:
    # Reinvestment Rate = (CapEx + Change in NCWC) / NOPAT
    # Use the raw "Change in NCWC" column from CSV as the change in non-cash working capital.
    reinv_rates = []
    for idx, row in df.iterrows():
        fiscal = row.get("Fiscal Year")
        capex = row.get("CapEx")
        change_ncwc = row.get("Change in NCWC")
        nopat = row.get("NOPAT")

        # Defensive handling: if NOPAT is zero or missing, result is set to None
        rate = None
        try:
            if nopat is None or pd.isna(nopat) or nopat == 0:
                rate = None
            else:
                # Ensure numeric
                capex_v = float(capex) if (capex is not None and not pd.isna(capex)) else 0.0
                change_v = float(change_ncwc) if (change_ncwc is not None and not pd.isna(change_ncwc)) else 0.0
                nopat_v = float(nopat)
                rate = (capex_v + change_v) / nopat_v
        except Exception:
            rate = None

        reinv_rates.append({
            "Fiscal Year": to_native(fiscal),
            INDICATOR_NAME: to_native(rate)
        })

    # Prepare scr_data: original CSV rows as list of dicts with native types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": reinv_rates
    }

    # Write to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()