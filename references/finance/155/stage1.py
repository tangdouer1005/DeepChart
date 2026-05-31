import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Current Assets,Total Liabilities,Shares,Net-Net Value
2016,34401000000.0,5767000000.0,2925000000,28634000000.0
2017,48563000000.0,10177000000.0,2956000000,38386000000.0
2018,50480000000.0,13207000000.0,2921000000,37273000000.0
2019,66225000000.0,32322000000.0,2876000000,33903000000.0
2020,75670000000.0,31026000000.0,2888000000,44644000000.0
2021,66666000000.0,41108000000.0,2859000000,25558000000.0
2022,59549000000.0,60014000000.0,2702000000,-465000000.0
2023,85365000000.0,76455000000.0,2629000000,8910000000.0
2024,100045000000.0,93417000000.0,2614000000,6628000000.0
"""

INDICATOR_NAME = '格雷厄姆“烟蒂股”净值 (Graham\'s Net-Net Working Capital, NNWC)'
PER_SHARE_NAME = '每股清算价值 (Per-Share Liquidation Value)'

def to_python_native(val):
    # Convert pandas/numpy types to native Python types for JSON serialization
    if pd.isna(val):
        return None
    # Convert numpy integer/float to python int/float
    try:
        if isinstance(val, (float,)) and val.is_integer():
            return int(val)
    except Exception:
        pass
    # For other numeric types, attempt direct conversion
    if hasattr(val, 'item'):
        try:
            return val.item()
        except Exception:
            pass
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Calculation for Graham's Net-Net Working Capital (NNWC)
    # Net-Net Value = Total Current Assets - Total Liabilities
    # Per-share liquidation value = Net-Net Value / Shares Outstanding
    df['Calculated_NetNet'] = df['Current Assets'] - df['Total Liabilities']
    df['Per_Share_Liquidation'] = df['Calculated_NetNet'] / df['Shares']

    # Prepare scr_data: mirror input CSV rows with original headers
    scr_data = []
    for _, row in df.iterrows():
        entry = {}
        for col in ['Fiscal Year', 'Current Assets', 'Total Liabilities', 'Shares', 'Net-Net Value']:
            entry[col] = to_python_native(row[col])
        scr_data.append(entry)

    # Prepare der_data: calculated indicator per row. Include Fiscal Year for mapping.
    der_data = []
    for _, row in df.iterrows():
        der_entry = {
            'Fiscal Year': to_python_native(row['Fiscal Year']),
            INDICATOR_NAME: to_python_native(row['Calculated_NetNet']),
            PER_SHARE_NAME: to_python_native(row['Per_Share_Liquidation'])
        }
        der_data.append(der_entry)

    output_obj = {
        'scr_data': scr_data,
        'der_data': der_data
    }

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()