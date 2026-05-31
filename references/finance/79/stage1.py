#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Working Capital,Total Assets,Retained Earnings,Operating Income,Market Value of Equity,Total Liabilities,Revenue,X1 (WC/TA),X2 (RE/TA),X3 (EBIT/TA),X4 (MVE/TL),X5 (S/TA)
2016,-2166000000,260078000000,173046000000,-5471000000,145556000000,113356000000,110215000000,-0.0083282707495443,0.6653619298825737,-0.0210359968932397,1.2840608348918452,0.4237767131399041
2017,823000000,253806000000,174106000000,3128000000,148124000000,104487000000,134674000000,0.0032426341378848,0.6859806308755506,0.0123243737342694,1.417630901451855,0.5306178734939284
2018,6850000000,253863000000,180987000000,14446000000,154554000000,98221000000,158902000000,0.0269830577910132,0.7129317781638128,0.0569047084451062,1.5735331548243248,0.6259360363660714
2019,1799000000,237428000000,174945000000,100000000,144213000000,92220000000,139865000000,0.0075770338797445,0.736833903330694,0.0004211803157167,1.563793103448276,0.5890838485772529
2020,3895000000,239790000000,160377000000,-6942000000,131688000000,107064000000,94471000000,0.0162433796238375,0.668822719879895,-0.0289503315400975,1.2299932750504372,0.3939738938237624
2021,6947000000,239535000000,165546000000,16104000000,167378000000,99595000000,155606000000,0.0290020247562986,0.6911140334397896,0.067230258626088,1.680586374818013,0.6496169662053562
2022,16135000000,257709000000,190024000000,50190000000,159282000000,97467000000,246252000000,0.0626093772433248,0.7373588039222534,0.1947545487352013,1.634214657268614,0.955542879759729
2023,8870000000,261632000000,200025000000,33790000000,160957000000,99703000000,196913000000,0.0339025807240704,0.7645280393835616,0.1291508683953033,1.6143646630492563,0.7526334699119374
2024,2353000000,256938000000,205852000000,29099000000,152318000000,103781000000,193414000000,0.0091578513104328,0.8011738240353704,0.1132530026699048,1.4676867634730828,0.752765258544863
"""

INDICATOR_NAME = "奥特曼破产预测模型 (Altman Z-Score)"

def to_serializable(obj):
    # helper for json.dump to convert numpy/pandas types to native python types
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    if pd.isna(obj):
        return None
    # fallback
    try:
        return obj.item()
    except Exception:
        return str(obj)

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    output_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Calculate components for Altman Z-Score per reference:
    # X1 = (Current Assets - Current Liabilities) / Total Assets
    # In provided CSV, "Working Capital" = Current Assets - Current Liabilities
    X1 = df["Working Capital"] / df["Total Assets"]

    # X2 = Retained Earnings / Total Assets
    X2 = df["Retained Earnings"] / df["Total Assets"]

    # X3 = EBIT / Total Assets
    # Using "Operating Income" as EBIT per reference
    X3 = df["Operating Income"] / df["Total Assets"]

    # X4 = Market Value of Equity / Total Liabilities
    X4 = df["Market Value of Equity"] / df["Total Liabilities"]

    # X5 = Revenue / Total Assets
    X5 = df["Revenue"] / df["Total Assets"]

    # Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
    Z = 1.2 * X1 + 1.4 * X2 + 3.3 * X3 + 0.6 * X4 + 1.0 * X5

    # Prepare scr_data: original rows as list of dicts
    scr_records = df.to_dict(orient="records")

    # Prepare der_data: list of dicts with Fiscal Year and computed indicator
    der_records = []
    for idx, row in df.iterrows():
        year_val = row.get("Fiscal Year")
        z_val = float(Z.iloc[idx])  # ensure native float
        der_records.append({
            "Fiscal Year": int(year_val) if not pd.isna(year_val) else None,
            INDICATOR_NAME: z_val
        })

    # Compose final JSON object
    out_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file with converter for numpy types
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, default=to_serializable, indent=4)

if __name__ == "__main__":
    main()