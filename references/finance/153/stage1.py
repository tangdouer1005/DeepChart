import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Net Income,Interest Expense,Income Tax,Depreciation & Amortization
2016,10217000000,10000000,2301000000.0,2342000000.0
2017,15934000000,6000000,4660000000.0,3025000000.0
2018,22112000000,9000000,3249000000.0,4315000000.0
2019,18485000000,20000000,6327000000.0,5741000000.0
2020,29146000000,672000000,4034000000.0,6862000000.0
2021,39370000000,461000000,7914000000.0,7967000000.0
2022,23200000000,185000000,5619000000.0,8686000000.0
2023,39098000000,446000000,8330000000.0,10382000000.0
2024,62360000000,715000000,8303000000.0,15498000000.0
"""

INDICATOR_NAME = "息税折旧摊销前利润 (Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)"

def to_native(value):
    # Convert numpy scalars and pandas types to native Python types for JSON serialization
    try:
        # numpy/pandas scalar have .item()
        if hasattr(value, "item"):
            return value.item()
    except Exception:
        pass
    # fallback
    return value

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows as list of dicts with original column names
    scr_records = df.to_dict(orient="records")
    # Convert values to native python types
    scr_data = []
    for rec in scr_records:
        native_rec = {k: to_native(v) for k, v in rec.items()}
        scr_data.append(native_rec)

    # Calculate EBITDA per row:
    der_data = []
    for _, row in df.iterrows():
        # Ensure retrieval by column names exactly as CSV header
        net_income = row["Net Income"]
        interest = row["Interest Expense"]
        income_tax = row["Income Tax"]
        da = row["Depreciation & Amortization"]

        # EBITDA = Net Income + Interest Expense + Income Tax + Depreciation + Amortization
        ebitda = net_income + interest + income_tax + da

        entry = {
            "Fiscal Year": to_native(row["Fiscal Year"]),
            INDICATOR_NAME: to_native(ebitda)
        }
        der_data.append(entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to file with ensure_ascii=False to keep Chinese characters readable
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()