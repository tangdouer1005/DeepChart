#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,ROA(Avg),CFO,Net Income,Long Term Debt,Avg Total Assets,Leverage,Current Ratio,Current Assets,Current Liabilities,Shares,Gross Margin,Revenue,Cost of Revenue,Asset Turnover (for F-score),1_ROA>0,2_CFO>0,3_dROA>0,4_CFO>NI,5_dLev<0,6_dCurrent>0,7_NoDilute,8_dMargin>0,9_dTurnover>0
2016,0.0156941633152904,-1473984000,186678000,3364311000.0,11894740500.0,0.2828402183301098,1.2471590964835608,5720291000,4586657000,4386520000,0.3171637392365176,8830669000,6029901000,0.742401147801417,1,0,1,0,0,0,0,0,0
2017,0.034290804308012,-1785948000,558929000,6499400000.0,16299676000.0,0.3987441222758047,1.403135057054921,7669974000,5466312000,4468140000,0.3449196948561039,11692713000,7659666000,0.7173586149810586,1,0,1,0,0,1,0,1,0
2018,0.0538483640503324,-2680479000,1211242000,10360000000.0,22493571000.0,0.4605760463734282,1.4943204589876868,9694135000,6487320000,4512440000,0.3689171330415115,15794341000,9967538000,0.702171344870052,1,0,1,0,0,1,0,1,0
2019,0.0622823190055091,-2887322000,1866916000,14759260000.0,29975056000.0,0.4923847348275179,0.9012219911734708,6178504000,6855696000,4517650000,0.3828171701093947,20156447000,12440213000,0.6724406786762968,1,0,1,0,0,0,0,1,0
2020,0.075390202130824,2427077000,2761395000,15809095000.0,36628035500.0,0.4316118728234824,1.250557118854798,9761580000,7805785000,4542080000,0.3888508251061687,24996056000,15276319000,0.6824296105096873,1,1,1,0,1,1,0,1,1
2021,0.1220110095481761,392610000,5116228000,14693072000.0,41932511000.0,0.3503980956446896,0.950625199818211,8069825000,8488966000,4553720000,0.4163656122646479,29697844000,17332683000,0.7082295644064817,1,1,1,0,1,0,0,1,1
2022,0.0964144973154,2026257000,4491924000,14353076000.0,46589715500.0,0.308073913866248,1.168390288506809,9266473000,7930974000,4512900000,0.3937070523840325,31615550000,19168285000,0.6785950431485249,1,1,0,0,1,1,1,0,0
2023,0.1111305873122664,7274301000,5407990000,14143417000.0,48663380000.0,0.2906377855381192,1.119345353136986,9918133000,8860655000,4494980000,0.4153783955346952,33723297000,19715368000,0.6929912595467064,1,1,1,1,1,0,1,1,1
2024,0.1702115990558483,7361364000,8711631000,13798351000.0,51181183000.0,0.2695981255454763,1.2180280603231866,13100379000,10755400000,4392610000,0.4605655665041732,39000966000,21038464000,0.762017673565693,1,1,1,0,1,1,1,1,1
"""

INDICATOR_NAME = "皮奥特罗斯基 F-Score (Piotroski F-Score)"

def to_py(val):
    # Convert pandas/numpy types to native Python types for JSON serialization
    if pd.isna(val):
        return None
    try:
        # numpy scalar
        return val.item()
    except Exception:
        return val

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))
    # Ensure consistent column names
    df_columns = list(df.columns)

    # Prepare scr_data: array of dicts representing original rows
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df_columns:
            rec[col] = to_py(row[col])
        scr_records.append(rec)

    # Calculate Piotroski F-Score per row
    der_records = []
    # We'll use the following columns (as present in CSV):
    # 'Fiscal Year', 'ROA(Avg)', 'CFO', 'Net Income', 'Leverage', 'Current Ratio', 'Shares',
    # 'Gross Margin', 'Asset Turnover (for F-score)'
    # For deltas, compare to prior fiscal row in the CSV (previous chronological row)
    for idx in range(len(df)):
        row = df.iloc[idx]
        # Helper to fetch previous row values if present
        prev = df.iloc[idx - 1] if idx - 1 >= 0 else None

        # 1. ROA > 0
        roa = row.get("ROA(Avg)")
        cond1 = (roa is not None) and (roa > 0)

        # 2. CFO > 0
        cfo = row.get("CFO")
        cond2 = (cfo is not None) and (cfo > 0)

        # 3. delta ROA > 0 (compared to previous year)
        if prev is not None:
            prev_roa = prev.get("ROA(Avg)")
            cond3 = (roa is not None and prev_roa is not None) and ((roa - prev_roa) > 0)
        else:
            cond3 = False

        # 4. Accruals: CFO > Net Income
        net_income = row.get("Net Income")
        cond4 = (cfo is not None and net_income is not None) and (cfo > net_income)

        # 5. delta Leverage < 0 (leverage decreased)
        leverage = row.get("Leverage")
        if prev is not None:
            prev_lev = prev.get("Leverage")
            cond5 = (leverage is not None and prev_lev is not None) and ((leverage - prev_lev) < 0)
        else:
            cond5 = False

        # 6. delta Current Ratio > 0 (improved current ratio)
        curr_ratio = row.get("Current Ratio")
        if prev is not None:
            prev_cr = prev.get("Current Ratio")
            cond6 = (curr_ratio is not None and prev_cr is not None) and ((curr_ratio - prev_cr) > 0)
        else:
            cond6 = False

        # 7. No Dilution: Shares not increased (current shares <= previous shares)
        shares = row.get("Shares")
        if prev is not None:
            prev_shares = prev.get("Shares")
            cond7 = (shares is not None and prev_shares is not None) and (shares <= prev_shares)
        else:
            cond7 = False

        # 8. delta Gross Margin > 0
        gm = row.get("Gross Margin")
        if prev is not None:
            prev_gm = prev.get("Gross Margin")
            cond8 = (gm is not None and prev_gm is not None) and ((gm - prev_gm) > 0)
        else:
            cond8 = False

        # 9. delta Asset Turnover > 0
        at = row.get("Asset Turnover (for F-score)")
        if prev is not None:
            prev_at = prev.get("Asset Turnover (for F-score)")
            cond9 = (at is not None and prev_at is not None) and ((at - prev_at) > 0)
        else:
            cond9 = False

        # Sum up as integers
        score = int(bool(cond1)) + int(bool(cond2)) + int(bool(cond3)) + int(bool(cond4)) + int(bool(cond5)) + int(bool(cond6)) + int(bool(cond7)) + int(bool(cond8)) + int(bool(cond9))

        der_rec = {
            "Fiscal Year": to_py(row.get("Fiscal Year")),
            INDICATOR_NAME: to_py(score)
        }
        der_records.append(der_rec)

    out_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()