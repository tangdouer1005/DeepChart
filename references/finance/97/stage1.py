#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,ROA(Avg),CFO,Net Income,Long Term Debt,Avg Total Assets,Leverage,Current Ratio,Current Assets,Current Liabilities,Shares,Gross Margin,Revenue,Cost of Revenue,Asset Turnover (for F-score),1_ROA>0,2_CFO>0,3_dROA>0,4_CFO>NI,5_dLev<0,6_dCurrent>0,7_NoDilute,8_dMargin>0,9_dTurnover>0
2016,0.1236863327808787,36036000000,19478000000,3935000000.0,157479000000.0,0.0249874586452796,6.290761518262115,105408000000,16756000000,13987786146,0.6107541651896491,90272000000,35138000000,0.5732319864870872,1,1,1,1,0,1,0,0,1
2017,0.0694203820259216,37091000000,12662000000,3943000000.0,182396000000.0,0.021617798635935,5.140305173055452,124308000000,24183000000,14068883261,0.5888051959767263,110855000000,45583000000,0.6077710037500822,1,1,0,1,1,0,0,0,1
2018,0.1429292212970864,47971000000,30736000000,3950000000.0,215043500000.0,0.0183683766307747,3.919006354708261,135676000000,34620000000,14066813595,0.5647607422945643,136819000000,59549000000,0.6362387144926491,1,1,1,1,1,0,1,0,1
2019,0.1350223412181222,54520000000,34343000000,3958000000.0,254350500000.0,0.0155612039292236,3.374051878552,152578000000,45221000000,13971114411,0.5558054331910266,161857000000,71896000000,0.6363541648237373,1,1,0,1,1,0,1,0,1
2020,0.1352386549683052,65124000000,40269000000,13932000000.0,297762500000.0,0.0467889677175601,3.066755815181053,174296000000,56834000000,13740560000,0.5357837470620785,182527000000,84732000000,0.6129952562864699,1,1,1,1,0,0,1,0,0
2021,0.2239940844091185,91652000000,76033000000,14817000000.0,339442000000.0,0.0436510508422646,2.928113424845146,188143000000,64254000000,13553473900,0.5693980290098084,257637000000,110939000000,0.7590015378179483,1,1,1,1,1,0,1,1,1
2022,0.1655468633545516,91495000000,59972000000,12857000000.0,362266000000.0,0.035490495933927,2.377994227994228,164795000000,69300000000,13242420000,0.5537944250378312,282836000000,126203000000,0.7807412233000061,1,1,0,1,1,0,1,0,1
2023,0.1922605958919099,101746000000,73795000000,11870000000.0,383828000000.0,0.0309253102952364,2.096584936563424,171530000000,81814000000,12722000000,0.566250479840205,307394000000,133332000000,0.8008639286347009,1,1,1,1,1,0,1,1,1
2024,0.2348401685103348,125299000000,100118000000,10883000000.0,426324000000.0,0.0255275330499807,1.8369313974102917,163711000000,89122000000,12447000000,0.5820043540617911,350018000000,146306000000,0.8210140644204877,1,1,1,1,1,0,1,1,1
"""

INDICATOR_NAME = "皮奥特罗斯基 F-Score (Piotroski F-Score)"

def to_json_friendly(value):
    # Convert pandas/numpy scalars to native Python types for JSON serialization
    if pd.isna(value):
        return None
    # pandas/Numpy scalars often have .item()
    if hasattr(value, "item") and not isinstance(value, str):
        try:
            return value.item()
        except Exception:
            pass
    return value

def compute_piotroski_fscore(df):
    # We'll use the provided columns:
    # 1. ROA: use "ROA(Avg)"
    roa = df["ROA(Avg)"]

    # 2. CFO: "CFO"
    cfo = df["CFO"]

    # 3. Net Income: "Net Income"
    ni = df["Net Income"]

    # 4. Leverage: "Leverage"
    lev = df["Leverage"]

    # 5. Current Ratio: "Current Ratio"
    cur = df["Current Ratio"]

    # 6. Shares: "Shares"
    shares = df["Shares"]

    # 7. Gross Margin: "Gross Margin"
    gm = df["Gross Margin"]

    # 8. Asset Turnover (for F-score)
    at = df["Asset Turnover (for F-score)"]

    # Condition 1: ROA > 0
    cond1 = (roa > 0).astype(int)

    # Condition 2: CFO > 0
    cond2 = (cfo > 0).astype(int)

    # Condition 3: ΔROA > 0 (compare to previous fiscal year)
    cond3 = (roa.diff() > 0).fillna(False).astype(int)

    # Condition 4: Accruals: CFO > Net Income
    cond4 = (cfo > ni).astype(int)

    # Condition 5: ΔLeverage < 0 (leverage decreased vs prior year)
    cond5 = (lev.diff() < 0).fillna(False).astype(int)

    # Condition 6: ΔCurrent Ratio > 0
    cond6 = (cur.diff() > 0).fillna(False).astype(int)

    # Condition 7: No Dilution: this year no increase in shares outstanding
    # => Shares_current <= Shares_prior => diff <= 0
    cond7 = (shares.diff() <= 0).fillna(False).astype(int)

    # Condition 8: ΔGross Margin > 0
    cond8 = (gm.diff() > 0).fillna(False).astype(int)

    # Condition 9: ΔAsset Turnover > 0
    cond9 = (at.diff() > 0).fillna(False).astype(int)

    # Sum up to get F-Score (0-9)
    fscore = cond1 + cond2 + cond3 + cond4 + cond5 + cond6 + cond7 + cond8 + cond9

    # Ensure integer type
    fscore = fscore.astype(int)

    # Build result list of dicts with Fiscal Year and the indicator
    results = []
    for idx, row in df.iterrows():
        year = to_json_friendly(row["Fiscal Year"])
        results.append({
            "Fiscal Year": year,
            INDICATOR_NAME: int(fscore.loc[idx])
        })
    return results

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Read CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA), sep=",")
    # Keep original scr_data as list of dicts with JSON-friendly values
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_json_friendly(row[col])
        scr_records.append(rec)

    der_records = compute_piotroski_fscore(df)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()