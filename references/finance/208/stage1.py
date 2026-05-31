#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,ROA(Avg),CFO,Net Income,Long Term Debt,Avg Total Assets,Leverage,Current Ratio,Current Assets,Current Liabilities,Shares,Gross Margin,Revenue,Cost of Revenue,Asset Turnover (for F-score),1_ROA>0,2_CFO>0,3_dROA>0,4_CFO>NI,5_dLev<0,6_dCurrent>0,7_NoDilute,8_dMargin>0,9_dTurnover>0
2016,0.0797998951063057,13561000000,8901000000,40105000000,111541500000.0,0.3595522742656321,3.737389586238959,64313000000,17208000000,4305000000,0.7981213053688557,37047000000,7479000000,0.3321364693858339,1,1,0,1,1,0,1,0,0
2017,0.0764814642494467,14126000000,9452000000,48112000000,123585500000.0,0.3893013338943484,3.0819339895773017,74515000000,24178000000,4219643000,0.8024809160305344,37728000000,7452000000,0.3052785318666025,1,1,0,1,0,0,1,1,0
2018,0.0263502965969403,15386000000,3587000000,56128000000,136127500000.0,0.412319332978274,3.967647824954416,76159000000,19195000000,4238000000,0.7976450503376766,39831000000,8060000000,0.2926006868560724,1,1,0,1,0,1,0,0,0
2019,0.0901155817914974,14551000000,11083000000,51673000000,122986500000.0,0.4201518052794412,2.489855072463768,46386000000,18630000000,3732000000,0.7976256771123373,39506000000,7995000000,0.3212222479703057,1,1,1,1,0,0,1,0,1
2020,0.0904317256086407,13139000000,10135000000,69226000000,112073500000.0,0.6176839306348066,3.031395348837209,52140000000,17200000000,3294000000,0.7968158083341865,39068000000,7938000000,0.3485926646352617,1,1,1,1,0,1,1,0,1
2021,0.1115090551420633,15887000000,13746000000,75995000000,123272500000.0,0.6164797501470319,2.299577884456216,55567000000,24164000000,3022000000,0.805948763556412,40479000000,7855000000,0.3283700744286033,1,1,1,1,1,0,1,1,0
2022,0.0558809337615014,9539000000,6717000000,72110000000,120202000000.0,0.5999068235137518,1.6212905540464353,31633000000,19511000000,2786000000,0.7908341187558907,42440000000,8877000000,0.3530723282474501,1,1,0,1,1,0,1,0,1
2023,0.0697879604893282,17165000000,8503000000,86420000000,121840500000.0,0.7092879625411912,0.9096578605456908,21004000000,23090000000,2766000000,0.728470192577171,49954000000,13564000000,0.4099950344918151,1,1,1,1,0,0,1,0,1
2024,0.0760241138872748,18673000000,10467000000,76264000000,137680000000.0,0.5539221382916909,0.7150012680699974,22554000000,31544000000,2823000000,0.7140726194747078,52961000000,15143000000,0.3846673445671121,1,1,1,1,1,0,0,0,0
"""

INDICATOR_NAME = "皮奥特罗斯基 F-Score (Piotroski F-Score)"

def to_python_native(value):
    # Convert numpy and pandas types to native Python types for JSON serialization
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        # Convert NaN to None
        if np.isnan(value):
            return None
        return float(value)
    if pd.isna(value):
        return None
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Keep a copy of scraped data as native python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_native(row[col])
        scr_records.append(rec)

    # Compute Piotroski F-Score per row
    der_records = []
    # We'll use these column names directly
    roa_col = "ROA(Avg)"
    cfo_col = "CFO"
    ni_col = "Net Income"
    leverage_col = "Leverage"
    current_ratio_col = "Current Ratio"
    shares_col = "Shares"
    gross_margin_col = "Gross Margin"
    asset_turnover_col = "Asset Turnover (for F-score)"
    fiscal_col = "Fiscal Year"

    for i in range(len(df)):
        row = df.iloc[i]
        score_components = []

        # 1. ROA > 0
        try:
            roa = float(row[roa_col])
            score_components.append(1 if roa > 0 else 0)
        except Exception:
            score_components.append(0)

        # 2. CFO > 0
        try:
            cfo = float(row[cfo_col])
            score_components.append(1 if cfo > 0 else 0)
        except Exception:
            score_components.append(0)

        # 3. ΔROA > 0 (requires previous year)
        if i > 0:
            try:
                prev_roa = float(df.iloc[i-1][roa_col])
                score_components.append(1 if roa > prev_roa else 0)
            except Exception:
                score_components.append(0)
        else:
            score_components.append(0)

        # 4. Accruals: CFO > Net Income
        try:
            ni = float(row[ni_col])
            accrual_ok = cfo > ni
            score_components.append(1 if accrual_ok else 0)
        except Exception:
            score_components.append(0)

        # 5. ΔLeverage < 0 (decrease in leverage)
        if i > 0:
            try:
                prev_lev = float(df.iloc[i-1][leverage_col])
                lev = float(row[leverage_col])
                score_components.append(1 if lev < prev_lev else 0)
            except Exception:
                score_components.append(0)
        else:
            score_components.append(0)

        # 6. ΔCurrent Ratio > 0
        if i > 0:
            try:
                prev_cr = float(df.iloc[i-1][current_ratio_col])
                cr = float(row[current_ratio_col])
                score_components.append(1 if cr > prev_cr else 0)
            except Exception:
                score_components.append(0)
        else:
            score_components.append(0)

        # 7. No Dilution: shares this year <= previous year
        if i > 0:
            try:
                prev_shares = float(df.iloc[i-1][shares_col])
                shares = float(row[shares_col])
                score_components.append(1 if shares <= prev_shares else 0)
            except Exception:
                score_components.append(0)
        else:
            score_components.append(0)

        # 8. ΔGross Margin > 0
        if i > 0:
            try:
                prev_gm = float(df.iloc[i-1][gross_margin_col])
                gm = float(row[gross_margin_col])
                score_components.append(1 if gm > prev_gm else 0)
            except Exception:
                score_components.append(0)
        else:
            score_components.append(0)

        # 9. ΔAsset Turnover > 0
        if i > 0:
            try:
                prev_at = float(df.iloc[i-1][asset_turnover_col])
                at = float(row[asset_turnover_col])
                score_components.append(1 if at > prev_at else 0)
            except Exception:
                score_components.append(0)
        else:
            score_components.append(0)

        # Sum up score
        try:
            score = int(sum(int(x) for x in score_components))
        except Exception:
            score = None

        der_rec = {
            fiscal_col: to_python_native(row[fiscal_col]),
            INDICATOR_NAME: to_python_native(score)
        }
        der_records.append(der_rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()