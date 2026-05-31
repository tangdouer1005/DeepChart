#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Avg Receivables,Revenue,Avg Inventory,Cost of Revenue,Avg Payables,DSO,DIO,DPO
2016,2328000000.0,10776000000,1485000000.0,2225000000,540500000.0,78.85300668151447,243.60674157303373,88.66629213483147
2017,2926500000.0,12497000000,1582500000.0,2687000000,771000000.0,85.47431383532047,214.965574990696,104.7320431708225
2020,4077500000.0,15301000000,2118000000.0,3787000000,508000000.0,97.26733546827003,204.1378399788751,48.96223923950357
2021,2826000000.0,18884000000,2370500000.0,4489000000,632500000.0,54.62243168820165,192.7450434395188,51.42849186901314
2022,3215500000.0,22237000000,2308000000.0,5263000000,832000000.0,52.77948913972209,160.06460193805813,57.70093102793084
2023,3742500000.0,25098000000,2001000000.0,6022000000,880000000.0,54.42714558928998,121.2827964131518,53.33776154101628
"""

def to_native_value(v):
    # Convert numpy types to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (int, float, str, bool)):
        return v
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: convert dataframe rows to list of native dicts
    scr_data = []
    for _, row in df.iterrows():
        row_dict = {}
        for col in df.columns:
            row_dict[col] = to_native_value(row[col])
        scr_data.append(row_dict)

    # Calculate CCC for each row using:
    # DSO = (Avg Receivables / Revenue) * 365
    # DIO = (Avg Inventory / Cost of Revenue) * 365
    # DPO = (Avg Payables / Cost of Revenue) * 365
    # CCC = DSO + DIO - DPO
    der_data = []
    indicator_name = "现金循环周期 (Cash Conversion Cycle, CCC)"
    for _, row in df.iterrows():
        year_val = to_native_value(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None

        # Read raw inputs
        avg_receivables = row.get("Avg Receivables", None)
        revenue = row.get("Revenue", None)
        avg_inventory = row.get("Avg Inventory", None)
        cost_of_revenue = row.get("Cost of Revenue", None)
        avg_payables = row.get("Avg Payables", None)

        # Compute components with safe checks for division by zero / missing data
        DSO = None
        DIO = None
        DPO = None
        CCC = None
        try:
            if pd.notna(avg_receivables) and pd.notna(revenue) and revenue != 0:
                DSO = (float(avg_receivables) / float(revenue)) * 365.0
            if pd.notna(avg_inventory) and pd.notna(cost_of_revenue) and cost_of_revenue != 0:
                DIO = (float(avg_inventory) / float(cost_of_revenue)) * 365.0
            if pd.notna(avg_payables) and pd.notna(cost_of_revenue) and cost_of_revenue != 0:
                DPO = (float(avg_payables) / float(cost_of_revenue)) * 365.0

            if DSO is not None and DIO is not None and DPO is not None:
                CCC = DSO + DIO - DPO
        except Exception:
            # In case of unexpected types, leave values as None
            DSO = DSO
            DIO = DIO
            DPO = DPO
            CCC = CCC

        # Build output dict for this row. Include Year if present.
        out_row = {}
        if year_val is not None:
            out_row["Fiscal Year"] = year_val
        # Use native types for numeric values (or None)
        out_row[indicator_name] = to_native_value(CCC) if CCC is not None else None
        # Optionally include breakdown (not required, but can be helpful). Commented out to strictly follow minimal requirement.
        # out_row["DSO"] = to_native_value(DSO) if DSO is not None else None
        # out_row["DIO"] = to_native_value(DIO) if DIO is not None else None
        # out_row["DPO"] = to_native_value(DPO) if DPO is not None else None

        der_data.append(out_row)

    final_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()