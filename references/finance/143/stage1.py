#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Cash & Equiv,Receivables,Operating Expenses,Cost of Revenue,Quick Assets,Daily Burn
2016,6721000000,2509000000,2790000000,2225000000,9230000000,13739726.02739726
2017,5933000000,3344000000,3188000000,2687000000,9277000000,16095890.410958905
2018,6682000000,4728000000,4454000000,3214000000,11410000000,21008219.17808219
2019,6988000000,5509000000,3682000000,3537000000,12497000000,19778082.19178082
2020,10113000000,2646000000,3433000000,3787000000,12759000000,19780821.91780822
2021,7421000000,3006000000,4313000000,4489000000,10427000000,24115068.493150685
2022,7008000000,3425000000,4710000000,5263000000,10433000000,27323287.671232875
2023,8588000000,4060000000,5068000000,6022000000,12648000000,30383561.64383561
2024,8442000000,3773000000,5912000000,6673000000,12215000000,34479452.05479452
"""

def to_python_value(val):
    # Convert numpy/pandas scalar types to native Python types for JSON serialization
    try:
        # pandas/numpy scalars have .item()
        if hasattr(val, "item"):
            return val.item()
    except Exception:
        pass
    # Fallbacks
    if pd.isna(val):
        return None
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows as dictionaries with native python types
    scr_records = []
    for rec in df.to_dict(orient='records'):
        converted = {k: to_python_value(v) for k, v in rec.items()}
        scr_records.append(converted)

    # Calculate Defensive Interval Ratio (DIR) for each row:
    # Formula:
    # Quick Assets = Cash + Receivables + Trading Financial Assets (if available)
    # Daily Cash Consumption = (Operating Expenses + Cost of Revenue) / 365
    # DIR = Quick Assets / Daily Cash Consumption
    der_records = []
    # Determine if we have a Quick Assets column; if not, try to compute from components.
    has_quick_assets_col = 'Quick Assets' in df.columns
    for idx, row in df.iterrows():
        # Extract numeric components safely
        cash = float(row['Cash & Equiv']) if not pd.isna(row['Cash & Equiv']) else 0.0
        receivables = float(row['Receivables']) if not pd.isna(row['Receivables']) else 0.0

        # Quick assets: prefer explicit column if present (treated as raw data), otherwise compute
        if has_quick_assets_col and not pd.isna(row['Quick Assets']):
            quick_assets = float(row['Quick Assets'])
        else:
            # If there's a trading/marketable securities column, include it; otherwise assume zero for that component
            trading_col = None
            for candidate in ['Trading Financial Assets', 'Marketable Securities', 'Short Term Investments']:
                if candidate in df.columns:
                    trading_col = candidate
                    break
            trading = float(row[trading_col]) if (trading_col and not pd.isna(row[trading_col])) else 0.0
            quick_assets = cash + receivables + trading

        # Daily cash consumption based on Operating Expenses and Cost of Revenue
        op_exp = float(row['Operating Expenses']) if not pd.isna(row['Operating Expenses']) else 0.0
        cog = float(row['Cost of Revenue']) if not pd.isna(row['Cost of Revenue']) else 0.0
        daily_cash_consumption = (op_exp + cog) / 365.0

        # Avoid division by zero
        if daily_cash_consumption == 0:
            dir_value = None
        else:
            dir_value = quick_assets / daily_cash_consumption

        # Build result record; include Fiscal Year for clarity
        rec = {
            "Fiscal Year": to_python_value(row['Fiscal Year']),
            "防御区间比率 (Defensive Interval Ratio, DIR)": to_python_value(dir_value)
        }
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to specified output file, ensure Chinese keys are not escaped
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4, default=to_python_value)

if __name__ == "__main__":
    main()