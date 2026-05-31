#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Net Income,Operating Cashflow,Accruals,Avg Total Assets
2016,186678000,-1473984000,1660662000,11894740500.0
2017,558929000,-1785948000,2344877000,16299676000.0
2018,1211242000,-2680479000,3891721000,22493571000.0
2019,1866916000,-2887322000,4754238000,29975056000.0
2020,2761395000,2427077000,334318000,36628035500.0
2021,5116228000,392610000,4723618000,41932511000.0
2022,4491924000,2026257000,2465667000,46589715500.0
2023,5407990000,7274301000,-1866311000,48663380000.0
2024,8711631000,7361364000,1350267000,51181183000.0
"""

INDICATOR_NAME = "斯隆比率 (Sloan Ratio / Accruals Ratio)"

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from hardcoded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric types
    # Columns: Fiscal Year, Net Income, Operating Cashflow, Accruals, Avg Total Assets
    # Compute accruals dynamically per reference: Accruals = Net Income - Operating Cashflow
    df["Computed Accruals"] = df["Net Income"] - df["Operating Cashflow"]

    # Use Avg Total Assets as denominator (as provided)
    # Compute Sloan Ratio = Accruals / Avg Total Assets
    # Use the computed accruals to derive the indicator dynamically
    df[INDICATOR_NAME] = df["Computed Accruals"] / df["Avg Total Assets"]

    # Prepare scr_data: original CSV rows as list of dicts (use original column names)
    scr_records = df[["Fiscal Year", "Net Income", "Operating Cashflow", "Accruals", "Avg Total Assets"]].to_dict(orient="records")

    # Prepare der_data: for each row, include Fiscal Year and calculated indicator
    der_records = []
    for _, row in df.iterrows():
        # Extract fiscal year value
        fiscal_year = int(row["Fiscal Year"]) if pd.notna(row["Fiscal Year"]) else None
        value = None
        if pd.notna(row[INDICATOR_NAME]):
            # Convert to native Python float for JSON serialization
            value = float(row[INDICATOR_NAME])
        der_records.append({
            "Fiscal Year": fiscal_year,
            INDICATOR_NAME: value
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