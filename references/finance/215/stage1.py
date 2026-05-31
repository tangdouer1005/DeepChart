#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Net Income,Total Assets,Avg Total Assets,CFO per Asset,NI per Asset
2016,15435000000,10508000000,127136000000,128315500000.0,0.1202894428186774,0.0818918992639236
2017,12753000000,15326000000,120406000000,123771000000.0,0.1030370603776328,0.1238254518425156
2018,14867000000,9750000000,118310000000,119358000000.0,0.1245580522461837,0.0816870255868898
2019,15242000000,3897000000,115095000000,116702500000.0,0.1306055997086609,0.0333926008440264
2020,17403000000,13027000000,120700000000,117897500000.0,0.1476112725036578,0.1104942852901885
2021,18371000000,14306000000,119307000000,120003500000.0,0.1530872016232859,0.1192131896153028
2022,16723000000,14742000000,117208000000,118257500000.0,0.1414117497833118,0.1246601695452719
2023,16848000000,14653000000,120829000000,119018500000.0,0.1415578250440057,0.1231153140058058
2024,19846000000,14879000000,122370000000,121599500000.0,0.1632079079272529,0.1223607004963013
"""

def to_py_value(v):
    # Convert numpy/pandas scalars to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    # pandas Timestamp etc not expected here, but handle generically
    try:
        if isinstance(v, (np.bool_, bool)):
            return bool(v)
    except Exception:
        pass
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from hardcoded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows with header keys preserved
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_py_value(row[col])
        scr_records.append(rec)

    # Calculate 盈余-现金质量剪刀差 (Earnings Quality Spread) for each row:
    # Spread = (CFO / Total Assets) - (Net Income / Total Assets)
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = to_py_value(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None
        # Ensure numeric conversion
        cfo = float(row["CFO"]) if not pd.isna(row["CFO"]) else None
        net_income = float(row["Net Income"]) if not pd.isna(row["Net Income"]) else None
        total_assets = float(row["Total Assets"]) if not pd.isna(row["Total Assets"]) else None

        spread_value = None
        if total_assets is not None and total_assets != 0 and cfo is not None and net_income is not None:
            spread_value = (cfo / total_assets) - (net_income / total_assets)
            # convert to native python float
            spread_value = float(spread_value)

        der_rec = {}
        if fiscal_year is not None:
            der_rec["Fiscal Year"] = fiscal_year
        der_rec["盈余-现金质量剪刀差 (Earnings Quality Spread)"] = to_py_value(spread_value)
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()