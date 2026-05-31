#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,NOPAT,Avg Invested Capital,WACC,Capital Charge
2016,2653356115.107913,9404500000.0,0.1,940450000.0
2017,2425193904.3615346,25477000000.0,0.1,2547700000.0
2018,10927523932.155226,41454000000.0,0.1,4145400000.0
2019,12071027618.775042,47742500000.0,0.1,4774250000.0
2020,20187450781.702374,74951000000.0,0.1,7495100000.0
2021,21754696862.467564,132952500000.0,0.1,13295250000.0
2022,12248000000.0,170425500000.0,0.1,17042550000.0
2023,29865652847.67153,189953000000.0,0.1,18995300000.0
2024,59317181615.16792,232856000000.0,0.1,23285600000.0
"""

INDICATOR_NAME = "经济增加值 (Economic Value Added, EVA) - 简化版"

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure required columns exist
    required_cols = {"Fiscal Year", "NOPAT", "Avg Invested Capital", "WACC"}
    if not required_cols.issubset(set(df.columns)):
        missing = required_cols - set(df.columns)
        raise ValueError(f"Missing required columns in CSV data: {missing}")

    # Calculation:
    # EVA = NOPAT - (Invested Capital * WACC)
    # Use Avg Invested Capital as Invested Capital in this simplified model
    invested_capital = df["Avg Invested Capital"].astype(float)
    wacc = df["WACC"].astype(float)
    nopat = df["NOPAT"].astype(float)

    capital_charge = invested_capital * wacc
    eva = nopat - capital_charge

    # Prepare scr_data (original rows) and der_data (derived EVA values)
    # Convert scr_data to list of plain Python dicts
    scr_data = df.to_dict(orient="records")

    der_data = []
    for idx, row in df.iterrows():
        fiscal_year = row["Fiscal Year"]
        eva_value = float(eva.iloc[idx])
        der_entry = {
            "Fiscal Year": int(fiscal_year) if pd.notna(fiscal_year) and float(fiscal_year).is_integer() else fiscal_year,
            INDICATOR_NAME: eva_value
        }
        der_data.append(der_entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to the specified file with non-ASCII characters preserved
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()