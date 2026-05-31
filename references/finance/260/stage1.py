#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Current Assets,Cash & Equiv,Current Liabilities,Short Term Debt,CapEx,NOPAT,NCWC,Change in NCWC,Reinvestment
2016,33748000000,10430000000,49215000000,7193000000,1705000000,7709170530.220012,-18704000000,-3156000000.0,-1451000000.0
2017,37084000000,11981000000,50463000000,2857000000,2023000000,11738358910.36155,-22503000000,-3799000000.0,-1776000000.0
2018,38692000000,10866000000,53209000000,1973000000,2063000000,13469230306.071247,-23410000000,-907000000.0,1156000000.0
2019,42634000000,10985000000,61782000000,3870000000,2071000000,15588383015.405151,-26263000000,-2853000000.0,-782000000.0
2020,53718000000,16921000000,72420000000,4819000000,2051000000,17033287291.485874,-30804000000,-4541000000.0,-2490000000.0
2021,61758000000,21375000000,78292000000,3620000000,2454000000,19051368892.87315,-34289000000,-3485000000.0,-1031000000.0
2022,69069000000,23365000000,89237000000,3110000000,2802000000,22278023194.017387,-40423000000,-6134000000.0,-3332000000.0
2023,78437000000,25427000000,99054000000,5312000000,3386000000,25724565539.983517,-40732000000,-309000000.0,3077000000.0
2024,85779000000,25312000000,103769000000,4545000000,3499000000,24518880673.60869,-38757000000,1975000000.0,5474000000.0
"""

INDICATOR_NAME = "资本再投资率 (Reinvestment Rate)"

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Read CSV from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are numeric
    numeric_cols = ['Current Assets','Cash & Equiv','Current Liabilities','Short Term Debt',
                    'CapEx','NOPAT','NCWC','Change in NCWC','Reinvestment']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Prepare scr_data: original input rows as list of dicts.
    # Replace NaN with None for JSON compatibility
    scr_df = df.copy()
    scr_df = scr_df.where(pd.notnull(scr_df), None)
    scr_data = scr_df.to_dict(orient='records')

    # Calculate Reinvestment Rate per the reference:
    # Reinvestment Rate = (CapEx + Change in NCWC) / NOPAT
    der_data = []
    for _, row in df.iterrows():
        fiscal_year = row.get('Fiscal Year')
        capex = row.get('CapEx')
        change_ncwc = row.get('Change in NCWC')
        nopat = row.get('NOPAT')

        # Validate inputs and compute
        reinvest_rate = None
        try:
            # If any of the required inputs are NaN/None, result remains None
            if pd.notnull(capex) and pd.notnull(change_ncwc) and pd.notnull(nopat):
                # Protect against division by zero
                if nopat != 0:
                    reinvest_rate = (float(capex) + float(change_ncwc)) / float(nopat)
                else:
                    reinvest_rate = None
        except Exception:
            reinvest_rate = None

        der_row = {
            "Fiscal Year": int(fiscal_year) if pd.notnull(fiscal_year) else None,
            INDICATOR_NAME: (None if reinvest_rate is None else float(reinvest_rate))
        }
        der_data.append(der_row)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON output
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()