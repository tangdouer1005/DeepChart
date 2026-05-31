import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Cash & Equiv,Receivables,Operating Expenses,Cost of Revenue,Quick Assets,Daily Burn
2016,18972000000,11699000000,29210000000,21789000000,30671000000,139723287.67123288
2017,17824000000,13490000000,32114000000,25439000000,31314000000,157679452.05479452
2018,18107000000,14098000000,33315000000,27091000000,32205000000,165495890.41095892
2019,17305000000,14481000000,33533000000,27556000000,31786000000,167367123.28767124
2020,13985000000,13576000000,34424000000,28427000000,27561000000,172194520.5479452
2021,14487000000,18984000000,34395000000,23402000000,33471000000,158347945.20547944
2022,12889000000,16915000000,34381000000,24596000000,29804000000,161580821.9178082
2023,21859000000,14873000000,36560000000,26739000000,36732000000,173421917.80821916
2024,24105000000,18927000000,66672000000,27471000000,43032000000,257926027.39726028
"""

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows as list of dicts
    # Convert numeric types to Python native types for JSON serialization
    scr_records = df.to_dict(orient="records")

    # Calculate Defensive Interval Ratio (DIR) for each row:
    # Quick Assets (from CSV) / ((Operating Expenses + Cost of Revenue) / 365)
    dir_name = "防御区间比率 (Defensive Interval Ratio, DIR)"
    der_records = []
    for _, row in df.iterrows():
        quick_assets = float(row["Quick Assets"])
        operating_expenses = float(row["Operating Expenses"])
        cost_of_revenue = float(row["Cost of Revenue"])
        daily_cash_consumption = (operating_expenses + cost_of_revenue) / 365.0

        # Protect against division by zero
        if daily_cash_consumption == 0:
            dir_value = None
        else:
            dir_value = quick_assets / daily_cash_consumption

        der_entry = {
            "Fiscal Year": int(row["Fiscal Year"]) if not pd.isna(row["Fiscal Year"]) else None,
            dir_name: (float(dir_value) if dir_value is not None else None)
        }
        der_records.append(der_entry)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON with ensure_ascii=False to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()