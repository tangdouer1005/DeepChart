#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Current Assets,Cash & Equiv,Current Liabilities,Short Term Debt,CapEx,NOPAT,NCWC,Change in NCWC,Reinvestment
2016,33782000000,7102000000,30770000000,11669000000,3314000000,10081001346.398384,7579000000,2521000000.0,5835000000.0
2017,26494000000,5569000000,30210000000,13567000000,3384000000,10585396696.085089,4282000000,-3297000000.0,87000000.0
2018,23320000000,2569000000,28237000000,10445000000,3717000000,9888379333.6335,2959000000,-1323000000.0,2394000000.0
2019,22473000000,4239000000,30011000000,9706000000,3347000000,3585671774.5921893,-2071000000,-5030000000.0,-1683000000.0
2020,27987000000,16181000000,32976000000,11422000000,3073000000,12997077049.387394,-9748000000,-7677000000.0,-4604000000.0
2021,23091000000,10288000000,33132000000,9108000000,2787000000,14654276014.760147,-11221000000,-1473000000.0,1314000000.0
2022,21653000000,7214000000,33081000000,8850000000,3156000000,14643384773.548208,-9792000000,1429000000.0,4585000000.0
2023,22648000000,8246000000,35756000000,10451000000,3062000000,14562136544.434153,-10903000000,-1111000000.0,1951000000.0
2024,24709000000,9482000000,33627000000,7434000000,3322000000,14801600660.94558,-10966000000,-63000000.0,3259000000.0
"""

def to_native_val(x):
    # Convert numpy/pandas scalar types to native Python types, keep None for NaN
    if pd.isna(x):
        return None
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        # Cast floats that are integer-valued to float nonetheless for consistency
        return float(x)
    return x

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows as dictionaries with native Python types
    scr_data = []
    for _, row in df.iterrows():
        row_dict = {}
        for col in df.columns:
            row_dict[col] = to_native_val(row[col])
        scr_data.append(row_dict)

    # Calculate Reinvestment Rate per the reference:
    # Reinvestment Rate = (CapEx + Change in NCWC) / NOPAT
    der_data = []
    for _, row in df.iterrows():
        fiscal_year = to_native_val(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None

        capex = row.get("CapEx", None)
        chg_ncwc = row.get("Change in NCWC", None)
        nopat = row.get("NOPAT", None)

        # Convert to native floats for calculation, handle missing values
        def as_float(v):
            if pd.isna(v):
                return None
            return float(v)

        capex_f = as_float(capex)
        chg_ncwc_f = as_float(chg_ncwc)
        nopat_f = as_float(nopat)

        reinvest_rate = None
        # Only compute if NOPAT is present and non-zero
        if nopat_f is not None and nopat_f != 0.0:
            # Treat missing CapEx or Change in NCWC as zero in the sum if one is missing
            capex_val = capex_f if capex_f is not None else 0.0
            chg_ncwc_val = chg_ncwc_f if chg_ncwc_f is not None else 0.0
            reinvest_rate = (capex_val + chg_ncwc_val) / nopat_f

        entry = {}
        if fiscal_year is not None:
            entry["Fiscal Year"] = fiscal_year
        # Use the exact indicator name as requested
        entry["资本再投资率 (Reinvestment Rate)"] = to_native_val(reinvest_rate) if reinvest_rate is not None else None
        der_data.append(entry)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()