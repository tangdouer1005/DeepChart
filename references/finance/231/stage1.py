#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Dividends,Net Income,Avg Total Assets,ROA(Avg),Retention Ratio
2016,55000000.0,1460000000,64163500000.0,0.0227543696961668,0.9623287671232876
2017,55000000.0,4536000000,68227000000.0,0.0664839433069019,0.9878747795414462
2018,0.0,2888000000,71515500000.0,0.0403828540666009,1.0
2019,0.0,3468000000,79694500000.0,0.0435161774024556,1.0
2020,54080000000.0,3064000000,143541500000.0,0.0213457432171183,-16.650130548302872
2021,0.0,3024000000,203362500000.0,0.0148699981560022,1.0
2022,0.0,2590000000,208950500000.0,0.0123952802218707,1.0
2023,747000000.0,8317000000,209510000000.0,0.0396973891461028,0.9101839605627028
2024,3300000000.0,11339000000,207858500000.0,0.0545515338559645,0.70896904488932
"""

INDICATOR_NAME = "内部增长率 (Internal Growth Rate, IGR)"

def to_native(value):
    """Convert pandas/numpy scalars to native Python types for JSON serialization."""
    if pd.isna(value):
        return None
    if isinstance(value, (np.generic,)):
        return value.item()
    return value

def compute_igr(dividends, net_income, avg_total_assets):
    """
    Compute Internal Growth Rate (IGR) per formula:
      b = 1 - (Dividends / Net Income)
      ROA = Net Income / Avg Total Assets
      IGR = (ROA * b) / (1 - (ROA * b))
    Returns Python float or None if cannot compute (e.g., division by zero).
    """
    try:
        # ensure floats
        if net_income is None or avg_total_assets is None or dividends is None:
            return None
        net_income = float(net_income)
        avg_total_assets = float(avg_total_assets)
        dividends = float(dividends)

        # retention ratio
        if net_income == 0:
            return None  # cannot compute retention if net income zero
        b = 1.0 - (dividends / net_income)

        # ROA
        if avg_total_assets == 0:
            return None
        roa = net_income / avg_total_assets

        x = roa * b
        denom = 1.0 - x
        if denom == 0:
            return None
        igr = x / denom
        return float(igr)
    except Exception:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: list of dicts with original CSV headers and native types
    scr_records = []
    for rec in df.to_dict(orient="records"):
        native_rec = {k: to_native(v) for k, v in rec.items()}
        scr_records.append(native_rec)

    # Compute der_data: one dict per row with Fiscal Year and computed IGR
    der_records = []
    for rec in scr_records:
        # Extract required raw fields
        dividends = rec.get("Dividends")
        net_income = rec.get("Net Income")
        avg_assets = rec.get("Avg Total Assets")
        fiscal_year = rec.get("Fiscal Year")
        igr_value = compute_igr(dividends, net_income, avg_assets)
        der_entry = {
            "Fiscal Year": fiscal_year,
            INDICATOR_NAME: igr_value
        }
        der_records.append(der_entry)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()