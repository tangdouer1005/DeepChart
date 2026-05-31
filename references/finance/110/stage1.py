#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Current Assets,Cash & Equiv,Current Liabilities,Short Term Debt,CapEx,NOPAT,NCWC,Change in NCWC,Reinvestment
2016,16993000000,2216000000,15501000000,3402000000,1503000000,7487883676.617366,2678000000,40000000.0,1543000000.0
2017,17724000000,2538000000,14133000000,1252000000,1621000000,8553249459.61092,2305000000,-373000000.0,1248000000.0
2018,18933000000,3595000000,16194000000,2761000000,1897000000,9249308658.198277,1905000000,-400000000.0,1497000000.0
2019,18529000000,1778000000,16716000000,2395000000,2442000000,11865150453.42127,2430000000,525000000.0,2967000000.0
2020,19810000000,2133000000,18375000000,3641000000,2678000000,12103772069.317024,2943000000,513000000.0,3191000000.0
2021,28477000000,7895000000,23166000000,2244000000,2463000000,13851145482.388971,-340000000,-3283000000.0,-820000000.0
2022,29055000000,2343000000,28693000000,4312000000,2566000000,17418057689.653587,2331000000,2671000000.0,5237000000.0
2023,32471000000,2757000000,23110000000,2176000000,3119000000,18293682208.479782,8780000000,6449000000.0,9568000000.0
2024,29775000000,3760000000,22015000000,2418000000,3226000000,16484467325.838186,6418000000,-2362000000.0,864000000.0
"""

INDICATOR_NAME = "资本再投资率 (Reinvestment Rate)"

def pandas_row_to_pyobj(row):
    out = {}
    for k, v in row.items():
        if pd.isna(v):
            out[k] = None
        else:
            # convert numpy types to native python types for JSON serialization
            if isinstance(v, (np.integer,)):
                out[k] = int(v)
            elif isinstance(v, (np.floating,)):
                out[k] = float(v)
            else:
                out[k] = v
    return out

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data (original rows)
    scr_records = []
    for _, row in df.iterrows():
        scr_records.append(pandas_row_to_pyobj(row))

    # Calculate Reinvestment Rate for each row:
    # Reinvestment Rate = (CapEx + Change in NCWC) / NOPAT
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = row.get("Fiscal Year")
        capex = row.get("CapEx")
        change_ncwc = row.get("Change in NCWC")
        nopat = row.get("NOPAT")

        # Ensure numeric types
        capex_val = None if pd.isna(capex) else float(capex)
        change_ncwc_val = None if pd.isna(change_ncwc) else float(change_ncwc)
        nopat_val = None if pd.isna(nopat) else float(nopat)

        reinvestment_rate = None
        # Only compute if NOPAT is a non-zero number
        if nopat_val is not None and nopat_val != 0.0:
            # Treat missing capex or change_ncwc as 0 in the numerator if None
            num = (0.0 if capex_val is None else capex_val) + (0.0 if change_ncwc_val is None else change_ncwc_val)
            reinvestment_rate = num / nopat_val
            # keep as float
            reinvestment_rate = float(reinvestment_rate)
        else:
            reinvestment_rate = None

        rec = {"Fiscal Year": int(fiscal_year) if not pd.isna(fiscal_year) else None,
               INDICATOR_NAME: reinvestment_rate}
        der_records.append(rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()