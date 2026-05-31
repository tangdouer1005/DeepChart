#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Operating Income,Income Tax,Pretax Income,Effective Tax Rate,NOPAT,Avg Invested Capital
2016,5499000000,718000000,4659000000,0.1541103241038849,4651547327.752737,60539500000.0
2017,6797000000,4103000000,6521000000,0.6291979757705873,2520341358.687318,55534500000.0
2018,8931000000,2508000000,8701000000,0.2882427307206068,6356704171.93426,48252000000.0
2019,7926000000,1565000000,7171000000,0.2182401338725421,6196228698.92623,43213500000.0
2020,5548000000,1340000000,5863000000,0.228551935869009,4279993859.798738,45963000000.0
2021,13199000000,1521000000,13879000000,0.1095900281000072,11752521219.108006,56421500000.0
2022,18282000000,1918000000,16444000000,0.1166382875212843,16149618827.53588,63881500000.0
2023,2954000000,1512000000,1889000000,0.8004235044997353,589548967.7077819,65174500000.0
2024,20221000000,2803000000,19936000000,0.1405999197431781,17377929022.87319,68272000000.0
"""

INDICATOR_NAME = "投入资本回报率 (Return on Invested Capital, ROIC)"

def to_native_value(v):
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data (original/raw data) as list of dicts with native python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native_value(row[col])
        scr_records.append(rec)

    # Calculation for ROIC:
    # NOPAT = Operating Income * (1 - Effective Tax Rate)
    # Invested Capital = Avg Invested Capital (provided in CSV)
    # ROIC = NOPAT / Invested Capital
    roic_list = []
    for _, row in df.iterrows():
        fiscal_year = to_native_value(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None

        # Read raw inputs
        operating_income = row.get("Operating Income", np.nan)
        effective_tax_rate = row.get("Effective Tax Rate", np.nan)
        invested_capital = row.get("Avg Invested Capital", np.nan)

        # Compute NOPAT from Operating Income and Effective Tax Rate
        # Note: We intentionally compute NOPAT here rather than using the provided NOPAT column,
        # to follow the reference calculation method.
        try:
            nopat = float(operating_income) * (1.0 - float(effective_tax_rate))
        except Exception:
            nopat = None

        # Compute ROIC with basic safety checks
        roic_value = None
        try:
            if nopat is None or invested_capital is None or invested_capital == 0 or np.isnan(invested_capital):
                roic_value = None
            else:
                roic_value = float(nopat) / float(invested_capital)
        except Exception:
            roic_value = None

        entry = {}
        if fiscal_year is not None:
            entry["Fiscal Year"] = fiscal_year
        entry[INDICATOR_NAME] = to_native_value(roic_value) if roic_value is not None else None
        roic_list.append(entry)

    output_obj = {
        "scr_data": scr_records,
        "der_data": roic_list
    }

    # Write JSON output
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()