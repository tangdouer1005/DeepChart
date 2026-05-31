import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,CFO,Operating Income,D&A,Denominator (OpInc+D&A)
2016,13570000000,12660000000,2076000000,14736000000
2017,13876000000,11973000000,2239000000,14212000000
2018,13666000000,12309000000,2191000000,14500000000
2019,15831000000,14219000000,1897000000,16116000000
2020,15426000000,13620000000,1808000000,15428000000
2021,15454000000,12833000000,1862000000,14695000000
2022,13226000000,13969000000,1957000000,15926000000
2023,19886000000,15031000000,1726000000,16757000000
2024,10880000000,12181000000,2507000000,14688000000
"""

INDICATOR_NAME = "自由现金流收益质量 (Quality of Income Ratio)"

def to_primitive(value):
    # Convert pandas/numpy scalar types to native Python types for JSON serialization
    if pd.isna(value):
        return None
    # numpy / pandas scalars often have .item()
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    # fallback: return as-is (likely native python type)
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are numeric
    numeric_cols = ['CFO', 'Operating Income', 'D&A']
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    # Calculate denominator as Operating Income + D&A (do not rely on precomputed Denominator column)
    df['__denominator_calc'] = df['Operating Income'] + df['D&A']

    # Calculate the Quality of Income Ratio for each row
    # Ratio = CFO / (Operating Income + D&A)
    der_records = []
    for _, row in df.iterrows():
        fy = to_primitive(row['Fiscal Year'])
        denom = row['__denominator_calc']
        if pd.isna(denom) or denom == 0:
            ratio = None
        else:
            ratio = float(row['CFO']) / float(denom)
        der_record = {
            "Fiscal Year": fy,
            INDICATOR_NAME: to_primitive(ratio)
        }
        der_records.append(der_record)

    # Prepare scr_data (original scraped data), converting values to native Python types
    scr_records = []
    for rec in df.drop(columns=['__denominator_calc']).to_dict(orient='records'):
        prim = {k: to_primitive(v) for k, v in rec.items()}
        scr_records.append(prim)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to the specified output file
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()