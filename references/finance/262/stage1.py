#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Avg Receivables,Revenue,Avg Inventory,Cost of Revenue,Avg Payables,DSO,DIO,DPO
2016,2036000000.0,15082000000,2796500000.0,2764000000,165000000.0,49.27330592759581,369.2917872648336,21.789073806078147
2017,2647000000.0,18358000000,2519000000.0,3248000000,191000000.0,52.62855430874823,283.07727832512313,21.463977832512317
2018,2672000000.0,20609000000,3032000000.0,3856000000,181000000.0,47.32301421708963,287.00207468879665,17.133039419087137
2019,3690000000.0,22977000000,3471000000.0,4165000000,169500000.0,58.61731296513905,304.18127250900363,14.854141656662664
2020,3736000000.0,21846000000,3536500000.0,4512000000,165000000.0,62.42058042662272,286.0865469858156,13.347739361702128
2021,3304000000.0,24105000000,3759000000.0,4970000000,220000000.0,50.02945447002696,276.0633802816901,16.156941649899395
2022,3839000000.0,29310000000,5234500000.0,5733000000,303000000.0,47.807403616513135,333.26225361939646,19.290947148090005
2023,4213000000.0,32653000000,5614000000.0,6567000000,357500000.0,47.09352892536673,312.0313689660423,19.870184254606365
"""

INDICATOR_NAME = "现金循环周期 (Cash Conversion Cycle, CCC)"

def json_default(o):
    # convert numpy types and pandas scalars to native Python types for json serialization
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.ndarray,)):
        return o.tolist()
    if hasattr(o, "item"):
        try:
            return o.item()
        except Exception:
            return str(o)
    return str(o)

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are floats for calculation
    # Required columns per formula:
    # Avg Receivables, Revenue, Avg Inventory, Cost of Revenue, Avg Payables
    for col in ["Avg Receivables", "Revenue", "Avg Inventory", "Cost of Revenue", "Avg Payables"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            raise KeyError(f"Required column '{col}' not found in CSV data.")

    # Calculate components per Reference Information
    # DSO = (Avg Receivables / Revenue) * 365
    dso = (df["Avg Receivables"] / df["Revenue"]) * 365.0

    # DIO = (Avg Inventory / Cost of Revenue) * 365
    dio = (df["Avg Inventory"] / df["Cost of Revenue"]) * 365.0

    # DPO = (Avg Payables / Cost of Revenue) * 365
    dpo = (df["Avg Payables"] / df["Cost of Revenue"]) * 365.0

    # CCC = DSO + DIO - DPO
    ccc = dso + dio - dpo

    # Prepare scr_data: mirror input CSV rows as dictionaries
    scr_records = df.copy()
    # If original CSV included computed DSO/DIO/DPO columns, keep them as-is from CSV.
    # Convert to list of dicts
    scr_list = scr_records.to_dict(orient="records")

    # Prepare der_data: one dict per row with Fiscal Year and computed CCC
    der_list = []
    for idx, row in df.iterrows():
        year_value = None
        if "Fiscal Year" in df.columns:
            year_value = row["Fiscal Year"]
        der_entry = {}
        if year_value is not None:
            der_entry["Fiscal Year"] = int(year_value) if (pd.notna(year_value) and float(year_value).is_integer()) else (None if pd.isna(year_value) else year_value)
        # Store computed CCC as float (ensure Python float)
        ccc_value = float(ccc.iloc[idx]) if pd.notna(ccc.iloc[idx]) else None
        der_entry[INDICATOR_NAME] = ccc_value
        der_list.append(der_entry)

    output_obj = {
        "scr_data": scr_list,
        "der_data": der_list
    }

    # Write JSON to file with proper serialization of numpy/pandas scalars
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4, default=json_default)

if __name__ == "__main__":
    main()