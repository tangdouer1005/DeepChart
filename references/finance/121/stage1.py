import sys
import io
import json
import math
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Dividends,Net Income,Avg Total Assets,ROA(Avg),Retention Ratio
2016,6043000000,6527000000,88633000000.0,0.0736407432897453,0.0741535161636279
2017,6320000000,1248000000,87583000000.0,0.0142493406254638,-4.064102564102564
2018,6644000000,6434000000,85556000000.0,0.0752022067417831,-0.0326391047559837
2019,6845000000,8920000000,84798500000.0,0.1051905399270034,0.2326233183856502
2020,7047000000,7747000000,86838500000.0,0.0892115824202398,0.0903575577642958
2021,7252000000,9771000000,90825000000.0,0.1075805119735755,0.2578037048408556
2022,7616000000,9542000000,93558500000.0,0.1019896642207816,0.2018444770488366
2023,7952000000,10714000000,95233000000.0,0.1125030189115117,0.2577935411610976
2024,8359000000,10631000000,99126000000.0,0.1072473417670439,0.2137146082212397
"""

def to_native(val):
    # Convert pandas/numpy types to native Python types for JSON serialization
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    return val

def compute_igr(net_income, dividends, avg_total_assets):
    # Compute retention ratio b = 1 - (dividends / net_income)
    # Compute ROA = net_income / avg_total_assets
    # IGR = (ROA * b) / (1 - (ROA * b))
    # Handle division by zero and missing data
    try:
        if net_income is None or avg_total_assets is None or dividends is None:
            return None
        if avg_total_assets == 0:
            return None
        # Use floats for calculation
        ni = float(net_income)
        div = float(dividends)
        ata = float(avg_total_assets)
        # retention ratio
        # if net income is zero, retention is undefined -> return None
        if ni == 0:
            return None
        b = 1.0 - (div / ni)
        roa = ni / ata
        product = roa * b
        denom = 1.0 - product
        # protect against division by zero or extremely small denom
        if denom == 0:
            return None
        igr = product / denom
        # return as float
        if not math.isfinite(igr):
            return None
        return float(igr)
    except Exception:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Build scr_data as list of native-type dicts reflecting the input CSV
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Compute derived IGR per row
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = to_native(row["Fiscal Year"])
        dividends = to_native(row["Dividends"])
        net_income = to_native(row["Net Income"])
        avg_total_assets = to_native(row["Avg Total Assets"])
        igr_value = compute_igr(net_income, dividends, avg_total_assets)
        # Optionally round the result to a reasonable number of decimals for readability
        if igr_value is not None:
            # keep high precision but avoid excessive decimals
            igr_value = round(igr_value, 12)
        der_rec = {
            "Fiscal Year": fiscal_year,
            "内部增长率 (Internal Growth Rate, IGR)": igr_value
        }
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