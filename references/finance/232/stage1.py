#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import math

CSV_DATA = """Fiscal Year,Operating Income,Income Tax,Pretax Income,Effective Tax Rate,NOPAT,Avg Invested Capital
2016,4050000000,867000000,2327000000,0.3725827245380318,2541039965.620971,35092000000.0
2017,4888000000,1375000000,3161000000,0.4349889275545713,2761774122.1132555,36308000000.0
2018,5309000000,1029000000,3917000000,0.2627010467194281,3914320142.966556,36197000000.0
2019,5722000000,1135000000,4603000000,0.2465783184879426,4311078861.611992,39404500000.0
2020,6636000000,786000000,3530000000,0.2226628895184136,5158409065.155808,83893500000.0
2021,6892000000,327000000,3351000000,0.0975828111011638,6219459265.890779,133754000000.0
2022,6543000000,556000000,3146000000,0.1767323585505403,5386640178.003815,141495500000.0
2023,14266000000,2682000000,10999000000,0.2438403491226475,10787373579.416311,140967500000.0
2024,18010000000,3373000000,14712000000,0.229268624252311,13880872077.21588,139833000000.0
"""

def to_native(value):
    # Convert pandas/numpy types to native Python types for JSON serialization
    if pd.isna(value):
        return None
    # bool check first
    if isinstance(value, (bool,)):
        return value
    try:
        # numpy integer / float have .item()
        return value.item()
    except Exception:
        return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: mirror the input CSV rows as dictionaries
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_data.append(rec)

    # Calculate ROIC for each row using the reference formula:
    # 1. NOPAT = Operating Income * (1 - Effective Tax Rate)
    # 2. Invested Capital = Avg Invested Capital (provided as raw input)
    # 3. ROIC = NOPAT / Invested Capital
    der_data = []
    roic_key = "投入资本回报率 (Return on Invested Capital, ROIC)"
    for _, row in df.iterrows():
        fiscal = to_native(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None

        operating_income = float(row["Operating Income"]) if not pd.isna(row.get("Operating Income")) else None
        eff_tax = float(row["Effective Tax Rate"]) if not pd.isna(row.get("Effective Tax Rate")) else None
        invested_capital = float(row["Avg Invested Capital"]) if not pd.isna(row.get("Avg Invested Capital")) else None

        # Compute NOPAT dynamically per reference (do not use provided NOPAT column for calculation)
        nopat = None
        roic = None
        if operating_income is not None and eff_tax is not None:
            nopat = operating_income * (1.0 - eff_tax)

        if nopat is not None and invested_capital is not None and invested_capital != 0:
            roic = nopat / invested_capital
            # Optionally, if value is extremely close to zero, set to 0.0
            if isinstance(roic, float) and (math.isfinite(roic) is False):
                roic = None

        rec = {}
        if fiscal is not None:
            rec["Year"] = fiscal
        # Ensure the ROIC value is a native Python type (or null)
        rec[roic_key] = to_native(roic) if roic is not None else None
        der_data.append(rec)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to the specified output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()