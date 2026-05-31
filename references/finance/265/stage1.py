import sys
import io
import json
import pandas as pd
import numbers

CSV_DATA = """Fiscal Year,Net Income,Operating Cashflow,Accruals,Avg Total Assets
2016,5991000000,5574000000,417000000,51701000000.0
2017,6699000000,9208000000,-2509000000,66006000000.0
2018,10301000000,12713000000,-2412000000,68601000000.0
2019,12080000000,12784000000,-704000000,70899500000.0
2020,10866000000,10440000000,426000000,76746500000.0
2021,12311000000,15227000000,-2916000000,81907500000.0
2022,14957000000,18849000000,-3892000000,84198500000.0
2023,17273000000,20755000000,-3482000000,88000000000.0
2024,19743000000,19950000000,-207000000,92505000000.0
"""

INDICATOR_NAME = "斯隆比率 (Sloan Ratio / Accruals Ratio)"

def to_native(val):
    # Convert numpy/pandas types to native Python types for JSON serialization
    if pd.isna(val):
        return None
    if isinstance(val, (int, float, str, bool)) and not isinstance(val, (pd.Series, pd.DataFrame)):
        # Ensure numpy types are converted
        if isinstance(val, numbers.Integral):
            return int(val)
        if isinstance(val, numbers.Real):
            return float(val)
        return val
    try:
        # Fallback conversions
        if hasattr(val, "item"):
            item = val.item()
            if isinstance(item, numbers.Integral):
                return int(item)
            if isinstance(item, numbers.Real):
                return float(item)
            return item
    except Exception:
        pass
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data (source data) as list of dicts with native types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Calculate Sloan Ratio for each row
    der_records = []
    for _, row in df.iterrows():
        # Prefer computing accruals from Net Income and Operating Cashflow per definition
        ni = row.get("Net Income", None)
        cfo = row.get("Operating Cashflow", None)
        avg_assets = row.get("Avg Total Assets", None)

        # Convert to numeric (floats) for calculation; handle missing values
        try:
            ni_val = float(ni) if not pd.isna(ni) else None
        except Exception:
            ni_val = None
        try:
            cfo_val = float(cfo) if not pd.isna(cfo) else None
        except Exception:
            cfo_val = None
        try:
            assets_val = float(avg_assets) if not pd.isna(avg_assets) else None
        except Exception:
            assets_val = None

        accruals_calc = None
        if (ni_val is not None) and (cfo_val is not None):
            accruals_calc = ni_val - cfo_val  # Accruals = Net Income - CFO

        sloan = None
        if (accruals_calc is not None) and (assets_val not in (None, 0)):
            sloan = accruals_calc / assets_val

        der_rec = {}
        # Include fiscal year if present
        if "Fiscal Year" in df.columns:
            der_rec["Fiscal Year"] = to_native(row["Fiscal Year"])
        der_rec[INDICATOR_NAME] = to_native(sloan)
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()