#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Avg Receivables,Revenue,Avg Inventory,Cost of Revenue,Avg Payables,DSO,DIO,DPO
2016,20634500000.0,200628000000,15662500000.0,156927000000,17937500000.0,37.54008662798812,36.42975714822816,41.72123025355739
2017,23495500000.0,237162000000,16036000000.0,180800000000,19751000000.0,36.16033555122659,32.373561946902655,39.873423672566375
2018,25149000000.0,279332000000,17975000000.0,211599000000,21382000000.0,32.86191700199046,31.0061720518528,36.8831138143375
2019,25833500000.0,255583000000,18743000000.0,199625000000,22878500000.0,36.89301518489101,34.270231684408266,41.83169693174703
2020,23773500000.0,178574000000,18689000000.0,170447000000,21096500000.0,48.59233427038651,40.02115026958526,45.17663848586364
2021,26482000000.0,276692000000,18815000000.0,211806000000,22061000000.0,34.933897619013194,32.42342048856028,38.01717137380433
2022,37066000000.0,398675000000,21607500000.0,295608000000,29896000000.0,33.935135135135134,26.679716042867582,36.91388595707829
2023,39882000000.0,334697000000,24777500000.0,250555000000,32209000000.0,43.49286070684828,36.09501905769193,46.92097543453533
2024,40848000000.0,339247000000,24322000000.0,262505000000,33697000000.0,43.94886321765557,33.81851774251919,46.85398373364316
"""

INDICATOR_NAME = "现金循环周期 (Cash Conversion Cycle, CCC)"

def to_native(obj):
    # Convert numpy types to native Python types and handle NaN
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.bool_ ,)):
        return bool(obj)
    if pd.isna(obj):
        return None
    return obj

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows, convert numpy types to native Python types
    scr_records = []
    for rec in df.to_dict(orient="records"):
        nat = {k: to_native(v) for k, v in rec.items()}
        scr_records.append(nat)

    # Calculate CCC for each row dynamically using formulas:
    # DSO = (Avg Receivables / Revenue) * 365
    # DIO = (Avg Inventory / Cost of Revenue) * 365
    # DPO = (Avg Payables / Cost of Revenue) * 365
    # CCC = DSO + DIO - DPO
    der_records = []
    for _, row in df.iterrows():
        # Safely extract numeric values
        avg_receivables = float(row["Avg Receivables"]) if not pd.isna(row["Avg Receivables"]) else None
        revenue = float(row["Revenue"]) if not pd.isna(row["Revenue"]) else None
        avg_inventory = float(row["Avg Inventory"]) if not pd.isna(row["Avg Inventory"]) else None
        cost_of_revenue = float(row["Cost of Revenue"]) if not pd.isna(row["Cost of Revenue"]) else None
        avg_payables = float(row["Avg Payables"]) if not pd.isna(row["Avg Payables"]) else None

        # Initialize computed components as None; compute only if denominators valid and non-zero
        dso = None
        dio = None
        dpo = None
        ccc = None

        if revenue and revenue != 0 and avg_receivables is not None:
            dso = (avg_receivables / revenue) * 365.0
        if cost_of_revenue and cost_of_revenue != 0 and avg_inventory is not None:
            dio = (avg_inventory / cost_of_revenue) * 365.0
        if cost_of_revenue and cost_of_revenue != 0 and avg_payables is not None:
            dpo = (avg_payables / cost_of_revenue) * 365.0

        # Compute CCC only if we have the needed components (DSO and DIO at least; DPO can be zero)
        if dso is not None and dio is not None and dpo is not None:
            ccc = dso + dio - dpo
        else:
            # If any component is missing, leave as None
            ccc = None

        der_entry = {
            "Fiscal Year": to_native(row["Fiscal Year"]),
            INDICATOR_NAME: to_native(ccc)
        }
        der_records.append(der_entry)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON with Chinese characters preserved
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()