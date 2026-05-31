#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,CFO,Net Income,Total Assets,Avg Total Assets,CFO per Asset,NI per Asset
2016,1175000000,614000000,7370000000,7285684000.0,0.1612751802027098,0.0842748601229479
2017,1672000000,1666000000,9841000000,8605500000.0,0.1942943466387775,0.1935971181221312
2018,3502000000,3047000000,11241000000,10541000000.0,0.3322265439711602,0.2890617588464093
2019,3743000000,4141000000,13292000000,12266500000.0,0.3051400154893409,0.337586108506909
2020,4761000000,2796000000,17315000000,15303500000.0,0.3111053027085307,0.1827033031659424
2021,5822000000,4332000000,28791000000,23053000000.0,0.2525484752526786,0.1879148050145317
2022,9108000000,9752000000,44187000000,36489000000.0,0.2496094713475294,0.2672586258872537
2023,5641000000,4368000000,41182000000,42684500000.0,0.1321557005470369,0.1023322283264416
2024,28090000000,29760000000,65728000000,53455000000.0,0.5254887288373398,0.5567299597792535
"""

INDICATOR_NAME = "盈余-现金质量剪刀差 (Earnings Quality Spread)"

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)

    out_path = sys.argv[1]

    # Load CSV from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric types are proper (pandas will typically handle this)
    # Build scr_data: original rows as dictionaries
    # Convert numpy types to native Python types via .item() where necessary when serializing
    scr_records = []
    for _, row in df.iterrows():
        rec = {
            "Fiscal Year": int(row["Fiscal Year"]) if not pd.isna(row["Fiscal Year"]) else None,
            "CFO": None if pd.isna(row["CFO"]) else float(row["CFO"]),
            "Net Income": None if pd.isna(row["Net Income"]) else float(row["Net Income"]),
            "Total Assets": None if pd.isna(row["Total Assets"]) else float(row["Total Assets"]),
            "Avg Total Assets": None if pd.isna(row["Avg Total Assets"]) else float(row["Avg Total Assets"]),
            "CFO per Asset": None if pd.isna(row["CFO per Asset"]) else float(row["CFO per Asset"]),
            "NI per Asset": None if pd.isna(row["NI per Asset"]) else float(row["NI per Asset"]),
        }
        scr_records.append(rec)

    # Calculate Earnings Quality Spread for each row:
    # Spread = (CFO / Total Assets) - (Net Income / Total Assets)
    der_records = []
    for rec in scr_records:
        fiscal = rec.get("Fiscal Year")
        cfo = rec.get("CFO")
        ni = rec.get("Net Income")
        ta = rec.get("Total Assets")

        spread = None
        # Guard against division by zero or missing data
        if ta in (None, 0) or cfo is None or ni is None:
            spread = None
        else:
            spread = (cfo / ta) - (ni / ta)

        der_rec = {
            "Fiscal Year": fiscal,
            INDICATOR_NAME: None if spread is None else float(spread)
        }
        der_records.append(der_rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file with UTF-8 and preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()