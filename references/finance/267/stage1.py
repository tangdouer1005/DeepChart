#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Working Capital,Total Assets,Retained Earnings,Operating Income,Market Value of Equity,Total Liabilities,Revenue,X1 (WC/TA),X2 (RE/TA),X3 (EBIT/TA),X4 (MVE/TL),X5 (S/TA)
2016,6267000000,64035000000,10462000000,7883000000,32912000000,31123000000,15082000000,0.0978683532443195,0.1633794018895916,0.1231045521980167,1.0574816052437104,0.2355274459280081
2017,9029000000,67977000000,9508000000,12144000000,32760000000,35217000000,18358000000,0.1328243376436147,0.1398708386660193,0.1786486605763714,0.9302325581395348,0.2700619327125351
2018,6911000000,69225000000,11318000000,12954000000,34006000000,35219000000,20609000000,0.0998338750451426,0.1634958468761285,0.1871289274106175,0.965558363383401,0.2977103647526182
2019,7555000000,72574000000,13502000000,15001000000,34684000000,37890000000,22977000000,0.1041006421032325,0.1860445889712569,0.2066993689199989,0.9153866455529164,0.3166009865792157
2020,13135000000,80919000000,14088000000,14081000000,36210000000,44709000000,21846000000,0.1623228166438043,0.1741000259518778,0.174013519692532,0.8099040461652016,0.2699736773810848
2021,11868000000,82896000000,15351000000,15804000000,37589000000,45307000000,24105000000,0.1431673422119282,0.1851838448176027,0.1906485234510712,0.8296510472995343,0.290786045165026
2022,9352000000,85501000000,16116000000,18813000000,35581000000,49920000000,29310000000,0.1093788376744131,0.1884890235201927,0.2200325142395995,0.7127604166666667,0.3428030081519514
2023,10434000000,90499000000,18040000000,21000000000,38733000000,51766000000,32653000000,0.1152940916474215,0.1993392192178919,0.2320467629476569,0.7482324305528726,0.3608106166918971
2024,7516000000,94511000000,17289000000,23595000000,39137000000,55374000000,35926000000,0.0795251346404122,0.1829310873866534,0.24965347948916,0.7067757431285441,0.3801250648072711
"""

def to_native(val):
    # Convert numpy types to native Python types for JSON serialization
    if pd.isna(val):
        return None
    if isinstance(val, (np.generic,)):
        return val.item()
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are numeric
    numeric_cols = ["Working Capital", "Total Assets", "Retained Earnings", "Operating Income",
                    "Market Value of Equity", "Total Liabilities", "Revenue"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Calculate components for Altman Z-Score dynamically:
    # X1 = (Current Assets - Current Liabilities) / Total Assets
    # Here "Working Capital" is (Current Assets - Current Liabilities)
    df["X1_calc"] = df["Working Capital"] / df["Total Assets"]

    # X2 = Retained Earnings / Total Assets
    df["X2_calc"] = df["Retained Earnings"] / df["Total Assets"]

    # X3 = EBIT / Total Assets. Use "Operating Income" as EBIT.
    df["X3_calc"] = df["Operating Income"] / df["Total Assets"]

    # X4 = Market Value of Equity / Total Liabilities
    # If Total Liabilities is zero, avoid division by zero by using NaN.
    df["X4_calc"] = df["Market Value of Equity"] / df["Total Liabilities"].replace({0: np.nan})

    # X5 = Revenue / Total Assets
    df["X5_calc"] = df["Revenue"] / df["Total Assets"]

    # Altman Z-Score: Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
    df["奥特曼破产预测模型 (Altman Z-Score)"] = (
        1.2 * df["X1_calc"]
        + 1.4 * df["X2_calc"]
        + 3.3 * df["X3_calc"]
        + 0.6 * df["X4_calc"]
        + 1.0 * df["X5_calc"]
    )

    # Prepare scr_data: original CSV rows as list of dicts, with native types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            # We want scr_data to reflect the original input columns only.
            # The original CSV header columns are up to "Revenue" and the provided X1..X5.
            # To match "scr_data" requirement, include the original CSV header fields.
            # Therefore, collect those fields from the original CSV.
            pass

    # Build scr_data from the original CSV (not including our calc columns)
    original_columns = ["Fiscal Year", "Working Capital", "Total Assets", "Retained Earnings",
                        "Operating Income", "Market Value of Equity", "Total Liabilities",
                        "Revenue", "X1 (WC/TA)", "X2 (RE/TA)", "X3 (EBIT/TA)", "X4 (MVE/TL)", "X5 (S/TA)"]
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in original_columns:
            if col in df.columns:
                rec[col] = to_native(row[col])
            else:
                rec[col] = None
        scr_data.append(rec)

    # Build der_data: calculated Altman Z-Score per row, include Fiscal Year
    der_data = []
    for _, row in df.iterrows():
        der_rec = {
            "Fiscal Year": to_native(row["Fiscal Year"]),
            "奥特曼破产预测模型 (Altman Z-Score)": to_native(row["奥特曼破产预测模型 (Altman Z-Score)"])
        }
        der_data.append(der_rec)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write to output JSON file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()