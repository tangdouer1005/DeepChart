#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Current Assets,Total Liabilities,Shares,Net-Net Value
2016,4347327000,7760051000,661647000,-3412724000
2017,5996827000,10084796000,700217000,-4087969000
2018,9290371000,11617439000,734598000,-2327068000
2019,10683000000,15132000000,775000000,-4449000000
2020,15963000000,21241000000,850000000,-5278000000
2021,21889000000,24808000000,930000000,-2919000000
2022,22850000000,37078000000,974000000,-14228000000
2023,26395000000,40490000000,997000000,-14095000000
2024,29074000000,40177000000,984000000,-11103000000
"""

INDICATOR_NAME = "格雷厄姆“烟蒂股”净值 (Graham's Net-Net Working Capital, NNWC)"

def to_native(v):
    """Convert pandas/numpy scalar to native Python types for JSON serialization."""
    if pd.isna(v):
        return None
    # numpy integer
    if isinstance(v, (np.integer,)):
        return int(v)
    # numpy floating
    if isinstance(v, (np.floating,)):
        # if integral value, return int
        if float(v).is_integer():
            return int(v)
        return float(v)
    # Python int/float
    if isinstance(v, (int, float)):
        # convert float that is integral to int
        if isinstance(v, float) and v.is_integer():
            return int(v)
        return v
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original CSV rows, converted to native Python types
    raw_records = df.to_dict(orient="records")
    scr_data = []
    for rec in raw_records:
        converted = {}
        for k, v in rec.items():
            converted[k] = to_native(v)
        scr_data.append(converted)

    # Calculate NNWC per the provided reference:
    # Net-Net Value = Total Current Assets - Total Liabilities
    # Per-share liquidation value = Net-Net Value / Shares
    der_data = []
    for _, row in df.iterrows():
        # Extract required fields, handle missing gracefully
        ca = row.get("Current Assets", np.nan)
        tl = row.get("Total Liabilities", np.nan)
        shares = row.get("Shares", np.nan)

        # Ensure numeric (float) for calculation
        try:
            ca_val = float(ca)
        except Exception:
            ca_val = float("nan")
        try:
            tl_val = float(tl)
        except Exception:
            tl_val = float("nan")
        try:
            shares_val = float(shares)
        except Exception:
            shares_val = float("nan")

        net_net_value = ca_val - tl_val  # Total Current Assets - Total Liabilities
        # Per-share liquidation value; guard against division by zero or NaN
        if shares_val == 0 or np.isnan(shares_val):
            per_share = None
        else:
            per_share = net_net_value / shares_val

        # Convert to native types for JSON
        entry = {}
        # include the Fiscal Year if present
        if "Fiscal Year" in row:
            entry["Fiscal Year"] = to_native(row["Fiscal Year"])
        # The calculated indicator value
        entry[INDICATOR_NAME] = to_native(per_share) if per_share is not None else None

        der_data.append(entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON with non-ASCII characters preserved
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()