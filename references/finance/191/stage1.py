#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Dividends,Net Income,Avg Total Assets,ROA(Avg),Retention Ratio
2016,213000000.0,614000000,7285684000.0,0.0842748601229479,0.6530944625407167
2017,261000000.0,1666000000,8605500000.0,0.1935971181221312,0.8433373349339736
2018,341000000.0,3047000000,10541000000.0,0.2890617588464093,0.8880866425992779
2019,371000000.0,4141000000,12266500000.0,0.337586108506909,0.91040811398213
2020,390000000.0,2796000000,15303500000.0,0.1827033031659424,0.8605150214592274
2021,395000000.0,4332000000,23053000000.0,0.1879148050145317,0.9088180978762695
2022,399000000.0,9752000000,36489000000.0,0.2672586258872537,0.9590853158326496
2023,398000000.0,4368000000,42684500000.0,0.1023322283264416,0.908882783882784
2024,395000000.0,29760000000,53455000000.0,0.5567299597792535,0.9867271505376344
"""

INDICATOR_NAME = "内部增长率 (Internal Growth Rate, IGR)"

def to_native(val):
    # Convert pandas / numpy scalar types to native Python types for JSON serialization
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, (int, float, str, bool)):
        return val
    # Fallbacks
    try:
        if float(val).is_integer():
            return int(float(val))
    except Exception:
        pass
    try:
        return float(val)
    except Exception:
        return val

def compute_igr(dividends, net_income, avg_total_assets):
    # Compute retention ratio b = 1 - (Dividends / Net Income)
    # Compute ROA = Net Income / Avg Total Assets
    # IGR = (ROA * b) / (1 - (ROA * b))
    # Return None if any denominator would be zero or inputs invalid
    try:
        if net_income is None or avg_total_assets is None:
            return None
        net_income_f = float(net_income)
        if net_income_f == 0:
            return None
        dividends_f = float(dividends) if dividends is not None else 0.0
        avg_assets_f = float(avg_total_assets)
        if avg_assets_f == 0:
            return None

        b = 1.0 - (dividends_f / net_income_f)
        roa = net_income_f / avg_assets_f
        product = roa * b
        denom = 1.0 - product
        if denom == 0:
            return None
        igr = product / denom
        return float(igr)
    except Exception:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: raw scraped data as list of dicts with native Python types
    raw_records = df.to_dict(orient="records")
    scr_data = []
    for rec in raw_records:
        native_rec = {}
        for k, v in rec.items():
            native_rec[k] = to_native(v)
        scr_data.append(native_rec)

    # Prepare der_data: derived indicator values per row
    der_data = []
    for rec in raw_records:
        # Extract raw inputs for calculation
        dividends = rec.get("Dividends", None)
        net_income = rec.get("Net Income", None)
        avg_assets = rec.get("Avg Total Assets", None)
        igr_value = compute_igr(dividends, net_income, avg_assets)
        # Build output record; include Fiscal Year if present in input
        out_rec = {}
        if "Fiscal Year" in rec:
            out_rec["Fiscal Year"] = to_native(rec["Fiscal Year"])
        out_rec[INDICATOR_NAME] = to_native(igr_value)
        der_data.append(out_rec)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON with ensure_ascii=False to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()