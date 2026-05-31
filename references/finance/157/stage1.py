#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

csv_data = """Fiscal Year,Working Capital,Total Assets,Retained Earnings,Operating Income,Market Value of Equity,Total Liabilities,Revenue,X1 (WC/TA),X2 (RE/TA),X3 (EBIT/TA),X4 (MVE/TL),X5 (S/TA)
2016,31526000000.0,64961000000.0,21670000000.0,12427000000,59194000000.0,5767000000.0,27638000000,0.4853065685565185,0.333584766244362,0.1912993950216283,10.264262181376798,0.4254552731638983
2017,44803000000.0,84524000000.0,33990000000.0,20203000000,74347000000.0,10177000000.0,40653000000,0.5300624674648621,0.4021343050494534,0.2390208698121243,7.305394517048246,0.4809639865600303
2018,43463000000.0,97334000000.0,41981000000.0,24913000000,84127000000.0,13207000000.0,55838000000,0.4465346127766248,0.4313086896665091,0.2559537263443401,6.369879609298099,0.5736741529167608
2019,51172000000.0,133376000000.0,55692000000.0,23986000000,101054000000.0,32322000000.0,70697000000,0.383667226487524,0.4175563819577735,0.1798374520153551,3.1264773219478994,0.5300578814779271
2020,60689000000.0,159316000000.0,77345000000.0,32671000000,128290000000.0,31026000000.0,85965000000,0.3809347460393181,0.4854816841999548,0.2050704260714554,4.1349191001095855,0.539587988651485
2021,45531000000.0,165987000000.0,69761000000.0,46753000000,124879000000.0,41108000000.0,117929000000,0.274304614216776,0.4202799014380644,0.2816666365438257,3.0378271869222537,0.7104713019694313
2022,32523000000.0,185727000000.0,64799000000.0,28944000000,125713000000.0,60014000000.0,116609000000,0.1751118577266633,0.3488938065009395,0.1558416385339772,2.0947278968240743,0.6278516316959839
2023,53405000000.0,229623000000.0,82070000000.0,46751000000,153168000000.0,76455000000.0,134902000000,0.2325768760098074,0.3574119317315774,0.2035989426146335,2.003374534039631,0.5874934131162819
2024,66449000000.0,276054000000.0,102506000000.0,69380000000,182637000000.0,93417000000.0,164501000000,0.2407101509125026,0.3713259000050715,0.2513276387953082,1.9550724172259868,0.5959015265129286
"""

def to_native(obj):
    # Recursively convert numpy and pandas types to native Python types for JSON serialization
    if isinstance(obj, dict):
        return {k: to_native(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_native(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if pd.isna(obj):
        return None
    return obj

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(csv_data))
    # Ensure numeric columns are proper dtype
    numeric_cols = ["Working Capital", "Total Assets", "Retained Earnings", "Operating Income",
                    "Market Value of Equity", "Total Liabilities", "Revenue"]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')

    # Compute components for Altman Z-Score dynamically (do not use precomputed X1..X5 columns)
    # X1 = (Current Assets - Current Liabilities) / Total Assets
    # Here Working Capital is Current Assets - Current Liabilities
    X1 = df["Working Capital"] / df["Total Assets"]

    # X2 = Retained Earnings / Total Assets
    X2 = df["Retained Earnings"] / df["Total Assets"]

    # X3 = EBIT / Total Assets -> using Operating Income as EBIT
    X3 = df["Operating Income"] / df["Total Assets"]

    # X4 = Market Value of Equity / Total Liabilities
    # If Total Liabilities is zero or NaN, avoid division by zero by producing NaN
    with np.errstate(divide='ignore', invalid='ignore'):
        X4 = df["Market Value of Equity"] / df["Total Liabilities"]

    # X5 = Sales / Total Assets (Revenue / Total Assets)
    X5 = df["Revenue"] / df["Total Assets"]

    # Altman Z formula:
    Z = 1.2 * X1 + 1.4 * X2 + 3.3 * X3 + 0.6 * X4 + 1.0 * X5

    # Build scr_data: original rows as list of dicts
    scr_records = df.to_dict(orient="records")
    scr_records = [to_native(r) for r in scr_records]

    # Build der_data: for each row, include Fiscal Year if present and the calculated Z-Score
    der_records = []
    for idx, row in df.iterrows():
        record = {}
        if "Fiscal Year" in df.columns:
            # cast to native int if possible
            fy = row["Fiscal Year"]
            record["Fiscal Year"] = int(fy) if not pd.isna(fy) else None
        z_val = Z.iloc[idx] if hasattr(Z, "iloc") else Z[idx]
        record["奥特曼破产预测模型 (Altman Z-Score)"] = None if pd.isna(z_val) else float(z_val)
        der_records.append(record)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()