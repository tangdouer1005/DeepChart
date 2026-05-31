#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Current Assets,Cash & Equiv,Current Liabilities,Short Term Debt,CapEx,NOPAT,NCWC,Change in NCWC,Reinvestment
2016,26776000000,18620000000,6660000000,1325000000,1121000000,2444222929.936306,2821000000,-277000000.0,844000000.0
2017,20147000000,9407000000,8912000000,714000000,1135000000,312019722.09771395,2542000000,-279000000.0,856000000.0
2018,14632000000,3844000000,9012000000,207000000,1394000000,3122831883.049078,1983000000,-559000000.0,835000000.0
2019,15667000000,3860000000,10863000000,1683000000,1638000000,4151831493.7454014,2627000000,644000000.0,2282000000.0
2020,20441000000,6838000000,11907000000,461000000,2177000000,4761686996.779388,2157000000,-470000000.0,1707000000.0
2021,24239000000,9799000000,13105000000,999000000,1885000000,7922689075.630252,2334000000,177000000.0,2062000000.0
2022,25224000000,9882000000,15489000000,2481000000,1777000000,6979743077.293523,2334000000,0.0,1777000000.0
2023,22670000000,6896000000,13841000000,1325000000,2202000000,5526336284.513805,3258000000,924000000.0,3126000000.0
2024,23656000000,7616000000,14157000000,1754000000,2207000000,607272208.7551686,3637000000,379000000.0,2586000000.0
"""

INDICATOR_NAME = "资本再投资率 (Reinvestment Rate)"

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are numeric
    numeric_cols = ["Current Assets", "Cash & Equiv", "Current Liabilities", "Short Term Debt",
                    "CapEx", "NOPAT", "NCWC", "Change in NCWC", "Reinvestment"]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Compute non-cash working capital change dynamically using NCWC (if NCWC is present).
    # NCWC as defined: (Current Assets - Cash) - (Current Liabilities - Short Term Debt)
    # But since the CSV provides NCWC, we'll compute change as difference in NCWC between periods.
    # For the first period where no prior exists, fall back to the provided "Change in NCWC" raw value.
    computed_ncwc = df["NCWC"].copy()
    computed_change = computed_ncwc - computed_ncwc.shift(1)
    # Fill first-period change with provided raw "Change in NCWC" if available
    if "Change in NCWC" in df.columns:
        computed_change.iloc[0] = df["Change in NCWC"].iloc[0]

    # Now compute Reinvestment Rate: (CapEx + Change in NCWC) / NOPAT
    reinvestment = []
    for idx, row in df.iterrows():
        capex = row.get("CapEx", np.nan)
        nopat = row.get("NOPAT", np.nan)
        change_ncwc = computed_change.iloc[idx]
        # If nopat is NaN or zero, result is set to None to avoid division errors
        if pd.isna(nopat) or nopat == 0:
            rr = None
        else:
            rr = (capex + change_ncwc) / nopat
            # ensure rr is a native Python float
            if pd.isna(rr):
                rr = None
            else:
                rr = float(rr)
        reinvestment.append(rr)

    # Prepare scr_data: original rows as dictionaries, converting numpy/pandas types to Python types
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            val = row[col]
            if pd.isna(val):
                rec[col] = None
            else:
                # Convert numpy numbers to native Python types
                if isinstance(val, (np.integer,)):
                    rec[col] = int(val)
                elif isinstance(val, (np.floating,)):
                    rec[col] = float(val)
                else:
                    rec[col] = val
        scr_data.append(rec)

    # Prepare der_data: one dict per row containing Fiscal Year (if present) and the calculated indicator
    der_data = []
    year_col = "Fiscal Year" if "Fiscal Year" in df.columns else None
    for idx, rr in enumerate(reinvestment):
        rec = {}
        if year_col:
            year_val = df.at[idx, year_col]
            if pd.isna(year_val):
                rec[year_col] = None
            else:
                # fiscal year appears integer-like
                if isinstance(year_val, (np.integer,)):
                    rec[year_col] = int(year_val)
                elif isinstance(year_val, (np.floating,)):
                    # but fiscal year shouldn't be float; still convert if needed
                    rec[year_col] = int(year_val) if year_val.is_integer() else float(year_val)
                else:
                    rec[year_col] = year_val
        # add the calculated indicator value (may be None)
        rec[INDICATOR_NAME] = (None if rr is None else float(rr))
        der_data.append(rec)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()