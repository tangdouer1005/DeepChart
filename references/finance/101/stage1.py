import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Dividends,Net Income,Avg Total Assets,ROA(Avg),Retention Ratio
2016,3031000000,7009000000,41247500000.0,0.1699254500272743,0.5675559994293051
2017,3404000000,7957000000,42757500000.0,0.1860960065485587,0.5722005781073269
2018,4212000000,8630000000,43747500000.0,0.1972684153380193,0.5119351100811125
2019,4704000000,11121000000,44266000000.0,0.251231193240862,0.5770164553547343
2020,5958000000,11242000000,47619500000.0,0.2360797572423062,0.4700231275573742
2021,6451000000,12866000000,60908500000.0,0.211234885114557,0.4986009637805068
2022,6985000000,16433000000,71228500000.0,0.2307082137065921,0.5749406681677114
2023,7789000000,17105000000,74160500000.0,0.2306483909898126,0.5446360713241742
2024,8383000000,15143000000,76487500000.0,0.1979800621016506,0.4464108829161989
"""

INDICATOR_NAME = "内部增长率 (Internal Growth Rate, IGR)"

def to_native(value):
    # Convert pandas/numpy scalars to native Python types for JSON serialization
    try:
        # pandas/numpy scalars have .item()
        return value.item()
    except Exception:
        # fallback: handle NaN
        try:
            if pd.isna(value):
                return None
        except Exception:
            pass
        return value

def calculate_igr(dividends, net_income, avg_total_assets):
    # Retention ratio b = 1 - (Dividends / Net Income)
    # ROA = Net Income / Avg Total Assets
    # IGR = (ROA * b) / (1 - ROA * b)
    if net_income is None or avg_total_assets is None:
        return None
    try:
        if net_income == 0 or avg_total_assets == 0:
            return None
        b = 1.0 - (dividends / net_income)
        roa = net_income / avg_total_assets
        denom = 1.0 - (roa * b)
        if denom == 0:
            return None
        igr = (roa * b) / denom
        return float(igr)
    except Exception:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: list of dicts matching the input CSV rows
    scr_records = []
    for _, row in df.iterrows():
        record = {}
        for col in df.columns:
            record[col] = to_native(row[col])
        scr_records.append(record)

    # Prepare der_data: compute IGR for each row
    der_records = []
    for _, row in df.iterrows():
        dividends = to_native(row["Dividends"])
        net_income = to_native(row["Net Income"])
        avg_assets = to_native(row["Avg Total Assets"])
        igr_value = calculate_igr(dividends, net_income, avg_assets)

        der_record = {
            "Fiscal Year": to_native(row["Fiscal Year"]),
            INDICATOR_NAME: igr_value
        }
        der_records.append(der_record)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()