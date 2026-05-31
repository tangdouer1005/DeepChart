import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Current Assets,Cash & Equiv,Current Liabilities,Short Term Debt,CapEx,NOPAT,NCWC,Change in NCWC,Reinvestment
2016,34401000000.0,8903000000.0,2875000000.0,1247000000.0,4491000000,10142727192.842308,23870000000.0,8842000000.0,13333000000.0
2017,48563000000.0,8079000000.0,3760000000.0,2081000000.0,6733000000,15631475284.063318,38805000000.0,14935000000.0,21668000000.0
2018,50480000000.0,10019000000.0,7017000000.0,500000000.0,13915000000,21721393320.452663,33944000000.0,-4861000000.0,9054000000.0
2019,66225000000.0,19079000000.0,15053000000.0,800000000.0,15102000000,17869628002.5794,32893000000.0,-1051000000.0,14051000000.0
2020,75670000000.0,17576000000.0,14981000000.0,1023000000.0,15115000000,28698883845.69017,44136000000.0,11243000000.0,26358000000.0
2021,66666000000.0,16601000000.0,21135000000.0,1127000000.0,18567000000,38927874333.81271,30057000000.0,-14079000000.0,4488000000.0
2022,59549000000.0,14681000000.0,27026000000.0,1367000000.0,31431000000,23300628057.878483,19209000000.0,-10848000000.0,20583000000.0
2023,85365000000.0,41862000000.0,31960000000.0,1623000000.0,27266000000,38539904655.477776,13166000000.0,-6043000000.0,21223000000.0
2024,100045000000.0,43889000000.0,33596000000.0,2018000000.0,37256000000,61227754270.268745,24578000000.0,11412000000.0,48668000000.0
"""

INDICATOR_NAME = "资本再投资率 (Reinvestment Rate)"

def make_json_serializable(obj):
    """
    Recursively convert numpy and pandas scalar types to native Python types,
    and convert NaN to None so json.dump can handle them.
    """
    if isinstance(obj, dict):
        return {make_json_serializable(k): make_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [make_json_serializable(v) for v in obj]
    # numpy scalar types
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        if np.isnan(obj):
            return None
        return float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    # pandas NA
    if obj is pd.NA:
        return None
    # floats that may be NaN
    if isinstance(obj, float) and np.isnan(obj):
        return None
    return obj

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Keep original scraped data as list of dicts
    # Convert pandas/numpy types to native python types for JSON serialization later
    scr_records = df.to_dict(orient="records")
    scr_records = [make_json_serializable(rec) for rec in scr_records]

    # Calculation:
    # Reinvestment Rate = (CapEx + Change in NCWC) / NOPAT
    # Use the raw fields "CapEx", "Change in NCWC", and "NOPAT" from the CSV.
    der_records = []
    for idx, row in df.iterrows():
        fiscal_year = row.get("Fiscal Year", None)
        capex = row.get("CapEx", None)
        change_ncwc = row.get("Change in NCWC", None)
        nopat = row.get("NOPAT", None)

        # Defensive checks and conversions
        # If any of the required inputs are missing or NaN, result will be None
        try:
            capex_val = None if pd.isna(capex) else float(capex)
        except Exception:
            capex_val = None
        try:
            change_ncwc_val = None if pd.isna(change_ncwc) else float(change_ncwc)
        except Exception:
            change_ncwc_val = None
        try:
            nopat_val = None if pd.isna(nopat) else float(nopat)
        except Exception:
            nopat_val = None

        reinvest_rate = None
        if nopat_val is not None and nopat_val != 0.0 and (capex_val is not None or change_ncwc_val is not None):
            # treat missing capex/change_ncwc as zero if other present? Here require numeric; treat None as 0
            capex_num = 0.0 if capex_val is None else capex_val
            change_ncwc_num = 0.0 if change_ncwc_val is None else change_ncwc_val
            reinvest_rate = (capex_num + change_ncwc_num) / nopat_val
        else:
            reinvest_rate = None

        record = {}
        # Include Fiscal Year if present in input
        if fiscal_year is not None and not (pd.isna(fiscal_year)):
            # cast to native int if integral
            try:
                fy_native = int(fiscal_year)
            except Exception:
                fy_native = make_json_serializable(fiscal_year)
            record["Fiscal Year"] = fy_native
        record[INDICATOR_NAME] = make_json_serializable(reinvest_rate)
        der_records.append(record)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file with UTF-8 encoding, ensure_ascii=False to keep Chinese characters readable
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()