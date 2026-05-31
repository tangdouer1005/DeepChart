import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Dividends,Net Income,Avg Total Assets,ROA(Avg),Retention Ratio
2016,8621000000,16540000000,137309500000.0,0.1204577978945375,0.4787787182587666
2017,8943000000,1300000000,149255500000.0,0.008709896787723,-5.8792307692307695
2018,9494000000,15297000000,155128500000.0,0.0986085728927953,0.3793554291691181
2019,9917000000,15119000000,155341000000.0,0.0973278142924276,0.3440703750248032
2020,10481000000,14714000000,166311000000.0,0.0884728009572427,0.2876851977708304
2021,11032000000,20878000000,178456000000.0,0.1169924239028107,0.4715968962544304
2022,11682000000,17941000000,184698000000.0,0.0971369478824892,0.34886572654813
2023,11770000000,35153000000,177468000000.0,0.1980807807604751,0.6651779364492362
2024,11823000000,14066000000,173831000000.0,0.0809176729121963,0.1594625337693729
"""

INDICATOR_NAME = "内部增长率 (Internal Growth Rate, IGR)"

def to_python_native(val):
    """
    Convert numpy/pandas scalar types to native Python types for JSON serialization.
    """
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    # for pandas Timestamp or other types, fallback to string
    return val

def compute_igr(net_income, dividends, avg_total_assets):
    """
    Compute Internal Growth Rate (IGR) using:
      b = 1 - (Dividends / Net Income)
      ROA = Net Income / Avg Total Assets
      IGR = (ROA * b) / (1 - ROA * b)
    Returns None if calculation is not feasible (e.g., division by zero).
    """
    # Guard against zero or missing inputs
    try:
        if net_income is None or avg_total_assets is None or dividends is None:
            return None
        # convert to float for division
        ni = float(net_income)
        div = float(dividends)
        ata = float(avg_total_assets)

        # If Avg Total Assets is zero, ROA undefined
        if ata == 0:
            return None

        # Compute retention ratio b
        # If net income is zero, division will raise; treat b as None
        if ni == 0:
            return None
        b = 1.0 - (div / ni)

        roa = ni / ata

        denom = 1.0 - (roa * b)
        if denom == 0:
            return None

        igr = (roa * b) / denom
        return float(igr)
    except Exception:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Read CSV from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: raw input rows as list of dicts with native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_native(row[col])
        scr_records.append(rec)

    # Prepare der_data: compute IGR per row
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = to_python_native(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None
        dividends = to_python_native(row["Dividends"]) if "Dividends" in df.columns else None
        net_income = to_python_native(row["Net Income"]) if "Net Income" in df.columns else None
        avg_total_assets = to_python_native(row["Avg Total Assets"]) if "Avg Total Assets" in df.columns else None

        igr_value = compute_igr(net_income=net_income, dividends=dividends, avg_total_assets=avg_total_assets)

        der_rec = {}
        if fiscal_year is not None:
            der_rec["Fiscal Year"] = fiscal_year
        der_rec[INDICATOR_NAME] = to_python_native(igr_value)
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()