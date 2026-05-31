#!/usr/bin/env python3
import sys
import io
import pandas as pd
import json
import numpy as np

CSV_DATA = """Fiscal Year,Avg Receivables,Revenue,Avg Inventory,Cost of Revenue,Avg Payables,DSO,DIO,DPO
2016,1687000000.0,88519000000,11444000000.0,58254000000,6186000000.0,6.956190196454998,71.70426065162907,38.7593984962406
2017,1959500000.0,94595000000,12179000000.0,62282000000,6782500000.0,7.5608383106929535,71.37431360585724,39.74844256767605
2018,1990500000.0,100904000000,12648500000.0,66548000000,7122000000.0,7.200234876714501,69.3740232614053,39.06248121656549
2019,1944000000.0,108203000000,13336500000.0,71043000000,7499500000.0,6.557674001645055,68.51938262742283,38.53043227341188
2020,2021000000.0,110225000000,14228000000.0,72653000000,7771000000.0,6.692356543433886,71.47977371891044,39.04057643868801
2021,2549000000.0,132110000000,15579000000.0,87257000000,9696500000.0,7.0425024600711525,65.16766563141066,40.56090055812141
2022,3209000000.0,151157000000,19347500000.0,100325000000,12534000000.0,7.748797607785283,70.38960877149265,45.600897084475456
2023,3371500000.0,157403000000,23477000000.0,104625000000,12452500000.0,7.818132437120004,81.90303464755078,43.44241338112306
2024,3322500000.0,152669000000,22931000000.0,101709000000,10740000000.0,7.943410253555076,82.29178342132947,38.54231188980327
"""

INDICATOR_NAME = "现金循环周期 (Cash Conversion Cycle, CCC)"
DAYS = 365.0

def to_native(value):
    # Convert numpy/pandas scalar types to native Python types for JSON serialization
    if value is None:
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.ndarray,)):
        return value.tolist()
    # pandas NA
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure required raw columns exist
    required_cols = ["Fiscal Year", "Avg Receivables", "Revenue", "Avg Inventory", "Cost of Revenue", "Avg Payables"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column in input data: {col}")

    # Calculate components per reference:
    # DSO = (Avg Receivables / Revenue) * 365
    # DIO = (Avg Inventory / Cost of Revenue) * 365
    # DPO = (Avg Payables / Cost of Revenue) * 365
    # CCC = DSO + DIO - DPO
    # Use float division and handle zeros safely
    df_calc = df.copy()
    # Avoid division by zero by replacing zero denominators with NaN
    df_calc["DSO_calc"] = df_calc.apply(
        lambda r: (r["Avg Receivables"] / r["Revenue"]) * DAYS if r["Revenue"] not in (0, 0.0, None) else float("nan"),
        axis=1,
    )
    df_calc["DIO_calc"] = df_calc.apply(
        lambda r: (r["Avg Inventory"] / r["Cost of Revenue"]) * DAYS if r["Cost of Revenue"] not in (0, 0.0, None) else float("nan"),
        axis=1,
    )
    df_calc["DPO_calc"] = df_calc.apply(
        lambda r: (r["Avg Payables"] / r["Cost of Revenue"]) * DAYS if r["Cost of Revenue"] not in (0, 0.0, None) else float("nan"),
        axis=1,
    )
    df_calc["CCC"] = df_calc["DSO_calc"] + df_calc["DIO_calc"] - df_calc["DPO_calc"]

    # Prepare scr_data: the original input rows as dictionaries
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Prepare der_data: one dict per row containing Fiscal Year (if present) and CCC
    der_records = []
    for _, row in df_calc.iterrows():
        rec = {}
        # Include year if present
        if "Fiscal Year" in df_calc.columns:
            rec["Fiscal Year"] = to_native(row["Fiscal Year"])
        # Calculated CCC
        rec[INDICATOR_NAME] = to_native(row["CCC"])
        der_records.append(rec)

    output_obj = {"scr_data": scr_records, "der_data": der_records}

    # Write JSON to file with UTF-8 encoding and ensure Chinese characters are preserved
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()