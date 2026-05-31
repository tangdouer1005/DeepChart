import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Working Capital,Total Assets,Retained Earnings,Operating Income,Market Value of Equity,Total Liabilities,Revenue,X1 (WC/TA),X2 (RE/TA),X3 (EBIT/TA),X4 (MVE/TL),X5 (S/TA)
2016,3615000000,7370000000,4350000000,747000000,4469000000,2901000000,5010000000,0.4905020352781546,0.5902306648575305,0.1013568521031207,1.5405032747328506,0.6797829036635007
2017,6717000000,9841000000,6108000000,1934000000,5762000000,4079000000,6910000000,0.6825525861192968,0.6206686312366629,0.1965247434203841,1.4126011277273842,0.7021644141855502
2018,8102000000,11241000000,8787000000,3210000000,7471000000,3770000000,9714000000,0.720754381282804,0.781692020282893,0.2855617827595409,1.9816976127320955,0.8641579930611155
2019,9228000000,13292000000,12565000000,3804000000,9342000000,3950000000,11716000000,0.6942521817634667,0.9453054468853446,0.2861871802588023,2.3650632911392404,0.8814324405657539
2020,11906000000,17315000000,14971000000,2846000000,12204000000,5111000000,10918000000,0.6876118971989604,0.8646260467802483,0.164366156511695,2.387791038935629,0.630551544903263
2021,12130000000,28791000000,18908000000,4532000000,16893000000,11898000000,16675000000,0.4213122156229377,0.656733006842416,0.1574103018304331,1.41981845688351,0.5791740474453823
2022,24494000000,44187000000,16235000000,10041000000,26612000000,17575000000,26914000000,0.5543259329667096,0.3674157557652703,0.2272387806368389,1.5141963015647226,0.6090931721999683
2023,16510000000,41182000000,10171000000,4224000000,22101000000,19081000000,26974000000,0.4009033072701666,0.2469768345393618,0.1025690835802049,1.1582726272207955,0.6549949006847652
2024,33714000000,65728000000,29817000000,32972000000,42978000000,22750000000,60922000000,0.5129320837390458,0.4536422833495618,0.501643135345667,1.8891428571428568,0.9268804771178188
"""

def to_python_native(obj):
    """
    Convert numpy / pandas scalar types to Python native types for JSON serialization.
    """
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.bool_ , bool)):
        return bool(obj)
    if pd.isna(obj):
        return None
    # For other types (str, int, float) return as-is
    return obj

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows as list of dicts, with native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_native(row[col])
        scr_records.append(rec)

    # Calculate Altman Z-Score for each row
    der_records = []
    indicator_name = "奥特曼破产预测模型 (Altman Z-Score)"
    for _, row in df.iterrows():
        # Extract required fields, with safe handling for zero denominators
        wc = row.get("Working Capital", None)
        ta = row.get("Total Assets", None)
        re = row.get("Retained Earnings", None)
        ebit = row.get("Operating Income", None)  # EBIT approximated by Operating Income
        mve = row.get("Market Value of Equity", None)
        tl = row.get("Total Liabilities", None)
        sales = row.get("Revenue", None)

        # Convert to floats for calculation, handle missing
        def safe_float(x):
            if pd.isna(x):
                return None
            try:
                return float(x)
            except Exception:
                return None

        wc_f = safe_float(wc)
        ta_f = safe_float(ta)
        re_f = safe_float(re)
        ebit_f = safe_float(ebit)
        mve_f = safe_float(mve)
        tl_f = safe_float(tl)
        sales_f = safe_float(sales)

        # Compute X1..X5 with guard against zero division
        X1 = None
        X2 = None
        X3 = None
        X4 = None
        X5 = None

        if ta_f is not None and ta_f != 0:
            if wc_f is not None:
                X1 = wc_f / ta_f
            if re_f is not None:
                X2 = re_f / ta_f
            if ebit_f is not None:
                X3 = ebit_f / ta_f
            if sales_f is not None:
                X5 = sales_f / ta_f

        if tl_f is not None and tl_f != 0 and mve_f is not None:
            X4 = mve_f / tl_f

        # For any missing X's, treat as 0 in the weighted sum? According to conservative approach,
        # if a ratio can't be computed due to missing data, we propagate None.
        # Here we'll compute Z only if all X1..X5 are not None; otherwise set None.
        Xs = [X1, X2, X3, X4, X5]
        if all(x is not None for x in Xs):
            Z = 1.2 * X1 + 1.4 * X2 + 3.3 * X3 + 0.6 * X4 + 1.0 * X5
        else:
            Z = None

        der_rec = {
            "Fiscal Year": to_python_native(row["Fiscal Year"]),
            indicator_name: to_python_native(Z)
        }
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON output with non-ASCII characters preserved
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()