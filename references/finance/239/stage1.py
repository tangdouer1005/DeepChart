#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,NOPAT,Avg Invested Capital,WACC,Capital Charge
2016,2541039965.620971,35092000000.0,0.1,3509200000.0
2017,2761774122.1132555,36308000000.0,0.1,3630800000.0
2018,3914320142.966556,36197000000.0,0.1,3619700000.0
2019,4311078861.611992,39404500000.0,0.1,3940450000.0
2020,5158409065.155808,83893500000.0,0.1,8389350000.0
2021,6219459265.890779,133754000000.0,0.1,13375400000.0
2022,5386640178.003815,141495500000.0,0.1,14149550000.0
2023,10787373579.416311,140967500000.0,0.1,14096750000.0
2024,13880872077.21588,139833000000.0,0.1,13983300000.0
"""

INDICATOR_NAME = "经济增加值 (Economic Value Added, EVA) - 简化版"

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python this.py output.json\n")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are numeric
    numeric_cols = ["NOPAT", "Avg Invested Capital", "WACC"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Calculation: EVA = NOPAT - (Invested Capital * WACC)
    # Here we use "Avg Invested Capital" as the invested capital proxy provided in the data
    df["EVA_calculated"] = df["NOPAT"] - (df["Avg Invested Capital"] * df["WACC"])

    # Prepare scr_data: original rows as dictionaries
    scr_data = []
    # Convert types to native python types for JSON serialization
    for rec in df.drop(columns=["EVA_calculated"]).to_dict(orient="records"):
        # convert numpy types to python native
        clean_rec = {}
        for k, v in rec.items():
            if pd.isna(v):
                clean_rec[k] = None
            else:
                # if it's a float that is actually an integer value (like Fiscal Year), preserve int
                if isinstance(v, float) and v.is_integer():
                    clean_rec[k] = int(v)
                else:
                    clean_rec[k] = v
        scr_data.append(clean_rec)

    # Prepare der_data: calculated EVA per row. Include Fiscal Year if present.
    der_data = []
    for _, row in df.iterrows():
        eva_value = row["EVA_calculated"]
        # convert to native python number and handle NaN
        if pd.isna(eva_value):
            eva_out = None
        else:
            eva_out = float(eva_value)
        entry = {}
        # include Fiscal Year if present
        if "Fiscal Year" in df.columns:
            fy = row["Fiscal Year"]
            # cast to int if appropriate
            if pd.isna(fy):
                entry["Fiscal Year"] = None
            else:
                entry["Fiscal Year"] = int(fy) if float(fy).is_integer() else fy
        entry[INDICATOR_NAME] = eva_out
        der_data.append(entry)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON output
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()