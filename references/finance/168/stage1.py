#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,ROA(Avg),CFO,Net Income,Long Term Debt,Avg Total Assets,Leverage,Current Ratio,Current Assets,Current Liabilities,Shares,Gross Margin,Revenue,Cost of Revenue,Asset Turnover (for F-score),1_ROA>0,2_CFO>0,3_dROA>0,4_CFO>NI,5_dLev<0,6_dCurrent>0,7_NoDilute,8_dMargin>0,9_dTurnover>0
2016,0.0397860484943213,10376000000,3920000000,24274000000,98527000000.0,0.2463690155997848,1.7794698907230877,30614000000,17204000000,2787000000,0.6475494259803553,39807000000,14030000000,0.4040212327585332,1,1,0,1,0,1,1,1,1
2017,0.0261283826924021,6447000000,2394000000,21353000000,91624500000.0,0.2330490207313546,1.330503921779306,24766000000,18614000000,2748000000,0.6781815462838343,40122000000,12912000000,0.4378959776042434,1,1,0,1,1,0,1,1,1
2018,0.072958025676064,10922000000,6220000000,19806000000,85254500000.0,0.2323161827234926,1.16522561469873,25875000000,22206000000,2679000000,0.6805929919137467,42294000000,13509000000,0.4960911154249922,1,1,1,1,1,0,1,1,1
2019,0.1178562448363806,13440000000,9843000000,22736000000,83517000000.0,0.2722320006705221,1.2368586858685868,27483000000,22220000000,2580000000,0.6928503872600393,39121000000,12016000000,0.4684196031945591,1,1,1,1,0,1,1,1,0
2020,0.0803136630962866,10253000000,7067000000,25360000000,87992500000.0,0.2882063812256726,1.0159915102279795,27764000000,27327000000,2541000000,0.6719976877498917,41518000000,13618000000,0.4718356678125976,1,1,0,1,0,0,1,0,1
2021,0.1322877910807879,14109000000,13049000000,30690000000,98641000000.0,0.3111282326821504,1.2678451742627346,30266000000,23872000000,2538000000,0.7202283180026281,48704000000,13626000000,0.493750063361077,1,1,1,1,0,1,1,1,1
2022,0.1351522429184469,19095000000,14519000000,28745000000,107427000000.0,0.2675770523239036,1.473740665869054,35722000000,24239000000,2542000000,0.7063070357438052,59283000000,17411000000,0.5518445083638192,1,1,1,1,1,1,0,0,1
2023,0.0033822132647624,13006000000,365000000,33683000000,0.3121180531424468,0.3121180531424468,1.251965439402195,32168000000,25694000000,2547000000,0.731747483989021,60115000000,16126000000,0.557045891537517,1,1,0,1,0,0,0,1,1
2024,0.1529799223347826,21468000000,17117000000,34462000000,111890500000.0,0.307997551177267,1.3646023926812103,38782000000,28420000000,2541000000,0.7632308939035033,64168000000,15193000000,0.5734892595886156,1,1,1,1,1,1,1,1,1
"""

def to_python_native(val):
    # Convert numpy/pandas scalar to native python types for JSON serialization
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, (np.bool_,)):
        return bool(val)
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA), dtype=object)

    # Some CSV rows might have misaligned columns due to numeric formatting; ensure numeric columns are cast where possible
    # Define columns we'll use for F-Score calculations
    cols_numeric = [
        "ROA(Avg)", "CFO", "Net Income", "Leverage", "Current Ratio",
        "Shares", "Gross Margin", "Asset Turnover (for F-score)"
    ]
    # Also ensure Fiscal Year exists
    if "Fiscal Year" not in df.columns:
        raise ValueError("CSV must contain 'Fiscal Year' column")

    # Safely coerce numeric columns to floats/ints
    for c in cols_numeric:
        if c in df.columns:
            # Some values may be strings; coerce
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Ensure Shares are integers if present
    if "Shares" in df.columns:
        df["Shares"] = pd.to_numeric(df["Shares"], errors="coerce").astype("Int64")

    # Build scr_data: original rows as dictionaries with native python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_native(row[col])
        scr_records.append(rec)

    # Compute Piotroski F-Score per row
    fscore_name = "皮奥特罗斯基 F-Score (Piotroski F-Score)"
    der_records = []
    for idx in range(len(df)):
        row = df.iloc[idx]
        prev = df.iloc[idx - 1] if idx > 0 else None

        score = 0

        # 1. ROA > 0
        roa = row.get("ROA(Avg)")
        if pd.notna(roa) and float(roa) > 0:
            score += 1

        # 2. CFO > 0
        cfo = row.get("CFO")
        if pd.notna(cfo) and float(cfo) > 0:
            score += 1

        # 3. ΔROA > 0 (current ROA > prior ROA)
        if prev is not None and pd.notna(prev.get("ROA(Avg)")) and pd.notna(roa):
            if float(roa) > float(prev.get("ROA(Avg)")):
                score += 1
        # else: no prior -> no point

        # 4. Accruals: CFO > Net Income
        ni = row.get("Net Income")
        if pd.notna(cfo) and pd.notna(ni) and float(cfo) > float(ni):
            score += 1

        # 5. ΔLeverage < 0 (leverage decreased)
        lev = row.get("Leverage")
        if prev is not None and pd.notna(prev.get("Leverage")) and pd.notna(lev):
            if float(lev) < float(prev.get("Leverage")):
                score += 1

        # 6. ΔCurrent Ratio > 0 (current ratio increased)
        cr = row.get("Current Ratio")
        if prev is not None and pd.notna(prev.get("Current Ratio")) and pd.notna(cr):
            if float(cr) > float(prev.get("Current Ratio")):
                score += 1

        # 7. No Dilution: Shares this year <= Shares last year
        shares = row.get("Shares")
        if prev is not None and pd.notna(prev.get("Shares")) and pd.notna(shares):
            # if current shares less than or equal to prior -> no dilution
            try:
                if int(shares) <= int(prev.get("Shares")):
                    score += 1
            except Exception:
                pass  # if conversion fails, don't award point

        # 8. ΔGross Margin > 0
        gm = row.get("Gross Margin")
        if prev is not None and pd.notna(prev.get("Gross Margin")) and pd.notna(gm):
            if float(gm) > float(prev.get("Gross Margin")):
                score += 1

        # 9. ΔAsset Turnover > 0
        at = row.get("Asset Turnover (for F-score)")
        if prev is not None and pd.notna(prev.get("Asset Turnover (for F-score)")) and pd.notna(at):
            if float(at) > float(prev.get("Asset Turnover (for F-score)")):
                score += 1

        der_rec = {
            "Fiscal Year": to_python_native(row.get("Fiscal Year")),
            fscore_name: to_python_native(int(score))
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