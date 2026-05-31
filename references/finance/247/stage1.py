#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,CFO,Net Income,Total Assets,Avg Total Assets,CFO per Asset,NI per Asset
2016,-123829000,-674914000,22664076000.0,15366007500.0,-0.0080586320161564,-0.0439225348549387
2017,-61000000,-1962000000,28655372000.0,25659724000.0,-0.0023772664117509,-0.0764622409812358
2018,2098000000,-976000000,29740000000.0,29197686000.0,0.0718550093319039,-0.0334273065338123
2019,2405000000,-862000000,34309000000.0,32024500000.0,0.0750987525176037,-0.0269168917547502
2020,5943000000,721000000,52148000000.0,43228500000.0,0.1374787466601894,0.0166788114322726
2021,11497000000,5644000000,62131000000.0,57139500000.0,0.2012093210476115,0.0987758030784308
2022,14724000000,12587000000,82338000000.0,72234500000.0,0.2038361170908637,0.1742519156358803
2023,13256000000,14974000000,106618000000.0,94478000000.0,0.1403077965240585,0.1584919240458096
2024,14923000000,7130000000,122070000000.0,114344000000.0,0.1305096900580704,0.0623556985937172
"""

INDICATOR_NAME = "盈余-现金质量剪刀差 (Earnings Quality Spread)"

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    scr_data = []
    der_data = []

    # Build scr_data with native Python types
    for _, row in df.iterrows():
        rec = {}
        # Map columns with appropriate native types
        for col in df.columns:
            val = row[col]
            if pd.isna(val):
                rec[col] = None
            else:
                if col == "Fiscal Year":
                    rec[col] = int(val)
                elif col in ("CFO", "Net Income"):
                    # these are whole amounts, convert to int
                    # but ensure we handle floats that are whole numbers
                    rec[col] = int(val)
                else:
                    # other numeric fields as float
                    rec[col] = float(val)
        scr_data.append(rec)

        # Calculate Earnings Quality Spread dynamically:
        # Spread = (CFO / Total Assets) - (Net Income / Total Assets)
        total_assets = rec.get("Total Assets")
        cfo = rec.get("CFO")
        net_income = rec.get("Net Income")

        if total_assets in (0, None):
            spread = None
        else:
            spread = (cfo / total_assets) - (net_income / total_assets)

        der_rec = {
            "Fiscal Year": rec.get("Fiscal Year"),
            INDICATOR_NAME: None if spread is None else float(spread)
        }
        der_data.append(der_rec)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON with ensure_ascii=False to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()