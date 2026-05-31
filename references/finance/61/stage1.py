#!/usr/bin/env python3
import sys
import io
import json
import math
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Dividends,Net Income,Avg Total Assets,ROA(Avg),Retention Ratio
2016,4750000000.0,10739000000,117512500000.0,0.0913860227635357,0.5576869354688518
2017,5511000000.0,9609000000,125735000000.0,0.0764226349067483,0.4264751795192008
2018,5968000000.0,110000000,119301000000.0,0.0009220375353098,-53.25454545454546
2019,5979000000.0,11621000000,103288500000.0,0.1125101051908005,0.4855003872300146
2020,6016000000.0,11214000000,96323000000.0,0.1164207925417605,0.4635277331906545
2021,6163000000.0,10591000000,96175000000.0,0.1101221731219131,0.4180908318383532
2022,6224000000.0,11812000000,95749500000.0,0.1233635684781643,0.4730782255333559
2023,6302000000.0,12613000000,97927000000.0,0.1288000245080519,0.5003567747562039
2024,6384000000.0,10320000000,113132500000.0,0.0912204715709455,0.3813953488372092
"""

INDICATOR_NAME = "内部增长率 (Internal Growth Rate, IGR)"

def to_native(obj):
    """Recursively convert numpy/pandas types to native Python types for JSON serialization."""
    if isinstance(obj, dict):
        return {to_native(k): to_native(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_native(i) for i in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        v = float(obj)
        if math.isnan(v):
            return None
        return v
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if pd.isna(obj):
        return None
    return obj

def compute_igr(row):
    """
    Compute Internal Growth Rate (IGR) for a single row.
    Formula:
      b = 1 - (Dividends / Net Income)
      ROA = Net Income / Avg Total Assets
      IGR = (ROA * b) / (1 - (ROA * b))
    Returns float or None if cannot be computed (e.g., division by zero).
    """
    try:
        dividends = float(row["Dividends"])
        net_income = float(row["Net Income"])
        avg_total_assets = float(row["Avg Total Assets"])
    except Exception:
        return None

    # Compute retention ratio b. If net_income is 0, this will be infinite/undefined; handle that.
    if net_income == 0:
        # If company made zero net income, cannot retain earnings meaningfully; treat as None
        return None
    b = 1.0 - (dividends / net_income)

    # Compute ROA
    if avg_total_assets == 0:
        return None
    roa = net_income / avg_total_assets

    numerator = roa * b
    denom = 1.0 - numerator
    # If denom is zero, IGR would be infinite; return None to indicate undefined/unstable.
    if math.isclose(denom, 0.0, rel_tol=1e-12, abs_tol=1e-12):
        return None

    igr = numerator / denom
    # Return as native float
    return float(igr)

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Build scr_data: list of dicts reflecting original CSV rows
    scr_records = df.to_dict(orient="records")
    scr_records = [to_native(r) for r in scr_records]

    # Compute derived IGR for each row
    der_records = []
    for idx, row in df.iterrows():
        igr_value = compute_igr(row)
        rec = {}
        # Include year if present
        if "Fiscal Year" in df.columns:
            rec["Fiscal Year"] = to_native(row["Fiscal Year"])
        rec[INDICATOR_NAME] = to_native(igr_value)
        der_records.append(rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON with UTF-8 and ensure Chinese keys are preserved
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()