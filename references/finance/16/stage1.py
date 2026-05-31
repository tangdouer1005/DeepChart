#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,CFO,Net Income,Total Assets,Avg Total Assets,CFO per Asset,NI per Asset
2016,3203000000,1400000000,55011000000,49506000000.0,0.0646992283763584,0.0282794004767098
2017,5570000000,477000000,76250000000,65630500000.0,0.0848690776392073,0.0072679623041116
2018,6300000000,2368000000,67173000000,71711500000.0,0.0878520181560837,0.0330212030148581
2019,6136000000,3687000000,67887000000,67530000000.0,0.0908633200059232,0.0545979564637938
2020,7901000000,4495000000,72548000000,70217500000.0,0.1125218072417844,0.0640153807811443
2021,10533000000,7071000000,75196000000,73872000000.0,0.1425844704353476,0.0957196231319038
2022,9581000000,6933000000,74438000000,74817000000.0,0.1280591309461753,0.0926661052969245
2023,7261000000,5723000000,73214000000,73826000000.0,0.0983528838078725,0.0775201148646818
2024,8558000000,13402000000,81414000000,77314000000.0,0.1106914659699407,0.1733450604030318
"""

INDICATOR_NAME = "盈余-现金质量剪刀差 (Earnings Quality Spread)"

def pandas_df_to_pylist(df: pd.DataFrame):
    """
    Convert a pandas DataFrame to a list of dictionaries with native Python types
    so that json.dumps can serialize it without issues (no numpy types).
    """
    def convert_value(v):
        # if it's a pandas / numpy scalar, convert to native Python type
        try:
            if hasattr(v, "item"):
                return v.item()
        except Exception:
            pass
        # Keep None and native types as is
        return v

    records = df.where(pd.notnull(df), None).to_dict(orient="records")
    converted = []
    for rec in records:
        new_rec = {k: convert_value(v) for k, v in rec.items()}
        converted.append(new_rec)
    return converted

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)

    out_path = sys.argv[1]

    # Load CSV data from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are numeric
    # Columns expected: 'CFO', 'Net Income', 'Total Assets'
    # Compute Earnings Quality Spread for each row:
    # Spread = (CFO / Total Assets) - (Net Income / Total Assets)
    # Safely handle division by zero by using None if Total Assets is zero or missing
    spreads = []
    for _, row in df.iterrows():
        fiscal_year = row.get("Fiscal Year")
        cfo = row.get("CFO")
        net_income = row.get("Net Income")
        total_assets = row.get("Total Assets")

        spread_value = None
        try:
            if total_assets is None:
                spread_value = None
            else:
                # Convert to float for division; if total_assets is zero, avoid ZeroDivisionError
                ta = float(total_assets)
                if ta == 0.0:
                    spread_value = None
                else:
                    cfo_f = float(cfo) if cfo is not None else 0.0
                    ni_f = float(net_income) if net_income is not None else 0.0
                    spread_value = (cfo_f / ta) - (ni_f / ta)
        except Exception:
            spread_value = None

        spreads.append({
            "Fiscal Year": int(fiscal_year) if (fiscal_year is not None and str(fiscal_year).isdigit()) else fiscal_year,
            INDICATOR_NAME: spread_value
        })

    # Prepare scr_data from the original dataframe (convert types to native)
    scr_data = pandas_df_to_pylist(df)

    # Ensure der_data values are native Python types as well
    der_data = pandas_df_to_pylist(pd.DataFrame(spreads))

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write output JSON
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()