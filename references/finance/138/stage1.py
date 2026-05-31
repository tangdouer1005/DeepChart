#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,ROA(Avg),CFO,Net Income,Long Term Debt,Avg Total Assets,Leverage,Current Ratio,Current Assets,Current Liabilities,Shares,Gross Margin,Revenue,Cost of Revenue,Asset Turnover (for F-score),1_ROA>0,2_CFO>0,3_dROA>0,4_CFO>NI,5_dLev<0,6_dCurrent>0,7_NoDilute,8_dMargin>0,9_dTurnover>0
2016,0.073616332413667,4851000000,2737600000,8367800000,37187400000.0,0.2250170756761698,1.374528971656381,15101400000,10986600000,1100875000,0.7309361467526776,21222100000,5710100000,0.570679853929019,1,1,1,1,0,0,1,0,1
2017,-0.0048718833135012,5615600000,-204100000,9940500000,41893450000.0,0.2372805295338531,1.3210121148329308,19202100000,14535900000,1052023000,0.777323293514504,19973800000,4447700000,0.476776202485114,0,1,0,1,0,0,1,1,0
2018,0.0727195818624042,5524500000,3232000000,11639700000,44444700000.0,0.2618917441224713,1.728585728585729,20549600000,11888100000,1033667000,0.7821786324110304,21493300000,4681700000,0.4835964693203014,1,1,1,1,0,1,1,1,1
2019,0.1999747579467392,4836600000,8318400000,13817900000,41597250000.0,0.3321830169061657,1.1642774645016645,13709600000,11775200000,957526000,0.7884719639776877,22319500000,4721200000,0.5365619121456346,1,1,1,0,0,0,1,1,1
2020,0.1441749923183642,6499600000,6193700000,16586600000,42959600000.0,0.3860976359183977,1.3990273682861172,17462100000,12481600000,956590000,0.7765548211476866,24539800000,5483300000,0.5712297134982635,1,1,0,1,0,1,1,0,1
2021,0.1169688314328194,7260700000,5581700000,15346400000,47719550000.0,0.3215956562876221,1.2258531691988812,18452400000,15052700000,953653000,0.7417650714729646,28318400000,7312800000,0.5934339280232106,1,1,0,1,1,0,1,0,1
2022,0.1270613800386181,7084400000,6244800000,14737500000,49147900000.0,0.299860217832298,1.0522983743917098,18034500000,17138200000,950182000,0.7677128662223998,28541400000,6629800000,0.5807247105166243,1,1,1,1,1,0,1,1,0
2023,0.0923450233091709,4240100000,5240400000,18320800000,56748050000.0,0.3228445735139797,0.9426157431155012,25727000000,27293200000,903284000,0.7924575300154436,34124100000,7082200000,0.6013263891887034,1,1,0,0,0,0,1,1,1
2024,0.1484012185996194,8817900000,10590000000,28527100000,71360600000.0,0.399759811436563,1.1537569687700429,32739700000,28376600000,904059000,0.8131040101947707,45042700000,8418300000,0.6311984484435389,1,1,1,0,0,1,0,1,1
"""

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)

    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA), dtype=str)

    # Convert numeric columns to appropriate types where possible
    # Keep Fiscal Year as is (int)
    # We'll attempt to convert all other columns to numeric (float) where appropriate
    numeric_cols = [c for c in df.columns if c != "Fiscal Year"]
    for c in numeric_cols:
        # coerce errors so that any non-numeric values become NaN
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Prepare scr_data: original rows with proper types
    # Convert DataFrame to records, but ensure Fiscal Year as int if possible
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            val = row[col]
            # If it's a float and represents an integer (for Fiscal Year), cast to int
            if pd.isna(val):
                rec[col] = None
            else:
                # Fiscal Year should be int if possible
                if col == "Fiscal Year":
                    try:
                        rec[col] = int(float(val))
                    except Exception:
                        rec[col] = val
                else:
                    # For numeric columns, if it's an integer value, keep as int
                    if isinstance(val, float) and val.is_integer():
                        rec[col] = int(val)
                    else:
                        rec[col] = float(val) if isinstance(val, float) or isinstance(val, int) else val
        scr_records.append(rec)

    # Compute Piotroski F-Score for each row
    der_records = []
    # We'll iterate with index to access previous year
    for idx in range(len(df)):
        row = df.iloc[idx]
        year_val = row.get("Fiscal Year")
        try:
            year = int(year_val)
        except Exception:
            year = year_val

        score_components = {}

        # 1. ROA > 0
        roa = row.get("ROA(Avg)", float("nan"))
        score_components["ROA_pos"] = 1 if (pd.notna(roa) and roa > 0) else 0

        # 2. CFO > 0
        cfo = row.get("CFO", float("nan"))
        score_components["CFO_pos"] = 1 if (pd.notna(cfo) and cfo > 0) else 0

        # 3. ΔROA > 0  (compare to previous year)
        if idx == 0:
            score_components["dROA_pos"] = 0
        else:
            prev_roa = df.iloc[idx - 1].get("ROA(Avg)", float("nan"))
            if pd.notna(roa) and pd.notna(prev_roa) and (roa - prev_roa) > 0:
                score_components["dROA_pos"] = 1
            else:
                score_components["dROA_pos"] = 0

        # 4. Accruals: CFO > Net Income
        net_income = row.get("Net Income", float("nan"))
        if pd.notna(cfo) and pd.notna(net_income) and cfo > net_income:
            score_components["Accruals"] = 1
        else:
            score_components["Accruals"] = 0

        # 5. ΔLeverage < 0 (leverage decreased)
        leverage = row.get("Leverage", float("nan"))
        if idx == 0:
            score_components["dLeverage_neg"] = 0
        else:
            prev_lev = df.iloc[idx - 1].get("Leverage", float("nan"))
            if pd.notna(leverage) and pd.notna(prev_lev) and (leverage - prev_lev) < 0:
                score_components["dLeverage_neg"] = 1
            else:
                score_components["dLeverage_neg"] = 0

        # 6. ΔCurrent Ratio > 0
        current_ratio = row.get("Current Ratio", float("nan"))
        if idx == 0:
            score_components["dCurrent_pos"] = 0
        else:
            prev_cr = df.iloc[idx - 1].get("Current Ratio", float("nan"))
            if pd.notna(current_ratio) and pd.notna(prev_cr) and (current_ratio - prev_cr) > 0:
                score_components["dCurrent_pos"] = 1
            else:
                score_components["dCurrent_pos"] = 0

        # 7. No Dilution: Shares current <= Shares previous
        shares = row.get("Shares", float("nan"))
        if idx == 0:
            # No prior year to compare; assume no dilution (1)
            score_components["NoDilute"] = 1
        else:
            prev_shares = df.iloc[idx - 1].get("Shares", float("nan"))
            if pd.notna(shares) and pd.notna(prev_shares) and shares <= prev_shares:
                score_components["NoDilute"] = 1
            else:
                score_components["NoDilute"] = 0

        # 8. ΔGross Margin > 0
        gm = row.get("Gross Margin", float("nan"))
        if idx == 0:
            score_components["dGrossMargin_pos"] = 0
        else:
            prev_gm = df.iloc[idx - 1].get("Gross Margin", float("nan"))
            if pd.notna(gm) and pd.notna(prev_gm) and (gm - prev_gm) > 0:
                score_components["dGrossMargin_pos"] = 1
            else:
                score_components["dGrossMargin_pos"] = 0

        # 9. ΔAsset Turnover > 0
        at = row.get("Asset Turnover (for F-score)", float("nan"))
        if idx == 0:
            score_components["dAssetTurnover_pos"] = 0
        else:
            prev_at = df.iloc[idx - 1].get("Asset Turnover (for F-score)", float("nan"))
            if pd.notna(at) and pd.notna(prev_at) and (at - prev_at) > 0:
                score_components["dAssetTurnover_pos"] = 1
            else:
                score_components["dAssetTurnover_pos"] = 0

        # Sum up the nine tests
        # The standard nine tests: ROA_pos, CFO_pos, dROA_pos, Accruals, dLeverage_neg,
        # dCurrent_pos, NoDilute, dGrossMargin_pos, dAssetTurnover_pos
        keys_order = [
            "ROA_pos", "CFO_pos", "dROA_pos", "Accruals",
            "dLeverage_neg", "dCurrent_pos", "NoDilute",
            "dGrossMargin_pos", "dAssetTurnover_pos"
        ]
        total_score = sum(score_components.get(k, 0) for k in keys_order)

        der_rec = {
            "Fiscal Year": year,
            "皮奥特罗斯基 F-Score (Piotroski F-Score)": int(total_score)
        }
        der_records.append(der_rec)

    # Prepare final JSON object
    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to specified file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()