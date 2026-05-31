#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Avg Receivables,Revenue,Avg Inventory,Cost of Revenue,Avg Payables,DSO,DIO,DPO
2016,12894000000.0,90272000000,379500000.0,35138000000,1986000000.0,52.134770471464016,3.942099721099664,20.62980249302749
2017,16468500000.0,110855000000,508500000.0,45583000000,2589000000.0,54.224008840377074,4.071748239475243,20.731083956738257
2018,19949000000.0,136819000000,928000000.0,59549000000,3757500000.0,53.21910699537345,5.688088800819493,23.03124317788712
2019,24342500000.0,161857000000,1053000000.0,71896000000,4969500000.0,54.89421217494456,5.3458467786803165,25.22904612217648
2020,29438000000.0,182527000000,863500000.0,84732000000,5575000000.0,58.86729086655673,3.719698579049237,24.01542510503706
2021,35827000000.0,257637000000,949000000.0,110939000000,5813000000.0,50.75689827159919,3.122301444938209,19.12533013638125
2022,40264000000.0,282836000000,1920000000.0,126203000000,5582500000.0,51.96071221485242,5.5529583290413065,16.14551555826724
"""

INDICATOR_NAME = "现金循环周期 (Cash Conversion Cycle, CCC)"

def make_json_serializable(obj):
    # Convert numpy / pandas scalar types to native Python types recursively for JSON serialization
    if isinstance(obj, dict):
        return {make_json_serializable(k): make_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [make_json_serializable(i) for i in obj]
    if isinstance(obj, (np.generic,)):
        return obj.item()
    if pd.isna(obj):
        return None
    return obj

def compute_ccc(row):
    # Compute DSO, DIO, DPO from raw inputs and then CCC
    # DSO = (Avg Receivables / Revenue) * 365
    # DIO = (Avg Inventory / Cost of Revenue) * 365
    # DPO = (Avg Payables / Cost of Revenue) * 365
    # CCC = DSO + DIO - DPO
    # Protect against division by zero
    receivables = row.get("Avg Receivables", 0)
    revenue = row.get("Revenue", 0)
    inventory = row.get("Avg Inventory", 0)
    cost_of_revenue = row.get("Cost of Revenue", 0)
    payables = row.get("Avg Payables", 0)

    dso = (receivables / revenue) * 365 if revenue not in (0, None, np.nan) else None
    dio = (inventory / cost_of_revenue) * 365 if cost_of_revenue not in (0, None, np.nan) else None
    dpo = (payables / cost_of_revenue) * 365 if cost_of_revenue not in (0, None, np.nan) else None

    if dso is None or dio is None or dpo is None:
        ccc = None
    else:
        ccc = dso + dio - dpo

    return {
        "DSO": dso,
        "DIO": dio,
        "DPO": dpo,
        "CCC": ccc
    }

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data as list of dicts using original CSV headers
    scr_records = df.to_dict(orient="records")
    scr_records = [make_json_serializable(r) for r in scr_records]

    # Compute derived CCC for each row
    der_records = []
    for idx, row in df.iterrows():
        row_dict = row.to_dict()
        metrics = compute_ccc(row_dict)
        # Build output dict: include Fiscal Year if present
        der_entry = {}
        if "Fiscal Year" in row_dict:
            # Ensure native python int if possible
            fy = row_dict["Fiscal Year"]
            if isinstance(fy, (np.generic,)):
                fy = fy.item()
            der_entry["Fiscal Year"] = fy
        der_entry[INDICATOR_NAME] = make_json_serializable(metrics["CCC"])
        # Optionally include intermediate days (not required, but keep output focused)
        der_records.append(make_json_serializable(der_entry))

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()