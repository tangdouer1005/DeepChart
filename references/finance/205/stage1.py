#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Current Assets,Total Liabilities,Shares,Net-Net Value
2016,64313000000,64390000000,4305000000,-77000000
2017,74515000000,80745000000,4219643000,-6230000000
2018,76159000000,91040000000,4238000000,-14881000000
2019,46386000000,86346000000,3732000000,-39960000000
2020,52140000000,102721000000,3294000000,-50581000000
2021,55567000000,125155000000,3022000000,-69588000000
2022,31633000000,115065000000,2786000000,-83432000000
2023,21004000000,132828000000,2766000000,-111824000000
2024,22554000000,131737000000,2823000000,-109183000000
"""

INDICATOR_NAME = '格雷厄姆“烟蒂股”净值 (Graham\'s Net-Net Working Capital, NNWC)'
PER_SHARE_NAME = '每股清算价值 (Per Share Liquidation Value)'

def load_data(csv_text: str) -> pd.DataFrame:
    return pd.read_csv(io.StringIO(csv_text))

def to_python_types(row):
    """Convert pandas row to plain python types for JSON serialization."""
    out = {}
    for k, v in row.items():
        if pd.isna(v):
            out[k] = None
        else:
            # convert numpy types to native python types
            if isinstance(v, (pd.Timestamp, )):
                out[k] = str(v)
            else:
                try:
                    # prefer int when value is integral
                    if float(v).is_integer():
                        out[k] = int(v)
                    else:
                        out[k] = float(v)
                except Exception:
                    out[k] = v
    return out

def calculate_nnwc(df: pd.DataFrame):
    """
    Calculate Net-Net Working Capital (Total Current Assets - Total Liabilities)
    and Per-Share Liquidation Value = Net-Net Value / Shares.
    Returns a list of dicts with 'Year' and the indicator value.
    """
    results = []
    for _, row in df.iterrows():
        # Read required raw data (ensure numeric)
        fiscal = int(row['Fiscal Year']) if not pd.isna(row['Fiscal Year']) else None
        current_assets = int(row['Current Assets']) if not pd.isna(row['Current Assets']) else None
        total_liabilities = int(row['Total Liabilities']) if not pd.isna(row['Total Liabilities']) else None
        shares = int(row['Shares']) if not pd.isna(row['Shares']) else None

        # Calculate Net-Net Value (NNWC) according to reference:
        # Net-Net Value = Total Current Assets - Total Liabilities
        net_net_value = None
        per_share_value = None
        if (current_assets is not None) and (total_liabilities is not None):
            net_net_value = current_assets - total_liabilities  # may be negative
            # per-share liquidation value if shares available and non-zero
            if shares:
                per_share_value = net_net_value / shares

        entry = {'Year': fiscal, INDICATOR_NAME: net_net_value}
        # include per-share value as an additional derived metric
        entry[PER_SHARE_NAME] = per_share_value
        results.append(entry)
    return results

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = load_data(CSV_DATA)

    # Prepare scr_data: original rows as dictionaries with native python types
    scr_data = []
    for _, row in df.iterrows():
        scr_data.append(to_python_types(row))

    # Calculate derived data
    der_data = calculate_nnwc(df)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON with unicode preserved
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()