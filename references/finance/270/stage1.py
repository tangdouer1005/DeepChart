#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Current Assets,Cash & Equiv,Current Liabilities,Short Term Debt,CapEx,NOPAT,NCWC,Change in NCWC,Reinvestment
2016,14313000000,5619000000,8046000000,2084000000,523000000,5894539815.277085,2732000000,-1491000000.0,-968000000.0
2017,19023000000,9874000000,9994000000,1749000000,707000000,6956786044.125193,904000000,-1828000000.0,-1121000000.0
2018,18216000000,8162000000,11305000000,2168000000,718000000,10420049508.043104,917000000,13000000.0,731000000.0
2019,20970000000,7838000000,13415000000,3990000000,756000000,12174958344.53104,3707000000,2790000000.0,3546000000.0
2020,27645000000,16289000000,14510000000,3107000000,736000000,11095297026.831038,-47000000,-3754000000.0,-3018000000.0
2021,27607000000,16487000000,15739000000,999000000,705000000,12112497291.913092,-3620000000,-3573000000.0,-2868000000.0
2022,30205000000,15689000000,20853000000,2250000000,970000000,15515330888.839876,-4087000000,-467000000.0,503000000.0
2023,33532000000,16286000000,23098000000,106000000,1059000000,17242620145.458,-5746000000,-1659000000.0,-600000000.0
2024,34033000000,11975000000,26517000000,0,1257000000,19478009909.68389,-4459000000,1287000000.0,2544000000.0
"""

def to_native(val):
    # Convert numpy types to native python types for JSON serialization
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        # Convert NaN to None
        if np.isnan(val):
            return None
        return float(val)
    if pd.isna(val):
        return None
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are of numeric dtype
    numeric_cols = ["Current Assets","Cash & Equiv","Current Liabilities","Short Term Debt","CapEx","NOPAT","NCWC","Change in NCWC"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Compute Change in NCWC dynamically when possible.
    # Prefer using the provided "Change in NCWC" column if present and not null.
    # Otherwise compute as difference of NCWC between periods.
    change_ncwc = []
    provided_change_exists = "Change in NCWC" in df.columns
    for idx, row in df.iterrows():
        provided = None
        if provided_change_exists:
            provided = row["Change in NCWC"]
            if not pd.isna(provided):
                change_ncwc.append(float(provided))
                continue
        # compute from NCWC difference if possible
        if idx == 0:
            change_ncwc.append(None)
        else:
            prev_ncwc = df.at[idx-1, "NCWC"] if "NCWC" in df.columns else np.nan
            cur_ncwc = row["NCWC"] if "NCWC" in df.columns else np.nan
            if pd.isna(prev_ncwc) or pd.isna(cur_ncwc):
                change_ncwc.append(None)
            else:
                change_ncwc.append(float(cur_ncwc - prev_ncwc))

    df["Calc_Change_in_NCWC"] = change_ncwc

    # For the Reinvestment Rate calculation use CapEx + Change in NCWC divided by NOPAT.
    # Use the calculated change if available; otherwise fall back to provided "Change in NCWC" or None.
    reinvestments = []
    for idx, row in df.iterrows():
        capex = row.get("CapEx", None)
        nopat = row.get("NOPAT", None)
        change = row.get("Calc_Change_in_NCWC", None)
        # If Calc_Change_in_NCWC is None but provided column exists, use provided
        if (change is None or pd.isna(change)) and ("Change in NCWC" in df.columns):
            change = row.get("Change in NCWC", None)
            if pd.isna(change):
                change = None
        # If any required value is missing or NOPAT is zero, result is None
        try:
            capex_val = None if pd.isna(capex) else float(capex)
        except:
            capex_val = None
        try:
            change_val = None if change is None or pd.isna(change) else float(change)
        except:
            change_val = None
        try:
            nopat_val = None if pd.isna(nopat) else float(nopat)
        except:
            nopat_val = None

        if nopat_val in (None, 0):
            reinvestments.append(None)
        else:
            # Treat missing capex/change as 0 if one is present? We'll require capex and change to be numeric;
            # if missing, assume 0 for that component (conservative handling).
            c = 0.0 if capex_val is None else capex_val
            nc = 0.0 if change_val is None else change_val
            val = (c + nc) / nopat_val
            reinvestments.append(val)

    df["Calculated_Reinvestment_Rate"] = reinvestments

    # Prepare scr_data: original CSV rows (preserve original columns)
    scr_records = df[list(pd.read_csv(io.StringIO(CSV_DATA)).columns)].to_dict(orient='records')

    # Convert numpy types to native python types for JSON serialization
    def normalize_records(records):
        out = []
        for rec in records:
            new = {}
            for k, v in rec.items():
                new[k] = to_native(v)
            out.append(new)
        return out

    scr_data = normalize_records(scr_records)

    # Prepare der_data: include Fiscal Year and the calculated indicator
    der_records = []
    for idx, row in df.iterrows():
        rec = {}
        # include year if present
        if "Fiscal Year" in df.columns:
            rec["Fiscal Year"] = to_native(row["Fiscal Year"])
        rec["资本再投资率 (Reinvestment Rate)"] = to_native(row["Calculated_Reinvestment_Rate"])
        der_records.append(rec)

    output = {
        "scr_data": scr_data,
        "der_data": der_records
    }

    # Write JSON to output file with UTF-8 encoding, preserve non-ascii chars
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()