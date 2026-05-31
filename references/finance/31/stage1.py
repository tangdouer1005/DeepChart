#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Avg Receivables,Revenue,Avg Inventory,Cost of Revenue,Avg Payables,DSO,DIO,DPO
2016,6996500000.0,135987000000,10852000000.0,121969000000,22853000000.0,18.77916639090501,32.47530110109946,68.38905787536177
2017,10751500000.0,177866000000,13754000000.0,111934000000,29962500000.0,22.063224562310957,44.849732878303286,97.70322243464898
2018,14920500000.0,232887000000,16610500000.0,139156000000,36404000000.0,23.38465650723312,43.568602862973925,95.48607318405244
2019,18746500000.0,280522000000,18835500000.0,165536000000,42687500000.0,24.39192826231098,41.53149465977189,94.12416332398992
2020,22679000000.0,386064000000,22146000000.0,233307000000,59861000000.0,21.44161330763811,34.646581542774115,93.650276245462
2021,28716500000.0,469822000000,28217500000.0,272344000000,75601500000.0,22.30956085496209,37.81756712099404,101.32239924507242
2022,37625500000.0,513983000000,33522500000.0,288831000000,79132000000.0,26.719380796641133,42.362878292150086,100.00027697857917
2023,47306500000.0,574785000000,33861500000.0,304739000000,82290500000.0,30.040576041476378,40.55748525787641,98.56313927656126
2024,53852000000.0,637959000000,33766000000.0,326288000000,89672000000.0,30.810726081143144,37.772121561320056,100.31101358309223
"""

INDICATOR_NAME = "现金循环周期 (Cash Conversion Cycle, CCC)"

def ensure_native(obj):
    """
    Recursively convert numpy / pandas scalar types to native Python types so json can serialize them.
    """
    if isinstance(obj, dict):
        return {ensure_native(k): ensure_native(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [ensure_native(x) for x in obj]
    if pd.isna(obj):
        return None
    # numpy types
    if isinstance(obj, (np.integer, )):
        return int(obj)
    if isinstance(obj, (np.floating, )):
        return float(obj)
    if isinstance(obj, (np.bool_, )):
        return bool(obj)
    # pandas Timestamp
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    return obj

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Keep original scraped data for output (as native types)
    scr_df = df.copy()

    # Implement calculation logic for CCC based on reference:
    # DSO = (Avg Receivables / Revenue) * 365
    # DIO = (Avg Inventory / Cost of Revenue) * 365
    # DPO = (Avg Payables / Cost of Revenue) * 365
    # CCC = DSO + DIO - DPO
    # Perform calculations row-wise (vectorized)
    # Guard against division by zero
    revenue = df['Revenue'].astype(float)
    cost_of_revenue = df['Cost of Revenue'].astype(float)

    # Compute DSO, DIO, DPO using the provided raw balance / flow items
    dso = (df['Avg Receivables'].astype(float) / revenue.replace({0: np.nan})) * 365.0
    dio = (df['Avg Inventory'].astype(float) / cost_of_revenue.replace({0: np.nan})) * 365.0
    dpo = (df['Avg Payables'].astype(float) / cost_of_revenue.replace({0: np.nan})) * 365.0

    ccc = dso + dio - dpo

    # Prepare scr_data and der_data for JSON output
    scr_records = scr_df.to_dict(orient='records')
    scr_records = [ensure_native(rec) for rec in scr_records]

    der_records = []
    for idx, row in df.iterrows():
        year_val = ensure_native(row['Fiscal Year'])
        ccc_val = ensure_native(float(ccc.iloc[idx]) if not pd.isna(ccc.iloc[idx]) else None)
        der_records.append({
            "Fiscal Year": year_val,
            INDICATOR_NAME: ccc_val
        })

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to specified output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()