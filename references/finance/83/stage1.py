#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Operating Income,Income Tax,Pretax Income,Effective Tax Rate,NOPAT,Avg Invested Capital
2016,14178000000,1133000000,7031000000,0.1611435073247048,11893307353.150335,283310000000.0
2017,-2739000000,2808000000,-11345000000,0.0,-2739000000.0,185716000000.0
2018,6761000000,93000000,-20987000000,0.0,6761000000.0,157818500000.0
2019,5151000000,552000000,-54000000,0.0,5151000000.0,136047000000.0
2020,409000000,487000000,5970000000,0.081574539363484,375636013.400335,88567000000.0
2021,1058000000,757000000,-5695000000,0.0,1058000000.0,66874000000.0
2022,1858000000,476000000,-799000000,0.0,1858000000.0,54971500000.0
2023,4717000000,994000000,10441000000,0.0952016090412795,4267934010.152284,41772000000.0
2024,6761000000,962000000,7620000000,0.126246719160105,5907445931.758531,29302500000.0
"""

INDICATOR_NAME = "投入资本回报率 (Return on Invested Capital, ROIC)"

def to_py(val):
    """Convert numpy/pandas scalar types to native Python types for JSON serialization."""
    if val is None:
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    # pandas uses numpy.bool_ sometimes
    if isinstance(val, (np.bool_,)):
        return bool(val)
    # pandas NaN
    if pd.isna(val):
        return None
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows as list of dicts (convert types to native Python)
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_py(row[col])
        scr_data.append(rec)

    # Prepare der_data: compute ROIC for each row
    der_data = []
    for _, row in df.iterrows():
        # Extract necessary fields with safe handling
        fiscal_year = to_py(row.get("Fiscal Year")) if "Fiscal Year" in df.columns else None

        # Compute NOPAT per reference: NOPAT = Operating Income * (1 - Effective Tax Rate)
        op_income = row.get("Operating Income", None)
        eff_tax = row.get("Effective Tax Rate", None)

        # If Operating Income is missing, try to fall back to provided NOPAT (but still adhere to formula preference)
        nopat_calc = None
        try:
            if pd.notna(op_income) and pd.notna(eff_tax):
                nopat_calc = float(op_income) * (1.0 - float(eff_tax))
            elif "NOPAT" in df.columns and pd.notna(row.get("NOPAT")):
                nopat_calc = float(row.get("NOPAT"))
            else:
                nopat_calc = None
        except Exception:
            nopat_calc = None

        # Determine Invested Capital.
        # Prefer 'Avg Invested Capital' if present in the raw data; otherwise attempt decomposition (not available here).
        invested_capital = None
        if "Avg Invested Capital" in df.columns and pd.notna(row.get("Avg Invested Capital")):
            invested_capital = float(row.get("Avg Invested Capital"))
        else:
            # If components (e.g., Debt, Equity, Cash) were present we would compute:
            # invested_capital = interest_bearing_debt + shareholders_equity - cash_and_equivalents
            invested_capital = None

        # Compute ROIC = NOPAT / InvestedCapital, guard divide-by-zero and missing data
        roic = None
        try:
            if nopat_calc is not None and invested_capital is not None:
                if invested_capital != 0:
                    roic = float(nopat_calc) / float(invested_capital)
                else:
                    roic = None
            else:
                roic = None
        except Exception:
            roic = None

        rec = {}
        if fiscal_year is not None:
            rec["Fiscal Year"] = fiscal_year
        rec[INDICATOR_NAME] = to_py(roic)
        der_data.append(rec)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write to the specified output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()