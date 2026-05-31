#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Current Assets,Cash & Equiv,Current Liabilities,Short Term Debt,CapEx,NOPAT,NCWC,Change in NCWC,Reinvestment
2016,11976222000,4905609000,8878924000,2773000,496566000,3733962194.70991,-1805538000,344312000.0,840878000.0
2017,12097289000,4126860000,9824279000,2907000,515919000,4088011793.389648,-1850943000,-45405000.0,470514000.0
2018,13585559000,5061360000,10151751000,5337000,619187000,4280399535.7384944,-1622215000,228728000.0,847915000.0
2019,15450601000,6126853000,11061896000,6411000,599009000,4887540034.78264,-1731737000,-109522000.0,489487000.0
2020,17749756000,8415330000,12662590000,763877000,599132000,4985773932.595264,-2564287000,-832550000.0,-233418000.0
2021,19666511000,8168174000,15708867000,756244000,580132000,5882802478.832297,-3454286000,-889999000.0,-309867000.0
2022,21610871000,7889833000,17523496000,716773000,717998000,7118928279.766994,-3085685000,368601000.0,1086599000.0
2023,23381931000,9045032000,18009038000,795227000,528172000,6751075670.319231,-2876912000,208773000.0,736945000.0
2024,20857781000,5004469000,18976127000,1672431000,516509000,7340046235.686655,-1450384000,1426528000.0,1943037000.0
"""

INDICATOR_NAME = "资本再投资率 (Reinvestment Rate)"

def to_native_python(val):
    """Convert pandas / numpy numeric types and NaN to native Python types for JSON serialization."""
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        # Convert numpy float to python float
        return float(val)
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA), dtype=object)

    # Convert numeric-like columns to numeric types where appropriate
    # We'll try to convert each column except Fiscal Year to numeric if possible
    for col in df.columns:
        if col == "Fiscal Year":
            # Keep Fiscal Year as integer if possible
            try:
                df[col] = df[col].astype(int)
            except Exception:
                pass
            continue
        # coerce errors to NaN so we can handle them
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Prepare scr_data as list of dicts with native Python types
    scr_records = []
    for idx, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native_python(row[col])
        scr_records.append(rec)

    # Calculate Reinvestment Rate for each row:
    # Reinvestment Rate = (CapEx + Change in NCWC) / NOPAT
    der_records = []
    for idx, row in df.iterrows():
        fiscal_year = to_native_python(row.get("Fiscal Year"))
        capex = row.get("CapEx")
        change_ncwc = row.get("Change in NCWC")
        nopat = row.get("NOPAT")

        # Ensure numeric types (they may be NaN)
        capex_val = None if pd.isna(capex) else float(capex)
        change_ncwc_val = None if pd.isna(change_ncwc) else float(change_ncwc)
        nopat_val = None if pd.isna(nopat) else float(nopat)

        reinvestment_rate = None
        # Only compute if NOPAT is non-zero and not None
        if nopat_val not in (None, 0.0):
            # Treat missing CapEx or Change in NCWC as 0 if one of them is missing but others exist
            capex_used = 0.0 if capex_val is None else capex_val
            change_ncwc_used = 0.0 if change_ncwc_val is None else change_ncwc_val
            reinvestment_rate = (capex_used + change_ncwc_used) / nopat_val

            # Convert to native float
            reinvestment_rate = float(reinvestment_rate)
        else:
            reinvestment_rate = None

        rec = {
            "Fiscal Year": fiscal_year,
            INDICATOR_NAME: reinvestment_rate
        }
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file with UTF-8 encoding, preserving Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()