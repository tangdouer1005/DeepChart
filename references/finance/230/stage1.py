#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Current Assets,Cash & Equiv,Current Liabilities,Short Term Debt,CapEx,NOPAT,NCWC,Change in NCWC,Reinvestment
2016,7021000000,786000000,4866000000,2097400000,444400000,2856922402.2926035,3466400000,1271800000.0,1716200000.0
2017,9421000000,1335000000,7048000000,2135000000,508000000,2996655413.7505145,3173000000,-293400000.0,214600000.0
2018,10625000000,2103000000,6147000000,1271000000,758000000,3487411404.046597,3646000000,473000000.0,1231000000.0
2019,11893000000,2399000000,6197000000,843000000,926000000,3867632432.4324327,4140000000,494000000.0,1420000000.0
2020,21957000000,10325000000,10304000000,2812000000,1474000000,6968198284.211983,4140000000,0.0,1474000000.0
2021,20113000000,4477000000,13436000000,2803000000,2523000000,9023141790.200294,5003000000,863000000.0,3386000000.0
2022,25229000000,8524000000,17010000000,5851000000,2243000000,7742920527.208665,5546000000,543000000.0,2786000000.0
2023,24589000000,8083000000,14012000000,3872000000,1479000000,6549702445.220705,6366000000,820000000.0,2299000000.0
2024,22137000000,4009000000,13332000000,2475000000,1400000000,6942352537.526805,7271000000,905000000.0,2305000000.0
"""

def to_python_native(value):
    # Convert numpy and pandas scalar types to native Python types for JSON serialization
    if pd.isna(value):
        return None
    if isinstance(value, (np.generic,)):
        return value.item()
    # plain Python numeric types or strings remain as-is
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Build scr_data: raw input rows as dictionaries with native Python types
    raw_records = df.to_dict(orient="records")
    scr_data = []
    for rec in raw_records:
        converted = {k: to_python_native(v) for k, v in rec.items()}
        scr_data.append(converted)

    # Calculate Reinvestment Rate for each row:
    # Reinvestment Rate = (CapEx + Change in NCWC) / NOPAT
    der_data = []
    for rec in raw_records:
        # Extract raw inputs (they are numpy scalars); convert to native floats for calculation
        capex = rec.get("CapEx")
        change_ncwc = rec.get("Change in NCWC")
        nopat = rec.get("NOPAT")

        # Safely convert to floats if not null
        try:
            capex_val = float(capex) if not pd.isna(capex) else None
        except Exception:
            capex_val = None
        try:
            change_ncwc_val = float(change_ncwc) if not pd.isna(change_ncwc) else None
        except Exception:
            change_ncwc_val = None
        try:
            nopat_val = float(nopat) if not pd.isna(nopat) else None
        except Exception:
            nopat_val = None

        reinvestment_rate = None
        if nopat_val is not None and nopat_val != 0.0:
            # Treat missing capex or change_ncwc as 0 for the purpose of this calculation only
            capex_for_calc = capex_val if capex_val is not None else 0.0
            change_ncwc_for_calc = change_ncwc_val if change_ncwc_val is not None else 0.0
            reinvestment_rate = (capex_for_calc + change_ncwc_for_calc) / nopat_val

        # Prepare derived record. Include Fiscal Year if present in raw data.
        der_rec = {}
        if "Fiscal Year" in rec:
            der_rec["Fiscal Year"] = to_python_native(rec["Fiscal Year"])
        der_rec["资本再投资率 (Reinvestment Rate)"] = to_python_native(reinvestment_rate)
        der_data.append(der_rec)

    output_obj = {"scr_data": scr_data, "der_data": der_data}

    # Write JSON to file with UTF-8 (to preserve Chinese characters)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()