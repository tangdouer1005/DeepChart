#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,CFO,Net Income,Total Assets,Avg Total Assets,CFO per Asset,NI per Asset
2016,4575115000,4111892000,20609004000,19405825500.0,0.2357598753013624,0.2118895689338235
2017,4973039000,3445149000,22689890000,21649447000.0,0.2297074377927528,0.1591333487640585
2018,6026688000,4059907000,24449083000,23569486500.0,0.255698739978913,0.1722526708420228
2019,6626953000,4779112000,29789880000,27119481500.0,0.244361345920275,0.1762243131381402
2020,8215152000,5107839000,37078593000,33434236500.0,0.2457107701562139,0.1527727124858975
2021,8975148000,5906809000,43175843000,40127218000.0,0.223667337217347,0.1472020562202941
2022,9541129000,6877169000,47263390000,45219616500.0,0.2109953541954518,0.1520837532976424
2023,9524268000,6871557000,51245305000,49254347500.0,0.1933690828002543,0.1395116847299621
2024,9131027000,7264787000,55932363000,53588834000.0,0.1703904772400907,0.1355653119827164
"""

INDICATOR_NAME = "盈余-现金质量剪刀差 (Earnings Quality Spread)"

def to_python_native(value):
    """
    Convert pandas / numpy scalar types to native Python types for JSON serialization.
    """
    if pd.isna(value):
        return None
    # numpy/Pandas scalars have .item()
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows as list of dicts with native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_native(row[col])
        scr_records.append(rec)

    # Calculate the Earnings Quality Spread for each row:
    # Spread = (CFO / Total Assets) - (Net Income / Total Assets)
    der_records = []
    for _, row in df.iterrows():
        cfo = row["CFO"]
        ni = row["Net Income"]
        total_assets = row["Total Assets"]

        # Defensive checks to avoid division by zero
        if total_assets == 0 or pd.isna(total_assets):
            spread = None
        else:
            # compute as specified; keep as float
            spread = (float(cfo) / float(total_assets)) - (float(ni) / float(total_assets))

        der_rec = {
            "Fiscal Year": to_python_native(row["Fiscal Year"]),
            INDICATOR_NAME: to_python_native(spread)
        }
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to specified output file with UTF-8 encoding and ensure Chinese keys are preserved
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()