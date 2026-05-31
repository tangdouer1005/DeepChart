#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Working Capital,Total Assets,Retained Earnings,Operating Income,Market Value of Equity,Total Liabilities,Revenue,X1 (WC/TA),X2 (RE/TA),X3 (EBIT/TA),X4 (MVE/TL),X5 (S/TA)
2016,-357000000,33163000000,7686000000,3672000000,12079000000,20831000000,118719000000,-0.0107650091969966,0.2317643156529867,0.1107258088833941,0.5798569439777255,3.5798631004432653
2017,-178000000,36347000000,5988000000,4111000000,10778000000,25268000000,129025000000,-0.004897240487523,0.1647453710072358,0.1131042451921754,0.426547411746082,3.5498115387789912
2018,363000000,40830000000,7887000000,4480000000,12799000000,27727000000,141576000000,0.0088905216752387,0.1931667891256429,0.1097232427136909,0.4616078190933025,3.4674504041146217
2019,248000000,45400000000,10258000000,4737000000,15243000000,29816000000,152703000000,0.0054625550660792,0.2259471365638766,0.1043392070484581,0.51123557821304,3.363502202643172
2020,3276000000,55556000000,12879000000,5435000000,18284000000,36851000000,166761000000,0.0589675282597739,0.2318201454388365,0.097829217366261,0.4961602127486364,3.001673986608107
2021,64000000,59268000000,11666000000,6708000000,17564000000,41190000000,195929000000,0.0010798407234932,0.1968347168792603,0.1131808058311399,0.4264141781985919,3.30581426739556
2022,698000000,64166000000,15585000000,7793000000,20642000000,43519000000,226954000000,0.0108780350964685,0.2428856403702895,0.1214506124738958,0.4743215606976263,3.5369822024124926
2023,2296000000,68994000000,19521000000,8114000000,25058000000,43936000000,242290000000,0.0332782560802388,0.2829376467518915,0.1176044293706699,0.5703295702840495,3.5117546453314783
2024,-1218000000,69831000000,17619000000,9285000000,23622000000,46209000000,254453000000,-0.0174421102375735,0.252309146367659,0.1329638699145078,0.5111991170551191,3.643840128309777
"""

def convert_for_json(o):
    # json can't handle numpy types directly; attempt to extract Python scalar
    try:
        return o.item()
    except Exception:
        return str(o)

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric calculations use numeric dtype
    # Columns used for Altman Z-Score calculation:
    # Working Capital (WC) -> (Current Assets - Current Liabilities)
    # Total Assets (TA)
    # Retained Earnings (RE)
    # Operating Income (EBIT)
    # Market Value of Equity (MVE)
    # Total Liabilities (TL)
    # Revenue (S)
    num_cols = ["Working Capital", "Total Assets", "Retained Earnings", "Operating Income",
                "Market Value of Equity", "Total Liabilities", "Revenue"]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Compute X ratios per Altman model
    # X1 = (Current Assets - Current Liabilities) / Total Assets  => Working Capital / Total Assets
    X1 = df["Working Capital"] / df["Total Assets"]
    # X2 = Retained Earnings / Total Assets
    X2 = df["Retained Earnings"] / df["Total Assets"]
    # X3 = EBIT / Total Assets  -> Operating Income assumed to be EBIT
    X3 = df["Operating Income"] / df["Total Assets"]
    # X4 = Market Value of Equity / Total Liabilities
    X4 = df["Market Value of Equity"] / df["Total Liabilities"]
    # X5 = Sales / Total Assets
    X5 = df["Revenue"] / df["Total Assets"]

    # Altman Z-Score:
    # Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
    Z = 1.2 * X1 + 1.4 * X2 + 3.3 * X3 + 0.6 * X4 + 1.0 * X5

    # Prepare scr_data: replicate input CSV rows as list of dicts
    scr_records = df.copy()
    # Preserve original dtypes where possible; convert NaN to None for JSON
    scr_records = scr_records.where(pd.notnull(scr_records), None)
    scr_list = scr_records.to_dict(orient="records")

    # Prepare der_data: each record with Fiscal Year and computed Altman Z-Score
    der_list = []
    for idx, row in df.iterrows():
        year = int(row["Fiscal Year"]) if not pd.isna(row["Fiscal Year"]) else None
        z_value = Z.iloc[idx]
        der_list.append({
            "Fiscal Year": year,
            "奥特曼破产预测模型 (Altman Z-Score)": z_value
        })

    output_obj = {
        "scr_data": scr_list,
        "der_data": der_list
    }

    # Write JSON to file, handling numpy scalar types
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, default=convert_for_json, indent=4)

if __name__ == "__main__":
    main()