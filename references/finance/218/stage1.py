#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,NOPAT,Avg Invested Capital,WACC,Capital Charge
2016,10081001346.398384,83401500000.0,0.1,8340150000.0
2017,10585396696.085089,81036500000.0,0.1,8103650000.0
2018,9888379333.6335,81126000000.0,0.1,8112600000.0
2019,3585671774.5921893,77044000000.0,0.1,7704400000.0
2020,12997077049.387394,69177500000.0,0.1,6917750000.0
2021,14654276014.760147,66798000000.0,0.1,6679800000.0
2022,14643384773.548208,69685000000.0,0.1,6968500000.0
2023,14562136544.434153,72216500000.0,0.1,7221650000.0
2024,14801600660.94558,73433500000.0,0.1,7343350000.0
"""

INDICATOR_NAME = "经济增加值 (Economic Value Added, EVA) - 简化版"

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from hardcoded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure Fiscal Year is int (if parsed as float)
    if 'Fiscal Year' in df.columns:
        try:
            df['Fiscal Year'] = df['Fiscal Year'].astype(int)
        except Exception:
            pass

    # Prepare scr_data: list of dicts matching input CSV rows
    scr_data = []
    for row in df.to_dict(orient='records'):
        # Convert any numpy types to native Python types for JSON serialization
        clean_row = {}
        for k, v in row.items():
            if pd.isna(v):
                clean_row[k] = None
            else:
                # Cast numpy int/float to native
                if isinstance(v, (pd.Timestamp,)):
                    clean_row[k] = str(v)
                else:
                    try:
                        if float(v).is_integer():
                            # keep integers as int
                            iv = int(v)
                            clean_row[k] = iv
                        else:
                            clean_row[k] = float(v)
                    except Exception:
                        clean_row[k] = v
        scr_data.append(clean_row)

    # Calculate EVA for each row using formula:
    # EVA = NOPAT - (Invested Capital * WACC)
    # Here we use 'Avg Invested Capital' as Invested Capital
    der_data = []
    for idx, row in df.iterrows():
        nopat = float(row['NOPAT']) if not pd.isna(row['NOPAT']) else None
        invested_capital = float(row['Avg Invested Capital']) if not pd.isna(row['Avg Invested Capital']) else None
        wacc = float(row['WACC']) if not pd.isna(row['WACC']) else None

        if nopat is None or invested_capital is None or wacc is None:
            eva = None
        else:
            capital_charge = invested_capital * wacc
            eva = nopat - capital_charge

        entry = {}
        # include year if present
        if 'Fiscal Year' in df.columns:
            try:
                entry['Fiscal Year'] = int(row['Fiscal Year'])
            except Exception:
                entry['Fiscal Year'] = row['Fiscal Year']
        entry[INDICATOR_NAME] = eva
        der_data.append(entry)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON with ensure_ascii False to preserve Chinese characters
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()