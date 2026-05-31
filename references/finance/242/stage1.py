#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Operating Income,Income Tax,Pretax Income,Effective Tax Rate,NOPAT,Avg Invested Capital
2016,-667340000,26698000,-746348000,0.0,-667340000.0,5592036500.0
2017,-1632000000,32000000,-2209000000,0.0,-1632000000.0,9933733000.0
2018,-388000000,58000000,-1005000000,0.0,-388000000.0,12309583000.0
2019,-69000000,110000000,-665000000,0.0,-69000000.0,13674836000.0
2020,1994000000,292000000,1154000000,0.2530329289428076,1489452339.6880417,14431500000.0
2021,6687000000,699000000,6343000000,0.1102002207157496,5950091124.073782,16661000000.0
2022,13656000000,1132000000,13719000000,0.082513302718857,12529198338.07129,24961500000.0
2023,8891000000,5001000000,9973000000,0.5014539255991176,4432573147.498245,41715000000.0
2024,7076000000,1837000000,8990000000,0.2043381535038932,5630103225.806451,58767500000.0
"""

INDICATOR_NAME = "投入资本回报率 (Return on Invested Capital, ROIC)"

def to_native(value):
    """Convert numpy/pandas scalar types to native Python types for JSON serialization."""
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        # Convert to Python float
        return float(value)
    # For normal python numeric types or strings
    if isinstance(value, (int, float, str, bool)):
        return value
    # Fallback: try to convert to float then to str
    try:
        return float(value)
    except Exception:
        return str(value)

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: convert each row to dict with native types
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_data.append(rec)

    # Calculate ROIC for each row:
    # Per reference: NOPAT = Operating Income * (1 - Effective Tax Rate)
    # Invested Capital = Avg Invested Capital (provided in CSV as a raw input)
    # ROIC = NOPAT / Invested Capital
    der_data = []
    for _, row in df.iterrows():
        fiscal = to_native(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None

        # Read raw inputs
        op_income = row.get("Operating Income", None)
        eff_tax = row.get("Effective Tax Rate", None)
        invested_cap = row.get("Avg Invested Capital", None)

        # Defensive checks and conversions
        op_income_val = None if pd.isna(op_income) else float(op_income)
        eff_tax_val = 0.0 if pd.isna(eff_tax) else float(eff_tax)
        invested_cap_val = None if pd.isna(invested_cap) else float(invested_cap)

        # Compute NOPAT dynamically
        # If Operating Income is missing but a NOPAT column exists, prefer computing from Operating Income per reference.
        if op_income_val is None:
            # fallback: try to use provided NOPAT column if present
            nopat_val = None
            if "NOPAT" in df.columns and not pd.isna(row["NOPAT"]):
                nopat_val = float(row["NOPAT"])
        else:
            nopat_val = op_income_val * (1.0 - eff_tax_val)

        # Compute ROIC
        roic = None
        if nopat_val is not None and invested_cap_val not in (None, 0):
            roic = nopat_val / invested_cap_val
        else:
            roic = None

        entry = {}
        if fiscal is not None:
            entry["Fiscal Year"] = fiscal
        entry[INDICATOR_NAME] = to_native(roic)
        der_data.append(entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to file with UTF-8 and ensure ascii disabled to keep Chinese chars
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()