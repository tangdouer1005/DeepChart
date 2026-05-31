#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Avg Total Equity,Dividends,ROE(Avg),Retention Ratio
2016,4059000000,5842000000.0,837000000.0,0.6947963026360835,0.7937915742793792
2017,3915000000,5562000000.0,942000000.0,0.7038834951456311,0.7593869731800766
2018,5859000000,5431500000.0,1044000000.0,1.0787075393537695,0.8218125960061444
2019,8118000000,5644000000.0,1345000000.0,1.4383416017009214,0.8343187977334319
2020,6411000000,6142000000.0,1605000000.0,1.0437968088570495,0.7496490407112775
2021,8687000000,6851500000.0,1741000000.0,1.2678975406845217,0.7995855876597214
2022,9930000000,6805000000.0,1903000000.0,1.4592211609110948,0.8083585095669688
2023,11195000000,6613500000.0,2158000000.0,1.6927496786875331,0.8072353729343457
2024,12874000000,6707000000.0,2448000000.0,1.9194871030266885,0.8098493086841696
"""

def to_native(py_val):
    # Convert numpy scalars to native Python types for JSON serialization
    if py_val is None or (isinstance(py_val, float) and (np.isnan(py_val))):
        return None
    if isinstance(py_val, (np.integer,)):
        return int(py_val)
    if isinstance(py_val, (np.floating,)):
        return float(py_val)
    return py_val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are proper dtype
    numeric_cols = ["Net Income", "Avg Total Equity", "Dividends"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Calculate Retention Ratio from raw data (do not use provided column)
    # Retention Ratio = 1 - (Dividends / Net Income)
    # Guard against division by zero
    def calc_retention(net_income, dividends):
        if net_income is None or net_income == 0 or pd.isna(net_income):
            return None
        return 1.0 - (dividends / net_income)

    # Calculate ROE from raw data (Net Income / Avg Total Equity)
    def calc_roe(net_income, avg_equity):
        if avg_equity is None or avg_equity == 0 or pd.isna(avg_equity):
            return None
        return net_income / avg_equity

    sgr_name = "可持续增长率 (Sustainable Growth Rate, SGR)"

    der_rows = []
    scr_rows = []

    for _, row in df.iterrows():
        fy = to_native(row.get("Fiscal Year"))

        net_income = row.get("Net Income")
        dividends = row.get("Dividends")
        avg_equity = row.get("Avg Total Equity")

        retention = calc_retention(net_income, dividends)
        roe = calc_roe(net_income, avg_equity)

        # SGR = ROE * Retention Ratio
        if retention is None or roe is None:
            sgr = None
        else:
            sgr = float(roe * retention)

        # Build scr_data row (reflect original CSV columns)
        scr_row = {}
        for col in df.columns:
            scr_row[col] = to_native(row.get(col))
        scr_rows.append(scr_row)

        # Build der_data row with Fiscal Year and calculated SGR
        der_row = {"Fiscal Year": fy, sgr_name: to_native(sgr)}
        der_rows.append(der_row)

    output_obj = {
        "scr_data": scr_rows,
        "der_data": der_rows
    }

    # Write JSON to specified output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()