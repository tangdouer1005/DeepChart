#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Working Capital,Total Assets,Retained Earnings,Operating Income,Market Value of Equity,Total Liabilities,Revenue,X1 (WC/TA),X2 (RE/TA),X3 (EBIT/TA),X4 (MVE/TL),X5 (S/TA)
2016,80303000000,193694000000,2282000000,26078000000,71997000000,121697000000,91154000000,0.4145869257695127,0.0117814697409315,0.1346350429027228,0.5916086674281207,0.4706082790380703
2017,95324000000,241086000000,2648000000,29025000000,72394000000,168692000000,96571000000,0.3953941746928482,0.010983632396738,0.1203927229287474,0.4291489815758897,0.4005666027890462
2018,111174000000,258848000000,13682000000,35058000000,82718000000,176130000000,110360000000,0.4294953022623315,0.0528572753121523,0.1354385585362838,0.469641741895191,0.4263505995796761
2019,106132000000,286556000000,24150000000,42959000000,102330000000,184226000000,125843000000,0.3703708873658203,0.0842767207805804,0.1499148508493976,0.5554590557250334,0.439156744231494
2020,109605000000,301311000000,34566000000,52959000000,118304000000,183007000000,143015000000,0.3637603671953563,0.114718679371148,0.1757619204078178,0.6464452179424831,0.4746424790332912
2021,95749000000,333779000000,57055000000,69916000000,141988000000,191791000000,168088000000,0.2868634635492347,0.1709364579557132,0.2094679413623984,0.7403267098039011,0.5035906992351227
2022,74602000000,364840000000,84281000000,83383000000,166542000000,198298000000,198270000000,0.2044786755838175,0.2310081131454884,0.2285467602236597,0.8398571846412974,0.5434437013485364
2023,80108000000,411976000000,118848000000,88523000000,206223000000,205753000000,211915000000,0.1944482202846768,0.2884828242421888,0.2148741674272287,1.002284292331096,0.5143867603938094
2024,34448000000,512163000000,173144000000,109433000000,268477000000,243686000000,245122000000,0.0672598372002663,0.338064249076954,0.2136683048170211,1.1017333781998144,0.4786015389631816
"""

def to_python_value(v):
    """Convert pandas/numpy types to plain Python types for JSON serialization."""
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        # convert to Python float
        return float(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    return v

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python this.py output.json\n")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA), dtype=object)

    # Convert numeric-like columns to numeric types where possible
    # We will attempt to coerce columns (except Fiscal Year) to numeric
    for col in df.columns:
        if col == "Fiscal Year":
            # keep as int if possible
            try:
                df[col] = df[col].astype(int)
            except Exception:
                pass
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Prepare scr_data: original scraped data as array of dicts with sane Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_value(row[col])
        scr_records.append(rec)

    # Compute Altman Z-Score for each row dynamically using the formula provided
    der_records = []
    for _, row in df.iterrows():
        # Extract necessary raw inputs (use numeric conversion)
        # X1 = (Current Assets - Current Liabilities) / Total Assets
        # In dataset "Working Capital" == Current Assets - Current Liabilities
        wc = row.get("Working Capital")
        ta = row.get("Total Assets")
        re = row.get("Retained Earnings")
        ebit = row.get("Operating Income")  # treated as EBIT
        mve = row.get("Market Value of Equity")
        tl = row.get("Total Liabilities")
        s = row.get("Revenue")

        # Coerce to floats for calculation (handle None/NaN)
        def safe_float(x):
            try:
                if pd.isna(x):
                    return None
                return float(x)
            except Exception:
                return None

        wc_f = safe_float(wc)
        ta_f = safe_float(ta)
        re_f = safe_float(re)
        ebit_f = safe_float(ebit)
        mve_f = safe_float(mve)
        tl_f = safe_float(tl)
        s_f = safe_float(s)

        # Compute X ratios with safety checks
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
            if s_f is not None:
                X5 = s_f / ta_f

        if tl_f is not None and tl_f != 0 and mve_f is not None:
            X4 = mve_f / tl_f
        else:
            # If Total Liabilities is zero or missing, fall back to using book equity if possible
            # (Reference notes: for non-listed companies use book value of equity)
            # We'll attempt to compute book equity = Total Assets - Total Liabilities if available
            if ta_f is not None and tl_f is not None:
                book_equity = ta_f - tl_f
                if tl_f != 0:
                    X4 = book_equity / tl_f
                elif book_equity is not None and book_equity != 0:
                    # avoid division by zero; set X4 to a large number using market proxy
                    X4 = book_equity / (abs(book_equity) + 1e-12)

        # Replace any remaining None with 0.0 for calculation to avoid crashing,
        # but keep intention transparent (better to compute with zeros than crash)
        X1_v = 0.0 if X1 is None else float(X1)
        X2_v = 0.0 if X2 is None else float(X2)
        X3_v = 0.0 if X3 is None else float(X3)
        X4_v = 0.0 if X4 is None else float(X4)
        X5_v = 0.0 if X5 is None else float(X5)

        # Altman Z-Score formula
        Z = 1.2 * X1_v + 1.4 * X2_v + 3.3 * X3_v + 0.6 * X4_v + 1.0 * X5_v

        # Prepare output record; include Fiscal Year if present
        der_rec = {}
        if "Fiscal Year" in df.columns:
            fy = row.get("Fiscal Year")
            # ensure year is plain Python int if possible
            try:
                fy_py = int(fy)
            except Exception:
                fy_py = to_python_value(fy)
            der_rec["Fiscal Year"] = fy_py
        der_rec["奥特曼破产预测模型 (Altman Z-Score)"] = float(Z)
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to the specified output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()