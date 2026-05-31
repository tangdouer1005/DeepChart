import sys
import io
import json
import math
import pandas as pd

CSV_DATA = """Fiscal Year,Dividends,Net Income,Avg Total Assets,ROA(Avg),Retention Ratio
2016,0.0,19478000000,157479000000.0,0.1236863327808787,1.0
2017,0.0,12662000000,182396000000.0,0.0694203820259216,1.0
2022,0.0,59972000000,362266000000.0,0.1655468633545516,1.0
2023,0.0,73795000000,383828000000.0,0.1922605958919099,1.0
2024,7363000000.0,100118000000,426324000000.0,0.2348401685103348,0.926456780998422
"""

def to_native(val):
    # Convert pandas / numpy scalar types to native Python types for JSON serialization
    if pd.isna(val):
        return None
    # For numpy types and pandas scalars
    try:
        return val.item()
    except Exception:
        return val

def calculate_igr(dividends, net_income, avg_total_assets):
    # Compute retention ratio b = 1 - (dividends / net_income)
    # Compute ROA = net_income / avg_total_assets
    # IGR = (ROA * b) / (1 - ROA * b)
    try:
        if net_income is None or avg_total_assets is None or dividends is None:
            return None
        # ensure floats
        net_income = float(net_income)
        dividends = float(dividends)
        avg_total_assets = float(avg_total_assets)
        # Avoid division by zero for net income and avg_total_assets
        if net_income == 0.0 or avg_total_assets == 0.0:
            return None
        b = 1.0 - (dividends / net_income)
        roa = net_income / avg_total_assets
        denom = 1.0 - (roa * b)
        if denom == 0.0:
            return None
        igr = (roa * b) / denom
        # return a native python float
        if math.isfinite(igr):
            return float(igr)
        else:
            return None
    except Exception:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data (raw data) preserving original column names and values
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_data.append(rec)

    # Prepare der_data with calculated IGR for each row
    der_data = []
    for _, row in df.iterrows():
        fiscal_year = to_native(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None
        dividends = to_native(row.get("Dividends")) if "Dividends" in df.columns else None
        net_income = to_native(row.get("Net Income")) if "Net Income" in df.columns else None
        avg_total_assets = to_native(row.get("Avg Total Assets")) if "Avg Total Assets" in df.columns else None

        igr_value = calculate_igr(dividends, net_income, avg_total_assets)

        entry = {}
        if fiscal_year is not None:
            entry["Fiscal Year"] = fiscal_year
        entry["内部增长率 (Internal Growth Rate, IGR)"] = igr_value
        der_data.append(entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to the specified output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()