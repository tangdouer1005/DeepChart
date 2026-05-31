#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Net Income,Total Assets,Avg Total Assets,CFO per Asset,NI per Asset
2016,10376000000,3920000000,95377000000,98527000000.0,0.1053112344839485,0.0397860484943213
2017,6447000000,2394000000,87872000000,91624500000.0,0.0703632761979601,0.0261283826924021
2018,10922000000,6220000000,82637000000,85254500000.0,0.1281105396196095,0.072958025676064
2019,13440000000,9843000000,84397000000,83517000000.0,0.1609253205934121,0.1178562448363806
2020,10253000000,7067000000,91588000000,87992500000.0,0.1165212944285024,0.0803136630962866
2021,14109000000,13049000000,105694000000,98641000000.0,0.1430338297462515,0.1322877910807879
2022,19095000000,14519000000,109160000000,107427000000.0,0.1777486106844648,0.1351522429184469
2023,13006000000,365000000,106675000000,107917500000.0,0.1205179882780828,0.0033822132647624
2024,21468000000,17117000000,117106000000,111890500000.0,0.1918661548567573,0.1529799223347826
"""

INDICATOR_NAME = "盈余-现金质量剪刀差 (Earnings Quality Spread)"

def to_native(val):
    if pd.isna(val):
        return None
    # numpy scalar types
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, (np.bool_,)):
        return bool(val)
    # plain python types (int/float/str) left as is
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Calculation:
    # Spread = (CFO / Total Assets) - (Net Income / Total Assets)
    # Compute using raw columns to avoid hardcoding results.
    # Ensure float division
    df_calc = df.copy()
    # Protect against division by zero
    df_calc["Spread"] = df_calc.apply(
        lambda r: (float(r["CFO"]) / float(r["Total Assets"]) - float(r["Net Income"]) / float(r["Total Assets"]))
        if (pd.notna(r["CFO"]) and pd.notna(r["Net Income"]) and pd.notna(r["Total Assets"]) and float(r["Total Assets"]) != 0)
        else None,
        axis=1
    )

    # Prepare scr_data: original rows as list of dicts, with native python types
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_data.append(rec)

    # Prepare der_data: one dict per row with Fiscal Year and calculated indicator
    der_data = []
    for _, row in df_calc.iterrows():
        fy = to_native(row["Fiscal Year"]) if "Fiscal Year" in df_calc.columns else None
        val = to_native(row["Spread"])
        entry = {}
        # include Fiscal Year if present in input
        if fy is not None:
            entry["Fiscal Year"] = fy
        entry[INDICATOR_NAME] = val
        der_data.append(entry)

    out_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()