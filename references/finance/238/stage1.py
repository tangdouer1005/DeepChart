#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

csv_data = """Fiscal Year,ROA(Avg),CFO,Net Income,Long Term Debt,Avg Total Assets,Leverage,Current Ratio,Current Assets,Current Liabilities,Shares,Gross Margin,Revenue,Cost of Revenue,Asset Turnover (for F-score),1_ROA>0,2_CFO>0,3_dROA>0,4_CFO>NI,5_dLev<0,6_dCurrent>0,7_NoDilute,8_dMargin>0,9_dTurnover>0
2016,0.0227543696961668,6135000000,1460000000,24453000000.0,64163500000.0,0.3811045220413475,1.5758146752383064,14217000000,9022000000,833054545,0.5585489463857028,37490000000,16550000000,0.5842885752803385,1,1,1,1,0,1,0,1,1
2017,0.0664839433069019,3831000000,4536000000,12121000000.0,68227000000.0,0.1776569393348674,0.7742075553625706,8915000000,11515000000,871787000,0.5638853314944341,40604000000,17708000000,0.595130959883917,1,1,1,0,1,0,0,1,1
2018,0.0403828540666009,3899000000,2888000000,12124000000.0,71515500000.0,0.1695296823765477,0.8065647219246128,8281000000,10267000000,858290000,0.5762179635188178,43310000000,18354000000,0.6056029811719138,1,1,0,1,1,1,1,1,1
2019,0.0435161774024556,6824000000,3468000000,10958000000.0,79694500000.0,0.1375000784244835,0.7440428594274748,9305000000,12506000000,863434000,0.5884039290635139,44998000000,18521000000,0.5646311853390134,1,1,1,1,1,0,0,1,0
2020,0.0213457432171183,8640000000,3064000000,61830000000.0,143541500000.0,0.4307465088493571,1.1005390959775143,23885000000,21703000000,1154749000,0.5867362603622966,68397000000,28266000000,0.476496344262809,1,1,0,1,0,1,0,0,0
2021,0.0148699981560022,13917000000,3024000000,68570000000.0,203362500000.0,0.3371811420492962,0.8890165538959105,20891000000,23499000000,1254770000,0.5431114106692628,80118000000,36605000000,0.3939664392402729,1,1,0,1,1,0,0,0,0
2022,0.0123952802218707,16781000000,2590000000,66796000000.0,208950500000.0,0.3196737983397982,0.7706329318567617,19067000000,24742000000,1255377000,0.5449849819657916,79571000000,36206000000,0.3808126805152416,1,1,0,1,1,0,0,1,0
2023,0.0396973891461028,18559000000,8317000000,71399000000.0,209510000000.0,0.3407904157319459,0.9085913608562692,19015000000,20928000000,1200286000,0.6157234145472136,78558000000,30188000000,0.3749606224046585,1,1,1,1,0,1,1,1,0
2024,0.0545515338559645,22293000000,11339000000,74197000000.0,207858500000.0,0.3569591813661698,0.912263309209874,18404000000,20174000000,1173214000,0.6357125307125308,81400000000,29653000000,0.3916125633543973,1,1,1,1,0,1,1,1,1
"""

def to_python_native(val):
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, (np.bool_, bool)):
        return bool(val)
    # for other numeric types like plain Python int/float or strings, return as-is
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(csv_data))
    # Ensure rows ordered by Fiscal Year ascending (they already are)
    df = df.reset_index(drop=True)

    # Prepare scr_data with native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_native(row[col])
        scr_records.append(rec)

    # Compute Piotroski F-Score per row
    der_records = []
    for i in range(len(df)):
        row = df.iloc[i]
        prev = df.iloc[i-1] if i > 0 else None

        # 1. ROA > 0
        c1 = (row["ROA(Avg)"] > 0)

        # 2. CFO > 0
        c2 = (row["CFO"] > 0)

        # 3. ΔROA > 0 (year-over-year)
        c3 = False
        if prev is not None:
            c3 = (row["ROA(Avg)"] - prev["ROA(Avg)"]) > 0

        # 4. Accruals: CFO > Net Income
        c4 = (row["CFO"] > row["Net Income"])

        # 5. ΔLeverage < 0 (leverage decreased)
        c5 = False
        if prev is not None:
            # Leverage is provided as a ratio; decrease means current < previous
            c5 = (row["Leverage"] - prev["Leverage"]) < 0

        # 6. ΔCurrent Ratio > 0
        c6 = False
        if prev is not None:
            c6 = (row["Current Ratio"] - prev["Current Ratio"]) > 0

        # 7. No Dilution: shares not increased this year
        c7 = False
        if prev is not None:
            # If current shares <= previous shares, then no dilution
            c7 = (row["Shares"] <= prev["Shares"])

        # 8. ΔGross Margin > 0
        c8 = False
        if prev is not None:
            c8 = (row["Gross Margin"] - prev["Gross Margin"]) > 0

        # 9. ΔAsset Turnover > 0
        c9 = False
        if prev is not None:
            c9 = (row["Asset Turnover (for F-score)"] - prev["Asset Turnover (for F-score)"]) > 0

        score = int(bool(c1)) + int(bool(c2)) + int(bool(c3)) + int(bool(c4)) + int(bool(c5)) + int(bool(c6)) + int(bool(c7)) + int(bool(c8)) + int(bool(c9))

        der_rec = {
            "Fiscal Year": to_python_native(row["Fiscal Year"]),
            "皮奥特罗斯基 F-Score (Piotroski F-Score)": score
        }
        der_records.append(der_rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()