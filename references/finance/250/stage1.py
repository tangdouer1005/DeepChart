#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Current Assets,Cash & Equiv,Current Liabilities,Short Term Debt,CapEx,NOPAT,NCWC,Change in NCWC,Reinvestment
2016,6259796000.0,3393216000.0,5827005000.0,1262993000.0,1440471000,-667340000.0,-1697432000.0,-1099422000.0,341049000.0
2017,6570520000.0,3367914000.0,7674670000.0,978777000.0,4081354000,-1632000000.0,-3493287000.0,-1795855000.0,2285499000.0
2018,8307000000.0,3686000000.0,9993000000.0,2712000000.0,2319000000,-388000000.0,-2660000000.0,833287000.0,3152287000.0
2019,12103000000.0,6268000000.0,10667000000.0,2013000000.0,1437000000,-69000000.0,-2819000000.0,-159000000.0,1278000000.0
2020,26717000000.0,19384000000.0,14248000000.0,2418000000.0,3242000000,1489452339.6880417,-4497000000.0,-1678000000.0,1564000000.0
2021,27100000000.0,17576000000.0,19705000000.0,1589000000.0,8014000000,5950091124.073782,-8592000000.0,-4095000000.0,3919000000.0
2022,40917000000.0,16253000000.0,26709000000.0,1987000000.0,7172000000,12529198338.07129,-58000000.0,8534000000.0,15706000000.0
2023,49616000000.0,16398000000.0,28748000000.0,3045000000.0,8899000000,4432573147.498245,7515000000.0,7573000000.0,16472000000.0
2024,58360000000.0,16139000000.0,28821000000.0,3263000000.0,11342000000,5630103225.806451,16663000000.0,9148000000.0,20490000000.0
"""

INDICATOR_NAME = "资本再投资率 (Reinvestment Rate)"

def pyify_value(v):
    # Convert numpy/pandas types to native Python types for JSON serialization
    if v is None:
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        # convert NaN to None
        if np.isnan(v):
            return None
        return float(v)
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    if pd.isna(v):
        return None
    return v

def pyify_record(rec):
    return {k: pyify_value(v) for k, v in rec.items()}

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: raw input rows (convert types to native python)
    scr_records = [pyify_record(rec) for rec in df.to_dict(orient="records")]

    # Compute Reinvestment Rate for each row
    der_records = []
    for idx, row in df.iterrows():
        # Raw inputs required for calculation:
        # Capital Expenditure (CapEx), Change in NCWC (Change in NCWC), NOPAT
        capex = row.get("CapEx")
        change_ncwc = None
        # Prefer explicit "Change in NCWC" column if present, otherwise compute from NCWC differences
        if "Change in NCWC" in row.index:
            change_ncwc = row.get("Change in NCWC")
        else:
            # compute from NCWC column if available and previous row exists
            if "NCWC" in row.index and idx > 0:
                prev_ncwc = df.at[idx - 1, "NCWC"]
                curr_ncwc = row.get("NCWC")
                if pd.notna(prev_ncwc) and pd.notna(curr_ncwc):
                    change_ncwc = curr_ncwc - prev_ncwc

        nopat = row.get("NOPAT")

        reinvestment_rate = None
        # Only calculate if NOPAT is a valid non-zero number
        if pd.notna(nopat) and nopat != 0 and (pd.notna(capex) or pd.notna(change_ncwc)):
            # Treat missing capex or change_ncwc as 0 in the numerator if one is missing
            capex_val = 0.0 if pd.isna(capex) else float(capex)
            change_ncwc_val = 0.0 if pd.isna(change_ncwc) else float(change_ncwc)
            try:
                reinvestment_rate = (capex_val + change_ncwc_val) / float(nopat)
            except Exception:
                reinvestment_rate = None

        record = {}
        # Include the fiscal year if present
        if "Fiscal Year" in row.index:
            record["Fiscal Year"] = pyify_value(row["Fiscal Year"])
        record[INDICATOR_NAME] = pyify_value(reinvestment_rate)
        der_records.append(record)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write output JSON
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()