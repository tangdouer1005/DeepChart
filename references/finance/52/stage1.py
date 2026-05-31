#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Avg Receivables,Revenue,Avg Inventory,Cost of Revenue,Avg Payables,DSO,DIO,DPO
2016,2214506000.0,6667216000,556767000.0,1654548000,83509000.0,121.2342138007828,122.82505856584396,18.422424130336505
2017,2877163000.0,8391984000,240508500.0,2234000000,93369000.0,125.13900109914414,39.29525626678603,15.255006714413607
2018,3590456500.0,10480012000,0.0,2773522000,95861000.0,125.04915285402346,0.0,12.615463299011148
2019,4437046500.0,13282000000,394000000.0,3451000000,120732500.0,121.93359226773076,41.67197913648218,12.769447261663288
2020,5549000000.0,17098000000,857000000.0,4235000000,1799000000.0,118.45742192069248,73.86186540731995,155.0495867768595
2021,6980000000.0,21252000000,1036000000.0,5438000000,3894000000.0,119.88048183700356,69.536594336153,261.3663111438029
2022,8762500000.0,26492000000,1300000000.0,7026000000,4914500000.0,120.72748376868488,67.53487048107031,255.3077853686308
2023,10247000000.0,31352000000,1615000000.0,8360000000,6108500000.0,119.29557922939524,70.51136363636364,266.6988636363636
"""

INDICATOR_NAME = "现金循环周期 (Cash Conversion Cycle, CCC)"

def to_py_type(value):
    # Convert numpy/pandas scalar types to native Python types for JSON serialization
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    # For plain Python numeric types or strings, return as-is
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: represent the original CSV rows
    scr_records_raw = df.to_dict(orient='records')
    scr_records = []
    for rec in scr_records_raw:
        converted = {k: to_py_type(v) for k, v in rec.items()}
        scr_records.append(converted)

    # Calculate CCC for each row using the provided formulas:
    # DSO = (Avg Receivables / Revenue) * 365
    # DIO = (Avg Inventory / Cost of Revenue) * 365
    # DPO = (Avg Payables / Cost of Revenue) * 365
    # CCC = DSO + DIO - DPO
    der_records = []
    for idx, row in df.iterrows():
        fiscal_year = to_py_type(row.get("Fiscal Year"))
        avg_receivables = row.get("Avg Receivables")
        revenue = row.get("Revenue")
        avg_inventory = row.get("Avg Inventory")
        cost_of_revenue = row.get("Cost of Revenue")
        avg_payables = row.get("Avg Payables")

        # Compute DSO
        if revenue and revenue != 0:
            dso = (avg_receivables / revenue) * 365.0
        else:
            dso = None

        # Compute DIO
        if cost_of_revenue and cost_of_revenue != 0:
            dio = (avg_inventory / cost_of_revenue) * 365.0
        else:
            dio = None

        # Compute DPO
        if cost_of_revenue and cost_of_revenue != 0:
            dpo = (avg_payables / cost_of_revenue) * 365.0
        else:
            dpo = None

        # Compute CCC
        if dso is None or dio is None or dpo is None:
            # If any component is None due to division by zero, set CCC to None
            ccc = None
        else:
            ccc = dso + dio - dpo

        der_rec = {
            "Fiscal Year": fiscal_year,
            INDICATOR_NAME: to_py_type(ccc)
        }
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