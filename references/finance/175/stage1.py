import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Current Assets,Total Liabilities,Shares,Net-Net Value
2016,139660000000,121697000000,8013000000,17963000000
2017,159851000000,168692000000,7832000000,-8841000000
2018,169662000000,176130000000,7794000000,-6468000000
2019,175552000000,184226000000,7753000000,-8674000000
2020,181915000000,183007000000,7683000000,-1092000000
2021,184406000000,191791000000,7608000000,-7385000000
2022,169684000000,198298000000,7540000000,-28614000000
2023,184257000000,205753000000,7472000000,-21496000000
2024,159734000000,243686000000,7469000000,-83952000000
"""

INDICATOR_NAME = '格雷厄姆“烟蒂股”净值 (Graham\'s Net-Net Working Capital, NNWC)'

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric types
    for col in ['Current Assets', 'Total Liabilities', 'Shares']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Calculate Net-Net Value (流动资产总额 - 负债总额)
    df['Calculated_NetNetValue'] = df['Current Assets'] - df['Total Liabilities']

    # Calculate per-share liquidation value (每股清算价值)
    # Avoid division by zero: if Shares is zero or NaN, result will be None
    def per_share(row):
        shares = row.get('Shares')
        if shares is None or pd.isna(shares) or shares == 0:
            return None
        return row['Calculated_NetNetValue'] / shares

    df['Calculated_NetNet_PerShare'] = df.apply(per_share, axis=1)

    # Prepare scr_data: original CSV rows as dictionaries (preserve original columns)
    scr_data = df[['Fiscal Year', 'Current Assets', 'Total Liabilities', 'Shares', 'Net-Net Value']].to_dict(orient='records')

    # Prepare der_data: for each row include Year and the calculated indicator value
    der_data = []
    for _, row in df.iterrows():
        entry = {
            "Year": int(row['Fiscal Year']) if not pd.isna(row['Fiscal Year']) else None,
            # The indicator key must be present and its value must be derived dynamically.
            # We store the per-share liquidation value under the indicator name.
            INDICATOR_NAME: None if pd.isna(row['Calculated_NetNet_PerShare']) else float(row['Calculated_NetNet_PerShare'])
        }
        der_data.append(entry)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to specified output path
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()