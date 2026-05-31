#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,CFO,Net Income,Total Assets,Avg Total Assets,CFO per Asset,NI per Asset
2016,1160000000,7500000000,365200000000,429150000000.0,0.0027030175929162,0.0174764068507514
2017,6554000000,-8484000000,382615000000,373907500000.0,0.0175283994035958,-0.0226901038358417
2018,4978000000,-22355000000,309100000000,345857500000.0,0.0143932110768163,-0.064636447091649
2019,8772000000,-4979000000,266000000000,287550000000.0,0.0305059989567031,-0.0173152495218222
2020,3597000000,5704000000,256211000000,261105500000.0,0.0137760407191729,0.0218455758304593
2021,3332000000,-6337000000,198874000000,227542500000.0,0.0146434182625223,-0.0278497423558236
2022,5916000000,292000000,188851000000,193862500000.0,0.0305164743052421,0.001506222193565
2023,5179000000,9482000000,176106000000,182478500000.0,0.0283814257570069,0.0519622859679359
2024,4710000000,6556000000,125761000000,150933500000.0,0.0312057959299956,0.0434363477955523
"""

INDICATOR_NAME = "盈余-现金质量剪刀差 (Earnings Quality Spread)"

def to_py_value(v):
    # Convert pandas/numpy scalar types to native Python types for JSON serialization
    if pd.isna(v):
        return None
    try:
        return v.item()
    except Exception:
        return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Build scr_data: list of dicts reflecting the original CSV rows with native Python types
    scr_data = []
    for _, row in df.iterrows():
        row_dict = {}
        for col in df.columns:
            row_dict[col] = to_py_value(row[col])
        scr_data.append(row_dict)

    # Calculate Earnings Quality Spread for each row:
    # Spread = (CFO / Total Assets) - (Net Income / Total Assets)
    der_data = []
    for _, row in df.iterrows():
        fiscal_year = to_py_value(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None

        cfo = row.get("CFO", None)
        ni = row.get("Net Income", None)
        total_assets = row.get("Total Assets", None)

        # Convert to Python numbers if possible
        cfo_py = None if pd.isna(cfo) else float(cfo)
        ni_py = None if pd.isna(ni) else float(ni)
        ta_py = None if pd.isna(total_assets) else float(total_assets)

        spread_value = None
        if ta_py is not None and ta_py != 0.0 and cfo_py is not None and ni_py is not None:
            spread_value = (cfo_py / ta_py) - (ni_py / ta_py)
            # keep as Python float
        else:
            spread_value = None

        entry = {}
        if fiscal_year is not None:
            entry["Fiscal Year"] = fiscal_year
        entry[INDICATOR_NAME] = to_py_value(spread_value)
        der_data.append(entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to the specified file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()