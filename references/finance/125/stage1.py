import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Net Income,Interest Expense,Income Tax,Depreciation & Amortization
2016,6527000000,733000000,1586000000,1787000000
2017,1248000000,853000000,5607000000,1260000000
2018,6434000000,950000000,1749000000,1086000000
2019,8920000000,946000000,1801000000,1365000000
2020,7747000000,1437000000,1981000000,1536000000
2021,9771000000,1597000000,2621000000,1452000000
2022,9542000000,882000000,2115000000,1260000000
2023,10714000000,1527000000,2249000000,1128000000
2024,10631000000,1656000000,2437000000,1075000000
"""

INDICATOR_NAME = "息税折旧摊销前利润 (Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)"

def to_native(v):
    # Convert numpy / pandas numeric types to native Python int/float for JSON serialization
    if v is None:
        return None
    if isinstance(v, (str, bool)):
        return v
    try:
        # Try integer conversion first
        iv = int(v)
        # If converting to int didn't change value (covers numpy ints and exact integers), keep int
        if float(iv) == float(v):
            return iv
    except Exception:
        pass
    try:
        return float(v)
    except Exception:
        # Fallback: return as-is (likely a string or already native)
        return v

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: raw rows as list of dictionaries, with native Python types
    raw_records = df.to_dict(orient='records')
    scr_data = []
    for rec in raw_records:
        sanitized = {k: to_native(v) for k, v in rec.items()}
        scr_data.append(sanitized)

    # Calculate EBITDA for each row dynamically
    der_data = []
    for idx, row in df.iterrows():
        # Extract required components by column names from the CSV
        net_income = row["Net Income"]
        interest = row["Interest Expense"]
        income_tax = row["Income Tax"]
        da = row["Depreciation & Amortization"]

        # EBITDA = Net Income + Interest Expense + Income Tax + Depreciation + Amortization
        ebitda = net_income + interest + income_tax + da

        entry = {}
        # Include the Fiscal Year if present in the data
        if "Fiscal Year" in row:
            entry["Fiscal Year"] = to_native(row["Fiscal Year"])
        entry[INDICATOR_NAME] = to_native(ebitda)
        der_data.append(entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to the specified output file (ensure Chinese characters are preserved)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()