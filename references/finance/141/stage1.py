#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Dividends,Net Income,Avg Total Assets,ROA(Avg),Retention Ratio
2016,837000000.0,4059000000,17472000000.0,0.2323145604395604,0.7937915742793792
2017,942000000.0,3915000000,20002000000.0,0.1957304269573042,0.7593869731800766
2018,1044000000.0,5859000000,23094500000.0,0.2536967676286562,0.8218125960061444
2019,1345000000.0,8118000000,27048000000.0,0.3001330967169476,0.8343187977334319
2020,1605000000.0,6411000000,31410000000.0,0.2041069723018147,0.7496490407112775
2021,1741000000.0,8687000000,35626500000.0,0.2438353472836231,0.7995855876597214
2022,1903000000.0,9930000000,38196500000.0,0.2599714633539722,0.8083585095669688
2023,2158000000.0,11195000000,40586000000.0,0.2758340314394126,0.8072353729343457
2024,2448000000.0,12874000000,45264500000.0,0.2844171480961902,0.8098493086841696
"""

INDICATOR_NAME = "内部增长率 (Internal Growth Rate, IGR)"

def to_native(v):
    # Convert numpy/pandas scalar types and NaN to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.bool_ , bool)):
        return bool(v)
    return v

def compute_igr(dividends, net_income, avg_total_assets):
    # Compute retention ratio b = 1 - (dividends / net_income)
    # Compute ROA = net_income / avg_total_assets
    # IGR = (ROA * b) / (1 - (ROA * b))
    # Handle division by zero and missing data gracefully
    try:
        if net_income is None or avg_total_assets is None or dividends is None:
            return None
        # convert to float
        d = float(dividends)
        ni = float(net_income)
        ata = float(avg_total_assets)
        if ata == 0 or ni == 0:
            # If net income is zero, retention ratio undefined; if assets zero, ROA undefined
            return None
        b = 1.0 - (d / ni)
        roa = ni / ata
        numerator = roa * b
        denom = 1.0 - numerator
        if denom == 0:
            return None
        igr = numerator / denom
        return float(igr)
    except Exception:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Build scr_data: preserve original columns and values (convert to native types)
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Build der_data: compute IGR for each row
    der_records = []
    for _, row in df.iterrows():
        dividends = row["Dividends"]
        net_income = row["Net Income"]
        avg_assets = row["Avg Total Assets"]
        igr_value = compute_igr(dividends, net_income, avg_assets)
        rec = {}
        # include Fiscal Year if present
        if "Fiscal Year" in df.columns:
            rec["Fiscal Year"] = to_native(row["Fiscal Year"])
        rec[INDICATOR_NAME] = to_native(igr_value)
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()