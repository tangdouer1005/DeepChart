import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Cash & Equiv,Receivables,Operating Expenses,Cost of Revenue,Quick Assets,Daily Burn
2016,8903000000.0,3993000000.0,11422000000,3789000000,12896000000.0,41673972.60273973
2017,8079000000.0,5832000000.0,14996000000,5454000000,13911000000.0,56027397.26027397
2018,10019000000.0,7587000000.0,21570000000,9355000000,17606000000.0,84726027.39726028
2019,19079000000.0,9518000000.0,33941000000,12770000000,28597000000.0,127975342.46575342
2020,17576000000.0,11335000000.0,36602000000,16692000000,28911000000.0,146010958.9041096
2021,16601000000.0,14039000000.0,48527000000,22649000000,30640000000.0,195002739.7260274
2022,14681000000.0,13466000000.0,62416000000,25249000000,28147000000.0,240178082.19178084
2023,41862000000.0,16169000000.0,62192000000,25959000000,58031000000.0,241509589.04109588
2024,43889000000.0,16994000000.0,64960000000,30161000000,60883000000.0,260605479.4520548
"""

INDICATOR_KEY = "防御区间比率 (Defensive Interval Ratio, DIR)"

def to_py_val(v):
    # Convert pandas / numpy scalars to native Python types for JSON serialization
    if pd.isna(v):
        return None
    try:
        # numpy scalar has .item()
        return v.item()
    except Exception:
        return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Build scr_data as records with native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_py_val(row[col])
        scr_records.append(rec)

    # Calculate DIR for each row:
    # Quick Assets = use "Quick Assets" column (raw data)
    # Daily cash consumption = (Operating Expenses + Cost of Revenue) / 365
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = to_py_val(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None
        operating_expenses = row["Operating Expenses"] if "Operating Expenses" in df.columns else 0.0
        cost_of_revenue = row["Cost of Revenue"] if "Cost of Revenue" in df.columns else 0.0
        quick_assets = row["Quick Assets"] if "Quick Assets" in df.columns else None

        # compute daily cash consumption per reference:
        daily_cash_consumption = (operating_expenses + cost_of_revenue) / 365.0

        # Defensive Interval Ratio:
        dir_value = None
        if quick_assets is None or pd.isna(quick_assets) or daily_cash_consumption == 0:
            dir_value = None
        else:
            dir_value = float(quick_assets) / float(daily_cash_consumption)

        rec = {}
        if fiscal_year is not None:
            rec["Fiscal Year"] = fiscal_year
        rec[INDICATOR_KEY] = to_py_val(dir_value)
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()