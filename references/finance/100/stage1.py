#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Current Assets,Cash & Equiv,Current Liabilities,Short Term Debt,CapEx,NOPAT,NCWC,Change in NCWC,Reinvestment
2016,105408000000,12918000000,16756000000,554000000.0,10212000000,19127960579.710144,76288000000.0,18808000000.0,29020000000.0
2017,124308000000,10715000000,24183000000,16740000000.0,13184000000,12189380943.625198,106150000000.0,29862000000.0,43046000000.0
2018,135676000000,16701000000,34620000000,69000000.0,25139000000,24231021797.038357,84424000000.0,-21726000000.0,3413000000.0
2019,152578000000,18498000000,45221000000,1199000000.0,23548000000,29668018498.42271,90058000000.0,5634000000.0,29182000000.0
2020,174296000000,26465000000,56834000000,1694000000.0,22281000000,34525378644.8151,92691000000.0,2633000000.0,24914000000.0
2021,188143000000,20945000000,64254000000,2189000000.0,24640000000,65960517138.007805,105133000000.0,12442000000.0,37082000000.0
2022,164795000000,21879000000,69300000000,2477000000.0,31485000000,62926542507.85105,76093000000.0,-29040000000.0,2445000000.0
2023,171530000000,24048000000,81814000000,2791000000.0,32251000000,72569057888.16687,68459000000.0,-7634000000.0,24617000000.0
2024,163711000000,23466000000,89122000000,2887000000.0,52535000000,93913633685.2648,54010000000.0,-14449000000.0,38086000000.0
"""

INDICATOR_NAME = "资本再投资率 (Reinvestment Rate)"

def to_native(val):
    """Convert pandas/numpy scalar to native Python types for JSON serialization."""
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer, int)):
        return int(val)
    if isinstance(val, (np.floating, float)):
        # Convert to Python float
        return float(val)
    return val

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows as list of dicts with native types
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_data.append(rec)

    # Calculate Reinvestment Rate for each row:
    # Reinvestment Rate = (CapEx + Change in NCWC) / NOPAT
    der_data = []
    for _, row in df.iterrows():
        fiscal = to_native(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None

        # Extract inputs
        capex = row.get("CapEx", None)
        change_ncwc = row.get("Change in NCWC", None)
        nopat = row.get("NOPAT", None)

        # Handle missing / NaN
        capex_val = None if pd.isna(capex) else float(capex)
        change_ncwc_val = None if pd.isna(change_ncwc) else float(change_ncwc)
        nopat_val = None if pd.isna(nopat) else float(nopat)

        reinv_rate = None
        # Only compute if NOPAT is a non-zero numeric value
        if nopat_val is not None and nopat_val != 0.0:
            # Treat missing capex/change as 0.0 if one of them is missing but others exist
            capex_num = capex_val if capex_val is not None else 0.0
            change_ncwc_num = change_ncwc_val if change_ncwc_val is not None else 0.0
            reinv_rate = (capex_num + change_ncwc_num) / nopat_val
            # Ensure it's a native float
            reinv_rate = float(reinv_rate)
        else:
            reinv_rate = None

        entry = {}
        if fiscal is not None:
            entry["Fiscal Year"] = fiscal
        entry[INDICATOR_NAME] = reinv_rate
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