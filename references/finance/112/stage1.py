#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Avg Receivables,Revenue,Avg Inventory,Cost of Revenue,Avg Payables,DSO,DIO,DPO
2016,11216500000.0,71890000000,8098500000.0,21789000000,6793000000.0,56.94842815412436,135.6626049841663,113.79342787645142
2017,12594500000.0,76450000000,8454500000.0,25439000000,7114000000.0,60.1307063440157,121.3055741184795,102.07201540941074
2018,13794000000.0,81581000000,8682000000.0,27091000000,7423500000.0,61.71547296551893,116.97353364586024,100.01762577977928
2019,14289500000.0,82059000000,8809500000.0,27556000000,8040500000.0,63.55996904666154,116.68847075047177,106.50248584700248
2020,14028500000.0,82584000000,9182000000.0,28427000000,9024500000.0,62.0023551777584,117.89601435255216,115.87372920111162
2021,16280000000.0,78740000000,9865500000.0,23402000000,10280000000.0,75.46609093218187,153.87178446286643,160.33672335697804
2022,17949500000.0,79990000000,10327500000.0,24596000000,10472000000.0,81.90483185398175,153.25815173198896,155.40250447227191
2023,15894000000.0,85159000000,10724500000.0,26739000000,9760500000.0,68.12327528505502,146.39449867235123,133.23544261191518
2024,16900000000.0,88821000000,11812500000.0,27471000000,9971500000.0,69.4486664189775,156.9496013978377,132.48871537257472
"""

INDICATOR_NAME = "现金循环周期 (Cash Conversion Cycle, CCC)"

def to_native(val):
    # convert numpy types to native python types for json serialization
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if pd.isna(val):
        return None
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure column names are as expected; columns needed for CCC:
    # Avg Receivables, Revenue, Avg Inventory, Cost of Revenue, Avg Payables
    required_cols = ["Fiscal Year", "Avg Receivables", "Revenue", "Avg Inventory", "Cost of Revenue", "Avg Payables"]
    for c in required_cols:
        if c not in df.columns:
            raise KeyError(f"Required column missing from data: {c}")

    # Calculate DSO, DIO, DPO and CCC per reference formulas, row by row
    der_rows = []
    for _, row in df.iterrows():
        # extract raw inputs
        avg_receivables = float(row["Avg Receivables"]) if not pd.isna(row["Avg Receivables"]) else None
        revenue = float(row["Revenue"]) if not pd.isna(row["Revenue"]) else None
        avg_inventory = float(row["Avg Inventory"]) if not pd.isna(row["Avg Inventory"]) else None
        cost_of_revenue = float(row["Cost of Revenue"]) if not pd.isna(row["Cost of Revenue"]) else None
        avg_payables = float(row["Avg Payables"]) if not pd.isna(row["Avg Payables"]) else None

        # Compute turnover days, guarding against division by zero / missing data
        dso = None
        dio = None
        dpo = None
        ccc = None

        if revenue and revenue != 0 and avg_receivables is not None:
            dso = (avg_receivables / revenue) * 365.0

        if cost_of_revenue and cost_of_revenue != 0:
            if avg_inventory is not None:
                dio = (avg_inventory / cost_of_revenue) * 365.0
            if avg_payables is not None:
                dpo = (avg_payables / cost_of_revenue) * 365.0

        # CCC = DSO + DIO - DPO (only if we have the necessary parts; treat missing as None)
        if dso is not None and dio is not None and dpo is not None:
            ccc = dso + dio - dpo

        # Prepare output dict for this row; include Year if present
        out_row = {}
        # keep same year field name as in input CSV header ("Fiscal Year")
        if "Fiscal Year" in df.columns:
            out_row["Fiscal Year"] = to_native(row["Fiscal Year"])
        out_row[INDICATOR_NAME] = to_native(ccc)
        der_rows.append(out_row)

    # Prepare scr_data as list of dictionaries with native python types
    scr_records = df.where(pd.notnull(df), None).applymap(lambda x: x.item() if hasattr(x, "item") else x).to_dict(orient="records")
    # Ensure native types for each value
    scr_records_native = []
    for rec in scr_records:
        rec_native = {k: to_native(v) for k, v in rec.items()}
        scr_records_native.append(rec_native)

    result = {
        "scr_data": scr_records_native,
        "der_data": der_rows
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()