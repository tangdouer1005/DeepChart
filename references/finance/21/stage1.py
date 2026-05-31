#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Cash & Equiv,Receivables,Operating Expenses,Cost of Revenue,Quick Assets,Daily Burn
2016,4905609000,6222399000,5466982000,24520234000,11128008000,82156756.16438356
2017,4126860000,6885257000,5880090000,25105349000,11012117000,84891613.69863014
2018,5061360000,7496368000,6594585000,28499170000,12557728000,96147273.97260274
2019,6126853000,8095071000,7009614000,29900325000,14221924000,101123120.5479452
2020,8415330000,7846892000,7462514000,30350881000,16262222000,103598342.46575342
2021,8168174000,9728212000,8742599000,34169261000,17896386000,117566739.7260274
2022,7889833000,11776775000,10334358000,41892766000,19666608000,143088010.95890412
2023,9045032000,12227186000,11921718000,43380138000,21272218000,151511934.24657536
2024,5004469000,13664847000,11566470000,43734147000,18669316000,151508539.7260274
"""

INDICATOR_NAME = "防御区间比率 (Defensive Interval Ratio, DIR)"

def to_native(val):
    if pd.isna(val):
        return None
    # convert numpy types to native python types
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: represent original CSV rows with native Python types
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_data.append(rec)

    # Compute DIR for each row.
    # Formula:
    # Quick Assets = Cash + Receivables + Trading Financial Assets  (if available)
    # Daily cash consumption = (Operating Expenses + Cost of Revenue) / 365
    # DIR = Quick Assets / Daily cash consumption
    der_data = []
    for _, row in df.iterrows():
        fiscal_year = to_native(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None

        # Use Quick Assets column if present; otherwise calculate from components if available.
        if "Quick Assets" in df.columns and not pd.isna(row["Quick Assets"]):
            quick_assets = float(row["Quick Assets"])
        else:
            # attempt to compute from cash + receivables + trading financial assets if those exist
            qa_components = []
            for comp in ["Cash & Equiv", "Receivables", "Trading Financial Assets"]:
                if comp in df.columns and not pd.isna(row.get(comp, np.nan)):
                    qa_components.append(float(row[comp]))
            quick_assets = float(sum(qa_components)) if qa_components else None

        # Calculate daily cash consumption
        oe = float(row["Operating Expenses"]) if "Operating Expenses" in df.columns and not pd.isna(row["Operating Expenses"]) else None
        cor = float(row["Cost of Revenue"]) if "Cost of Revenue" in df.columns and not pd.isna(row["Cost of Revenue"]) else None

        daily_cash_consumption = None
        if oe is not None and cor is not None:
            daily_cash_consumption = (oe + cor) / 365.0

        # Calculate DIR safely
        dir_value = None
        if quick_assets is not None and daily_cash_consumption not in (None, 0):
            dir_value = quick_assets / daily_cash_consumption

        rec = {}
        if fiscal_year is not None:
            rec["Fiscal Year"] = fiscal_year
        rec[INDICATOR_NAME] = to_native(dir_value) if dir_value is not None else None
        der_data.append(rec)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()