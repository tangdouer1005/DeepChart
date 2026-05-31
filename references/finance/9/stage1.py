#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,ROA(Avg),CFO,Net Income,Long Term Debt,Avg Total Assets,Leverage,Current Ratio,Current Assets,Current Liabilities,Shares,Gross Margin,Revenue,Cost of Revenue,Asset Turnover (for F-score),1_ROA>0,2_CFO>0,3_dROA>0,4_CFO>NI,5_dLev<0,6_dCurrent>0,7_NoDilute,8_dMargin>0,9_dTurnover>0
2016,0.0999253036114445,7041000000,5953000000,36440000000.0,59574500000.0,0.6116711008904817,1.6549432573356508,16187000000.0,9781000000.0,1631000000,0.7724861533660972,25638000000,5833000000,0.4303519123114755,1,1,0,1,1,1,1,0,0
2017,0.0775687620995726,9960000000,5309000000,30953000000.0,68442500000.0,0.4522482375716842,1.2753440298059011,21223000000.0,16641000000.0,1603000000,0.7504961723844628,28216000000,7040000000,0.4122584651349673,1,1,0,1,1,0,1,0,0
2018,0.0873995297299789,13427000000,5687000000,35002000000.0,65069000000.0,0.537921283560528,0.9829456464992168,16945000000.0,17239000000.0,1546000000,0.7643574634384637,32753000000,7718000000,0.5033579738431511,1,1,1,1,0,0,1,1,1
2019,0.1061784773720759,13324000000,7882000000,62975000000.0,74233500000.0,0.8483366674075721,3.177350016041065,49519000000.0,15585000000.0,1484000000,0.7763782841339506,33266000000,7439000000,0.44812651969798,1,1,1,1,0,1,1,1,0
2020,0.0385180240320427,17588000000,4616000000,77554000000.0,119840000000.0,0.6471461949265688,0.8434109068071596,24173000000.0,28661000000.0,1673000000,0.6640686402934242,45804000000,15387000000,0.3822096128170894,1,1,0,1,1,0,0,0,0
2021,0.0776993140218247,22777000000,11542000000,64189000000.0,148547000000.0,0.432112395403475,0.7935443541512758,27928000000.0,35194000000.0,1777000000,0.6895563820132747,56197000000,17446000000,0.3783112415599103,1,1,1,1,1,0,0,1,0
2022,0.082962422984993,24943000000,11836000000,59135000000.0,142667000000.0,0.4144966951011796,0.9636062021802424,28463000000.0,29538000000.0,1778000000,0.7000378957522306,58054000000,17414000000,0.4069196100009112,1,1,1,1,1,1,0,1,1
2023,0.0355591629008906,22839000000,4863000000,52194000000.0,136758000000.0,0.3816522616592813,0.8721228297349436,33002000000.0,37841000000.0,1773000000,0.6241577377664862,54318000000,20415000000,0.3971833457640503,1,1,0,1,1,0,1,0,0
2024,0.0317039188948835,18806000000,4278000000,60340000000.0,134936000000.0,0.4471749570166597,0.6601976825208392,25582000000.0,38749000000.0,1773000000,0.6999325451769801,56334000000,16904000000,0.4174868085610956,1,1,0,1,0,0,1,1,1
"""

INDICATOR_NAME = "皮奥特罗斯基 F-Score (Piotroski F-Score)"

def to_native(v):
    """Convert numpy / pandas scalar types to native Python types for JSON serialization."""
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV into DataFrame
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: list of records with native types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Calculate Piotroski F-Score for each row
    der_records = []
    # We'll use these column names (they must match CSV header)
    for i, row in df.iterrows():
        # Extract current values
        roa = row.get("ROA(Avg)")
        cfo = row.get("CFO")
        ni = row.get("Net Income")
        leverage = row.get("Leverage")
        curr_ratio = row.get("Current Ratio")
        shares = row.get("Shares")
        gross_margin = row.get("Gross Margin")
        asset_turn = row.get("Asset Turnover (for F-score)")

        # Initialize binary flags
        f1 = 1 if (pd.notna(roa) and roa > 0) else 0
        f2 = 1 if (pd.notna(cfo) and cfo > 0) else 0

        # For year-over-year comparisons, need previous year; if missing, flag = 0
        if i > 0:
            prev = df.iloc[i - 1]
            prev_roa = prev.get("ROA(Avg)")
            prev_leverage = prev.get("Leverage")
            prev_curr = prev.get("Current Ratio")
            prev_shares = prev.get("Shares")
            prev_gross = prev.get("Gross Margin")
            prev_asset_turn = prev.get("Asset Turnover (for F-score)")

            f3 = 1 if (pd.notna(roa) and pd.notna(prev_roa) and (roa - prev_roa) > 0) else 0
            f5 = 1 if (pd.notna(leverage) and pd.notna(prev_leverage) and (leverage - prev_leverage) < 0) else 0
            f6 = 1 if (pd.notna(curr_ratio) and pd.notna(prev_curr) and (curr_ratio - prev_curr) > 0) else 0
            # No dilution: if current shares <= prior shares -> no dilution (1), else 0
            f7 = 1 if (pd.notna(shares) and pd.notna(prev_shares) and (shares <= prev_shares)) else 0
            f8 = 1 if (pd.notna(gross_margin) and pd.notna(prev_gross) and (gross_margin - prev_gross) > 0) else 0
            f9 = 1 if (pd.notna(asset_turn) and pd.notna(prev_asset_turn) and (asset_turn - prev_asset_turn) > 0) else 0
        else:
            f3 = f5 = f6 = f7 = f8 = f9 = 0

        f4 = 1 if (pd.notna(cfo) and pd.notna(ni) and cfo > ni) else 0

        score = int(f1 + f2 + f3 + f4 + f5 + f6 + f7 + f8 + f9)

        der_rec = {
            "Fiscal Year": to_native(row.get("Fiscal Year")),
            INDICATOR_NAME: to_native(score)
        }
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()