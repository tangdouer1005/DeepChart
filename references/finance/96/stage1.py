import sys
import io
import json
import pandas as pd

def to_native(value):
    # Convert pandas/numpy scalars to native Python types for JSON serialization
    if pd.isna(value):
        return None
    # numpy/pandas scalars expose .item()
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    return value

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    csv_data = """Fiscal Year,CFO,Net Income,Total Assets,Avg Total Assets,CFO per Asset,NI per Asset
2016,36036000000,19478000000,167497000000,157479000000.0,0.2288305107347646,0.1236863327808787
2017,37091000000,12662000000,197295000000,182396000000.0,0.2033542402245663,0.0694203820259216
2018,47971000000,30736000000,232792000000,215043500000.0,0.223075796292378,0.1429292212970864
2019,54520000000,34343000000,275909000000,254350500000.0,0.2143498833302863,0.1350223412181222
2020,65124000000,40269000000,319616000000,297762500000.0,0.2187112211913857,0.1352386549683052
2021,91652000000,76033000000,359268000000,339442000000.0,0.2700078363903112,0.2239940844091185
2022,91495000000,59972000000,365264000000,362266000000.0,0.2525630337928483,0.1655468633545516
2023,101746000000,73795000000,402392000000,383828000000.0,0.2650822764363204,0.1922605958919099
2024,125299000000,100118000000,450256000000,426324000000.0,0.2939055741642506,0.2348401685103348
"""

    df = pd.read_csv(io.StringIO(csv_data))

    # Prepare scr_data from input CSV (convert types to native)
    scr_records = []
    for rec in df.to_dict(orient="records"):
        native_rec = {k: to_native(v) for k, v in rec.items()}
        scr_records.append(native_rec)

    # Calculate Earnings Quality Spread for each row:
    # Spread = (CFO / Total Assets) - (Net Income / Total Assets)
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = to_native(row["Fiscal Year"])
        total_assets = row["Total Assets"]
        cfo = row["CFO"]
        net_income = row["Net Income"]

        try:
            # Protect against division by zero
            if total_assets == 0 or pd.isna(total_assets):
                spread = None
            else:
                spread = float((cfo / total_assets) - (net_income / total_assets))
        except Exception:
            spread = None

        der_rec = {
            "Fiscal Year": fiscal_year,
            "盈余-现金质量剪刀差 (Earnings Quality Spread)": to_native(spread)
        }
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()