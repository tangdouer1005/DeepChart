#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,ROA(Avg),CFO,Net Income,Long Term Debt,Avg Total Assets,Leverage,Current Ratio,Current Assets,Current Liabilities,Shares,Gross Margin,Revenue,Cost of Revenue,Asset Turnover (for F-score),1_ROA>0,2_CFO>0,3_dROA>0,4_CFO>NI,5_dLev<0,6_dCurrent>0,7_NoDilute,8_dMargin>0,9_dTurnover>0
2016,-0.0040438436347491,1672081000,-47426000,1293947000.0,11727951000.0,0.1103301847014879,0.7739581859015614,4347327000,5617005000,661647000,0.7518382485283213,6667216000,1654548000,0.5684894147323774,0,1,1,1,1,0,0,0,1
2017,0.0212865210881709,2162198000,323000000,2008391000.0,15173921500.0,0.1323580723677791,0.8261966592145629,5996827000,7258353000,700217000,0.7337935820659334,8391984000,2234000000,0.5530530785993588,1,1,1,1,0,1,0,0,0
2018,0.0066059804804931,2737965000,127478000,694781000.0,19297362500.0,0.0360039357710153,0.917158249780493,9290371000,10129518000,734598000,0.7353512572313848,10480012000,2773522000,0.5430800193549766,1,1,0,1,1,1,0,1,0
2019,0.0429012018945634,3398000000,1110000000,3173000000.0,25873401000.0,0.122635597848153,0.9491781430475345,10683000000,11255000000,775000000,0.740174672489083,13282000000,3451000000,0.5133457329401728,1,1,1,1,0,1,0,1,0
2020,0.0029349079347332,4331000000,126000000,2673000000.0,42931500000.0,0.0622619754725551,1.0753115527113506,15963000000,14845000000,850000000,0.752310211720669,17098000000,4235000000,0.3982623481592769,1,1,0,1,1,1,0,1,0
2021,0.0670691032472184,4801000000,4072000000,2673000000.0,60713500000.0,0.0440264521070272,1.2347134476534296,21889000000,17728000000,930000000,0.7441182006399397,21252000000,5438000000,0.3500374710731551,1,1,1,1,1,1,0,0,0
2022,0.0178812457432976,6000000000,1444000000,10592000000.0,80755000000.0,0.1311621571419726,1.04874242702405,22850000000,21788000000,974000000,0.7347878604861845,26492000000,7026000000,0.3280539904649867,1,1,0,1,0,0,0,0,0
2023,0.0021436890001958,7111000000,208000000,9419000000.0,97029000000.0,0.097074070638675,1.0194662237843266,26395000000,25891000000,997000000,0.7333503444756315,31352000000,8360000000,0.3231198919910542,1,1,0,1,1,0,0,0,0
2024,0.0416364661351373,10234000000,4136000000,8427000000.0,99336000000.0,0.0848332930659579,1.0917351958244152,29074000000,26631000000,984000000,0.7549703072553576,34857000000,8541000000,0.3508999758395748,1,1,1,1,1,1,1,1,1
"""

def to_native(val):
    # Convert numpy types to native Python types for JSON serialization
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        # convert NaN to None
        if np.isnan(val):
            return None
        return float(val)
    if isinstance(val, (np.bool_, bool)):
        return bool(val)
    if pd.isna(val):
        return None
    return val

def df_to_records_native(df):
    records = []
    for _, row in df.iterrows():
        rec = {}
        for k, v in row.items():
            rec[k] = to_native(v)
        records.append(rec)
    return records

def compute_piotroski_fscore(df):
    results = []
    # Ensure ordering by Fiscal Year if present
    if 'Fiscal Year' in df.columns:
        df = df.sort_values('Fiscal Year').reset_index(drop=True)
    # Iterate rows and compute
    prev = None
    for idx, row in df.iterrows():
        year = to_native(row.get('Fiscal Year')) if 'Fiscal Year' in row else None

        # Extract raw inputs (may be None)
        roa = row.get('ROA(Avg)')
        cfo = row.get('CFO')
        ni = row.get('Net Income')
        leverage = row.get('Leverage')
        current_ratio = row.get('Current Ratio')
        shares = row.get('Shares')
        gross_margin = row.get('Gross Margin')
        asset_turnover = row.get('Asset Turnover (for F-score)')

        # Initialize component scores
        s1 = 1 if (pd.notna(roa) and roa > 0) else 0
        s2 = 1 if (pd.notna(cfo) and cfo > 0) else 0

        # For delta-based metrics, need previous-year values; if not available, score 0
        if prev is None:
            s3 = 0  # ΔROA > 0
            s5 = 0  # ΔLeverage < 0
            s6 = 0  # ΔCurrent Ratio > 0
            s7 = 0  # No Dilution (requires prior shares)
            s8 = 0  # ΔGross Margin > 0
            s9 = 0  # ΔAsset Turnover > 0
        else:
            prev_roa = prev.get('ROA(Avg)')
            prev_leverage = prev.get('Leverage')
            prev_current = prev.get('Current Ratio')
            prev_shares = prev.get('Shares')
            prev_gm = prev.get('Gross Margin')
            prev_at = prev.get('Asset Turnover (for F-score)')

            s3 = 1 if (pd.notna(roa) and pd.notna(prev_roa) and (roa - prev_roa) > 0) else 0
            # Accruals quality (CFO > Net Income)
            # s4 computed below independent of prev
            s5 = 1 if (pd.notna(leverage) and pd.notna(prev_leverage) and (leverage - prev_leverage) < 0) else 0
            s6 = 1 if (pd.notna(current_ratio) and pd.notna(prev_current) and (current_ratio - prev_current) > 0) else 0
            # No dilution: shares outstanding did not increase (<= prior year)
            s7 = 1 if (pd.notna(shares) and pd.notna(prev_shares) and (shares <= prev_shares)) else 0
            s8 = 1 if (pd.notna(gross_margin) and pd.notna(prev_gm) and (gross_margin - prev_gm) > 0) else 0
            s9 = 1 if (pd.notna(asset_turnover) and pd.notna(prev_at) and (asset_turnover - prev_at) > 0) else 0

        # Accruals: CFO > Net Income
        s4 = 1 if (pd.notna(cfo) and pd.notna(ni) and (cfo > ni)) else 0

        total = int(s1 + s2 + s3 + s4 + s5 + s6 + s7 + s8 + s9)

        result = {
            'Fiscal Year': to_native(year),
            '皮奥特罗斯基 F-Score (Piotroski F-Score)': total
        }
        results.append(result)
        prev = row
    return results

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA), dtype=object)

    # Convert numeric-like columns to numeric where possible
    for col in df.columns:
        # Try to convert to numeric; keep original if fails
        try:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        except Exception:
            pass

    # Prepare scr_data as list of native Python dicts
    scr_data = df_to_records_native(df)

    # Compute Piotroski F-Score dynamically
    der_data = compute_piotroski_fscore(df)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()