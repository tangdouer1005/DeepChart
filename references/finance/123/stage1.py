#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Operating Income,Income Tax,Pretax Income,Effective Tax Rate,NOPAT,Avg Invested Capital
2016,8657000000,1586000000,8136000000,0.1949360865290068,6969438298.918387,61336500000.0
2017,7755000000,5607000000,6890000000,0.8137880986937591,1444073294.629898,59483500000.0
2018,9152000000,1749000000,8225000000,0.212644376899696,7205878662.613981,55428500000.0
2019,10086000000,1801000000,10786000000,0.166975709252735,8401882996.476914,53825500000.0
2020,8997000000,1981000000,9749000000,0.2032003282387937,7168806646.835572,55582000000.0
2021,10308000000,2621000000,12425000000,0.2109456740442656,8133571991.951711,56002500000.0
2022,10909000000,2115000000,11686000000,0.1809857949683382,8934625962.6904,55231000000.0
2023,11311000000,2249000000,12952000000,0.1736411365040148,9346945105.003088,56538000000.0
2024,9992000000,2437000000,13086000000,0.1862295583065872,8131194253.400581,58920000000.0
"""

INDICATOR_KEY = "投入资本回报率 (Return on Invested Capital, ROIC)"

def to_native_python(val):
    """Convert pandas/numpy types to native Python types for JSON serialization."""
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer, np.int64, np.int32)):
        return int(val)
    if isinstance(val, (np.floating, np.float64, np.float32)):
        return float(val)
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: mirror input CSV rows
    scr_data = []
    for _, row in df.iterrows():
        record = {}
        for col in df.columns:
            record[col] = to_native_python(row[col])
        scr_data.append(record)

    # Calculate ROIC for each row dynamically using:
    # NOPAT = Operating Income * (1 - Effective Tax Rate)
    # Invested Capital = Avg Invested Capital (from CSV)
    der_data = []
    for _, row in df.iterrows():
        # Extract raw inputs
        operating_income = row.get("Operating Income")
        effective_tax_rate = row.get("Effective Tax Rate")
        invested_capital = row.get("Avg Invested Capital")  # using provided average invested capital

        # Convert to native numeric types where needed
        try:
            op_inc = float(operating_income) if not pd.isna(operating_income) else None
        except Exception:
            op_inc = None
        try:
            tax_rate = float(effective_tax_rate) if not pd.isna(effective_tax_rate) else None
        except Exception:
            tax_rate = None
        try:
            inv_cap = float(invested_capital) if not pd.isna(invested_capital) else None
        except Exception:
            inv_cap = None

        # Compute NOPAT dynamically per reference: Operating Income * (1 - Effective Tax Rate)
        if op_inc is None or tax_rate is None:
            nopat_calc = None
        else:
            nopat_calc = op_inc * (1.0 - tax_rate)

        # Compute ROIC = NOPAT / Invested Capital
        if nopat_calc is None or inv_cap in (None, 0):
            roic = None
        else:
            roic = nopat_calc / inv_cap

        # Assemble derived record; include Fiscal Year if present
        derived_record = {}
        if "Fiscal Year" in df.columns:
            fy = row.get("Fiscal Year")
            derived_record["Fiscal Year"] = to_native_python(fy)
        derived_record[INDICATOR_KEY] = to_native_python(roic)
        der_data.append(derived_record)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()