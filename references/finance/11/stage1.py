#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Dividends,Net Income,Avg Total Assets,ROA(Avg),Retention Ratio
2016,1539000000,1400000000,49506000000.0,0.0282794004767098,-0.0992857142857142
2017,1849000000,477000000,65630500000.0,0.0072679623041116,-2.876310272536688
2018,1974000000,2368000000,71711500000.0,0.0330212030148581,0.1663851351351351
2019,2270000000,3687000000,67530000000.0,0.0545979564637938,0.3843232980743152
2020,2560000000,4495000000,70217500000.0,0.0640153807811443,0.4304783092324805
2021,3202000000,7071000000,73872000000.0,0.0957196231319038,0.5471644746146231
2022,3309000000,6933000000,74817000000.0,0.0926661052969245,0.5227174383383817
2023,3556000000,5723000000,73826000000.0,0.0775201148646818,0.3786475624672374
2024,3836000000,13402000000,77314000000.0,0.1733450604030318,0.7137740635726011
"""

INDICATOR_NAME = "内部增长率 (Internal Growth Rate, IGR)"

def to_python_value(v):
    # Convert numpy/pandas scalar types to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    return v

def compute_igr_row(dividends, net_income, avg_total_assets):
    """
    Compute Internal Growth Rate (IGR) for a single row using:
      retention ratio b = 1 - (Dividends / Net Income)
      ROA = Net Income / Avg Total Assets
      IGR = (ROA * b) / (1 - (ROA * b))
    Returns a Python float or None if computation is not possible (e.g., division by zero).
    """
    # Guard against invalid inputs
    try:
        # Convert to floats
        dividends = float(dividends)
        net_income = float(net_income)
        avg_total_assets = float(avg_total_assets)
    except Exception:
        return None

    # If Net Income is zero, retention ratio is undefined; return None
    if net_income == 0 or avg_total_assets == 0:
        return None

    b = 1.0 - (dividends / net_income)
    roa = net_income / avg_total_assets
    denom = 1.0 - (roa * b)
    # If denominator is zero (or extremely close), return None to avoid infinite values
    if abs(denom) < 1e-12:
        return None
    igr = (roa * b) / denom
    return float(igr)

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the hardcoded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: array of dicts representing original rows
    scr_records = []
    for rec in df.to_dict(orient='records'):
        converted = {k: to_python_value(v) for k, v in rec.items()}
        scr_records.append(converted)

    # Compute IGR for each row and prepare der_data
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = to_python_value(row.get("Fiscal Year"))
        dividends = row.get("Dividends")
        net_income = row.get("Net Income")
        avg_total_assets = row.get("Avg Total Assets")
        igr_value = compute_igr_row(dividends, net_income, avg_total_assets)
        der_entry = {
            "Fiscal Year": fiscal_year,
            INDICATOR_NAME: to_python_value(igr_value)
        }
        der_records.append(der_entry)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()