#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Current Assets,Total Liabilities,Shares,Net-Net Value
2016,5720291000,10906810000,4386520000,-5186519000
2017,7669974000,15430786000,4468140000,-7760812000
2018,9694135000,20735635000,4512440000,-11041500000
2019,6178504000,26393555000,4517650000,-20215051000
2020,9761580000,28215119000,4542080000,-18453539000
2021,8069825000,28735415000,4553720000,-20665590000
2022,9266473000,27817367000,4512900000,-18550894000
2023,9918133000,28143679000,4494980000,-18225546000
2024,13100379000,28886807000,4392610000,-15786428000
"""

INDICATOR_NAME = '格雷厄姆“烟蒂股”净值 (Graham\'s Net-Net Working Capital, NNWC)'

def to_python_scalar(v):
    # Convert numpy / pandas scalar types to native Python types for JSON serialization
    try:
        # pandas/numpy scalars often have .item()
        if hasattr(v, "item"):
            return v.item()
    except Exception:
        pass
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded multiline string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: raw input rows as dictionaries, converting scalars to native types
    raw_records = []
    for rec in df.to_dict(orient='records'):
        cleaned = {k: to_python_scalar(v) for k, v in rec.items()}
        raw_records.append(cleaned)

    # Calculate NNWC per the reference:
    # Net-Net Value = Total Current Assets - Total Liabilities
    # Per-share liquidation value = Net-Net Value / Shares
    derived_records = []
    for row in raw_records:
        # Extract necessary fields, ensure numeric
        ca = row.get("Current Assets", None)
        tl = row.get("Total Liabilities", None)
        shares = row.get("Shares", None)
        fiscal = row.get("Fiscal Year", None)

        # Convert possible strings to numbers (defensive)
        try:
            ca_n = float(ca) if ca is not None else None
        except Exception:
            ca_n = None
        try:
            tl_n = float(tl) if tl is not None else None
        except Exception:
            tl_n = None
        try:
            shares_n = float(shares) if shares is not None else None
        except Exception:
            shares_n = None

        net_net_value = None
        per_share_value = None
        if (ca_n is not None) and (tl_n is not None):
            net_net_value = ca_n - tl_n
            if (shares_n is not None) and (shares_n != 0):
                per_share_value = net_net_value / shares_n

        # For this indicator we provide the per-share liquidation value under the indicator name.
        # Also include the Fiscal Year for reference.
        entry = {"Fiscal Year": fiscal, INDICATOR_NAME: to_python_scalar(per_share_value)}
        # Optionally, one could include the absolute Net-Net Value as well, but the requirement
        # asks for the calculated indicator value keyed by the indicator name.
        derived_records.append(entry)

    output_obj = {
        "scr_data": raw_records,
        "der_data": derived_records
    }

    # Write JSON with ensure_ascii=False to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()