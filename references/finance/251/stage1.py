#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Operating Income,Income Tax,Pretax Income,Effective Tax Rate,NOPAT,Avg Invested Capital
2016,12930000000,4790000000,11863000000,0.403776447778808,7709170530.220012,57916500000.0
2017,15209000000,3200000000,14023000000,0.2281965342651358,11738358910.36155,65240500000.0
2018,17344000000,3562000000,15944000000,0.2234069242348218,13469230306.071247,73464000000.0
2019,19685000000,3742000000,17981000000,0.2081085590345364,15588383015.405151,82346500000.0
2020,22405000000,4973000000,20742000000,0.2397550862983319,17033287291.485874,89673000000.0
2021,23970000000,4578000000,22310000000,0.2051994621246078,19051368892.87315,94212500000.0
2022,28435000000,5704000000,26343000000,0.2165281099343279,22278023194.017387,104209000000.0
2023,32358000000,5968000000,29112000000,0.2050013740038472,25724565539.983517,119467000000.0
2024,32287000000,4829000000,20071000000,0.2405958846096358,24518880673.60869,135577000000.0
"""

INDICATOR_NAME = "投入资本回报率 (Return on Invested Capital, ROIC)"

def scalarify(v):
    # Convert numpy and pandas scalar types to native Python types for JSON serialization
    if v is None:
        return None
    if isinstance(v, (np.generic,)):
        try:
            return v.item()
        except Exception:
            pass
    # pandas NA (pd.NA) handling
    try:
        if pd.isna(v):
            return None
    except Exception:
        pass
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows as dictionaries with Python-native types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = scalarify(row[col])
        scr_records.append(rec)

    # Calculate ROIC per reference:
    # NOPAT = Operating Income * (1 - Effective Tax Rate)
    # Invested Capital = Avg Invested Capital (using provided column as proxy)
    der_records = []
    for _, row in df.iterrows():
        # Extract values with safe conversions
        op_income = scalarify(row.get("Operating Income"))
        eff_tax = scalarify(row.get("Effective Tax Rate"))
        invested_cap = scalarify(row.get("Avg Invested Capital"))
        fiscal_year = scalarify(row.get("Fiscal Year"))

        # Ensure numeric types for calculation
        try:
            op_income_f = float(op_income) if op_income is not None else None
        except Exception:
            op_income_f = None
        try:
            eff_tax_f = float(eff_tax) if eff_tax is not None else None
        except Exception:
            eff_tax_f = None
        try:
            invested_cap_f = float(invested_cap) if invested_cap is not None else None
        except Exception:
            invested_cap_f = None

        roic_value = None
        # compute NOPAT from Operating Income and Effective Tax Rate if possible
        if (op_income_f is not None) and (eff_tax_f is not None) and (invested_cap_f is not None):
            try:
                nopat_calc = op_income_f * (1.0 - eff_tax_f)
                # Avoid division by zero or near-zero invested capital
                if invested_cap_f != 0:
                    roic_value = nopat_calc / invested_cap_f
                else:
                    roic_value = None
            except Exception:
                roic_value = None

        # Build record; include Fiscal Year if present
        rec = {}
        if fiscal_year is not None:
            rec["Fiscal Year"] = fiscal_year
        rec[INDICATOR_NAME] = scalarify(roic_value)
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()