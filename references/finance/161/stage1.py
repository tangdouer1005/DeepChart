#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Avg Receivables,Revenue,Avg Inventory,Cost of Revenue,Avg Payables,DSO,DIO,DPO
2016,6751000000.0,39807000000,4783000000.0,14030000000,2670000000.0,61.90154997864697,124.4330007127584,69.46186742694228
2017,6945500000.0,40122000000,4981000000.0,12912000000,2954500000.0,63.18497333133941,140.80429058240398,83.5186260842627
2018,6972000000.0,42294000000,5268000000.0,13509000000,3210000000.0,60.16881827209533,142.3362202975794,86.73106817677105
2019,6924500000.0,39121000000,5709000000.0,12016000000,3528000000.0,64.60577439227013,173.41752663115847,107.1671105193076
2020,6790500000.0,41518000000,5766000000.0,13618000000,4032500000.0,59.69778168505227,154.54472022323395,108.08213394037304
2021,8016500000.0,48704000000,5753500000.0,13626000000,4468000000.0,60.077663025624176,154.11914721855277,119.68442683105827
2022,9340000000.0,59283000000,5932000000.0,17411000000,4436500000.0,57.50552434930757,124.35701567974267,93.0057147780139
2023,9899500000.0,60115000000,6134500000.0,16126000000,4093000000.0,60.10675372203277,138.84983876968872,92.64200669725908
2024,10313500000.0,64168000000,6233500000.0,15193000000,4000500000.0,58.665183580600925,149.75498584874614,96.1088988349898
"""

def to_native(value):
    # Convert pandas/numpy scalar types and NaN to JSON-serializable Python native types
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer, np.int64, np.int32)):
        return int(value)
    if isinstance(value, (np.floating, np.float64, np.float32)):
        return float(value)
    if isinstance(value, (np.bool_)):
        return bool(value)
    # fallback for other types (including Python native types)
    return value

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))
    # Build scr_data preserving original column names and converting to native types
    scr_records_raw = df.to_dict(orient='records')
    scr_records = []
    for rec in scr_records_raw:
        conv = {k: to_native(v) for k, v in rec.items()}
        scr_records.append(conv)

    der_records = []
    # Compute CCC for each row using formulas:
    # DSO = (Avg Receivables / Revenue) * 365
    # DIO = (Avg Inventory / Cost of Revenue) * 365
    # DPO = (Avg Payables / Cost of Revenue) * 365
    # CCC = DSO + DIO - DPO
    for idx, row in df.iterrows():
        fy = to_native(row.get("Fiscal Year"))
        # Safely extract denominators and handle division-by-zero
        revenue = row.get("Revenue")
        cost_of_revenue = row.get("Cost of Revenue")

        dso = None
        dio = None
        dpo = None
        ccc = None

        try:
            if revenue and revenue != 0:
                dso = (row.get("Avg Receivables", 0.0) / revenue) * 365.0
            else:
                dso = None
        except Exception:
            dso = None

        try:
            if cost_of_revenue and cost_of_revenue != 0:
                dio = (row.get("Avg Inventory", 0.0) / cost_of_revenue) * 365.0
                dpo = (row.get("Avg Payables", 0.0) / cost_of_revenue) * 365.0
            else:
                dio = None
                dpo = None
        except Exception:
            dio = None
            dpo = None

        if dso is None or dio is None or dpo is None:
            ccc = None
        else:
            # compute CCC
            ccc = dso + dio - dpo

        der_entry = {
            "Fiscal Year": fy,
            "现金循环周期 (Cash Conversion Cycle, CCC)": to_native(ccc)
        }
        der_records.append(der_entry)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()