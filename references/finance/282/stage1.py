import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Cash & Equiv,Receivables,Operating Expenses,Cost of Revenue,Quick Assets,Daily Burn
2016,3657000000,21394000000,40930000000,156927000000,25051000000,542073972.6027397
2017,3177000000,25597000000,42543000000,180800000000,28774000000,611898630.1369863
2018,3042000000,24701000000,45609000000,211599000000,27743000000,704679452.0547945
2019,3089000000,26966000000,43192000000,199625000000,30055000000,665252054.7945205
2020,4364000000,20581000000,37575000000,170447000000,24945000000,569923287.6712328
2021,6802000000,32383000000,40867000000,211806000000,39185000000,692254794.520548
2022,29640000000,41749000000,39039000000,295608000000,71389000000,916841095.8904108
2023,31539000000,38015000000,39681000000,250555000000,69554000000,795167123.2876712
2024,23029000000,43681000000,37090000000,262505000000,66710000000,820808219.1780822
"""

def to_native(obj):
    # convert numpy types to native python types for JSON serialization
    if pd.isna(obj):
        return None
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    return obj

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: list of dictionaries with original CSV headers
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Calculate Defensive Interval Ratio (DIR) for each row
    # Formula:
    # Quick Assets = Cash + Receivables + Trading Financial Assets
    # Daily Cash Consumption = (Operating Expenses + Cost of Revenue) / 365
    # DIR = Quick Assets / Daily Cash Consumption
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = to_native(row["Fiscal Year"])
        quick_assets = float(row["Quick Assets"])
        operating_expenses = float(row["Operating Expenses"])
        cost_of_revenue = float(row["Cost of Revenue"])
        daily_cash_consumption = (operating_expenses + cost_of_revenue) / 365.0

        # Protect against division by zero
        if daily_cash_consumption == 0:
            dir_value = None
        else:
            dir_value = quick_assets / daily_cash_consumption

        # Convert to native float if not None
        dir_value = None if dir_value is None else float(dir_value)

        der_records.append({
            "Fiscal Year": fiscal_year,
            "防御区间比率 (Defensive Interval Ratio, DIR)": dir_value
        })

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to specified file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()