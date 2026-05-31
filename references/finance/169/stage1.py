import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,NOPAT,Avg Invested Capital,WACC,Capital Charge
2016,4651547327.752737,60539500000.0,0.1,6053950000.0
2017,2520341358.687318,55534500000.0,0.1,5553450000.0
2018,6356704171.93426,48252000000.0,0.1,4825200000.0
2019,6196228698.92623,43213500000.0,0.1,4321350000.0
2020,4279993859.798738,45963000000.0,0.1,4596300000.0
2021,11752521219.108006,56421500000.0,0.1,5642150000.0
2022,16149618827.53588,63881500000.0,0.1,6388150000.0
2023,589548967.7077819,65174500000.0,0.1,6517450000.0
2024,17377929022.87319,68272000000.0,0.1,6827200000.0
"""

INDICATOR_NAME = "经济增加值 (Economic Value Added, EVA) - 简化版"

def to_python_native(value):
    # Convert numpy types to native Python types for JSON serialization
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if pd.isna(value):
        return None
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: raw data records with native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_native(row[col])
        scr_records.append(rec)

    # Calculate EVA for each row dynamically:
    # EVA = NOPAT - (Avg Invested Capital * WACC)
    der_records = []
    for _, row in df.iterrows():
        nopat = float(row["NOPAT"])
        invested_capital = float(row["Avg Invested Capital"])
        wacc = float(row["WACC"])
        eva = nopat - (invested_capital * wacc)

        rec = {
            "Fiscal Year": to_python_native(row["Fiscal Year"]),
            INDICATOR_NAME: to_python_native(eva)
        }
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()