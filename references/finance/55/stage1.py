#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Cash & Equivalents,SG&A,R&D,Interest Expense,Monthly Burn
2016,1158363000,711621000,946300000,72485000.0,144200500.0
2017,1606549000,966000000,1208000000,89000000.0,188583333.3333333
2018,2543484000,1088358000,1553073000,54000000.0,224619250.0
2019,2669000000,1346000000,1886000000,126000000.0,279833333.3333333
2020,4145000000,1704000000,2766000000,110000000.0,381666666.6666667
2021,6195000000,2087000000,3598000000,110000000.0,482916666.6666667
2022,5464000000,2598000000,4465000000,216000000.0,606583333.3333334
2023,7016000000,2553000000,5055000000,287000000.0,657916666.6666666
"""

INDICATOR_NAME = "现金消耗跑道 (Cash Burn Runway) - 零收入情景 (Zero Revenue Scenario)"

def to_native(value):
    """
    Convert numpy/pandas scalars to native Python types so they are JSON serializable.
    """
    try:
        # numpy/pandas scalars have item()
        return value.item()
    except Exception:
        return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original records converted to native types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Compute the Cash Burn Runway (Zero Revenue Scenario) for each row
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = to_native(row["Fiscal Year"])
        cash = float(row["Cash & Equivalents"])
        sg_a = float(row["SG&A"])
        r_and_d = float(row["R&D"])
        interest = float(row["Interest Expense"])

        # Monthly rigid outflow = (SG&A + R&D + Interest Expense) / 12
        monthly_rigid_outflow = (sg_a + r_and_d + interest) / 12.0

        # If monthly rigid outflow is <= 0, runway is undefined (set to None -> null in JSON)
        if monthly_rigid_outflow > 0:
            runway_months = cash / monthly_rigid_outflow
        else:
            runway_months = None

        rec = {
            "Fiscal Year": fiscal_year,
            INDICATOR_NAME: to_native(runway_months) if runway_months is not None else None
        }
        der_records.append(rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file with non-ASCII characters preserved
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()