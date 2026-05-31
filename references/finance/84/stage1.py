#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Avg Total Equity,Dividends,ROE(Avg),Retention Ratio
2016,7500000000,87050000000.0,8806000000,0.0861573808156232,-0.1741333333333332
2017,-8484000000,65915000000.0,8650000000,-0.1287112189941591,2.01956624233852
2018,-22355000000,43515000000.0,4474000000,-0.513730897391704,1.2001341981659583
2019,-4979000000,29650000000.0,649000000,-0.1679258010118043,1.130347459329183
2020,5704000000,31926000000.0,648000000,0.1786631585541565,0.8863955119214586
2021,-6337000000,37931000000.0,575000000,-0.1670665155150141,1.090736941770554
2022,292000000,37003000000.0,639000000,0.0078912520606437,-1.1883561643835616
2023,9482000000,30549500000.0,589000000,0.3103815119723727,0.9378823033115375
2024,6556000000,23372500000.0,1008000000,0.2805005882982137,0.8462477120195241
"""

INDICATOR_NAME = "可持续增长率 (Sustainable Growth Rate, SGR)"

def to_py_val(x):
    # Convert numpy and pandas scalar types to native Python types for JSON serialization
    if x is None:
        return None
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        # convert nan to None
        if np.isnan(x):
            return None
        return float(x)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    # pandas NA (pd.NA) handling
    try:
        if pd.isna(x):
            return None
    except Exception:
        pass
    return x

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA), sep=",")
    # Preserve original scraped data (scr_data) as list of dicts with native types
    raw_records = []
    for rec in df.to_dict(orient="records"):
        converted = {k: to_py_val(v) for k, v in rec.items()}
        raw_records.append(converted)

    der_records = []
    # Calculation per reference:
    # Retention Ratio (b) = 1 - (Dividends / Net Income)
    # ROE = Net Income / Avg Total Equity
    # SGR = ROE * Retention Ratio
    for idx, row in df.iterrows():
        ni = row.get("Net Income")
        div = row.get("Dividends")
        avg_eq = row.get("Avg Total Equity")

        # Initialize values safely
        sgr_value = None

        # Compute retention ratio, handle division by zero
        retention = None
        try:
            if ni == 0 or pd.isna(ni):
                retention = None
            else:
                retention = 1.0 - (div / ni)
        except Exception:
            retention = None

        # Compute ROE (using Net Income / Avg Total Equity), handle division by zero
        roe = None
        try:
            if avg_eq == 0 or pd.isna(avg_eq):
                roe = None
            else:
                roe = ni / avg_eq
        except Exception:
            roe = None

        # Compute SGR if both components available
        if (retention is not None) and (roe is not None):
            try:
                sgr_value = roe * retention
            except Exception:
                sgr_value = None

        # Prepare output entry; include Fiscal Year if present
        entry = {}
        if "Fiscal Year" in df.columns:
            entry["Fiscal Year"] = to_py_val(row["Fiscal Year"])
        entry[INDICATOR_NAME] = to_py_val(sgr_value)
        # Optionally include intermediate computed values for traceability (not required, so omitted)
        der_records.append(entry)

    output = {
        "scr_data": raw_records,
        "der_data": der_records
    }

    # Write JSON with ensure_ascii=False to keep Chinese readable
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()