#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,ROA(Avg),CFO,Net Income,Long Term Debt,Avg Total Assets,Leverage,Current Ratio,Current Assets,Current Liabilities,Shares,Gross Margin,Revenue,Cost of Revenue,Asset Turnover (for F-score),1_ROA>0,2_CFO>0,3_dROA>0,4_CFO>NI,5_dLev<0,6_dCurrent>0,7_NoDilute,8_dMargin>0,9_dTurnover>0
2016,0.0818918992639236,15435000000,10508000000,18945000000,128315500000.0,0.1476438933721958,1.0978875528111798,33782000000,30770000000,2844400000,0.4960259728326621,65299000000,32909000000,0.5088940930752714,1,1,1,1,0,1,1,1,0
2017,0.1238254518425156,12753000000,15326000000,18038000000,123771000000.0,0.1457368850538494,0.8769943727242635,26494000000,30210000000,2740400000,0.4983245719204402,65058000000,32638000000,0.5256320139612671,1,1,1,0,1,0,1,1,1
2018,0.0816870255868898,14867000000,9750000000,20863000000,119358000000.0,0.1747934784430034,0.8258667705492793,23320000000,28237000000,2656700000,0.4847977016997845,66832000000,34432000000,0.5599289532331306,1,1,0,1,0,0,1,0,1
2019,0.0333926008440264,15242000000,3897000000,20395000000,116702500000.0,0.1747606092414472,0.7488254306754191,22473000000,30011000000,2539500000,0.4863187754860824,67684000000,34768000000,0.5799704376512929,1,1,0,1,1,0,1,1,1
2020,0.1104942852901885,17403000000,13027000000,23537000000,117897500000.0,0.1996395173773829,0.8487081513828238,27987000000,32976000000,2625800000,0.5031712473572939,70950000000,35250000000,0.6017939311690239,1,1,1,1,0,1,0,1,1
2021,0.1192131896153028,18371000000,14306000000,23099000000,120003500000.0,0.1924860524901357,0.6969395146685984,23091000000,33132000000,2601000000,0.5124937596889041,76118000000,37108000000,0.6342981663034828,1,1,1,1,1,0,1,1,1
2022,0.1246601695452719,16723000000,14742000000,22848000000,118257500000.0,0.1932055049362619,0.6545449049303226,21653000000,33081000000,2539100000,0.4742664022846596,80187000000,42157000000,0.6780711582774877,1,1,1,1,0,0,1,0,1
2023,0.1231153140058058,16848000000,14653000000,24378000000,119018500000.0,0.2048253002684456,0.6334041839131894,22648000000,35756000000,2483900000,0.4785747384337731,82006000000,42760000000,0.689018934031264,1,1,0,1,0,0,1,1,1
2024,0.1223607004963013,19846000000,14879000000,25269000000,121599500000.0,0.2078051307776759,0.7347964433342254,24709000000,33627000000,2471900000,0.5139399564487916,84039000000,40848000000,0.6911130391161148,1,1,0,1,0,1,1,1,1
"""

def to_native(value):
    # Convert pandas/numpy scalar types to native Python types for JSON serialization
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA), dtype=object)

    # Convert numeric-like columns to numeric where appropriate for calculations
    # We'll coerce specific columns used in computations to numeric types
    numeric_cols = [
        'ROA(Avg)', 'CFO', 'Net Income', 'Leverage', 'Current Ratio',
        'Shares', 'Gross Margin', 'Asset Turnover (for F-score)', 'Fiscal Year'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Prepare scr_data: raw rows as dictionaries with original headers
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_data.append(rec)

    # Calculate Piotroski F-Score for each year dynamically
    der_data = []
    # We'll iterate by index so we can refer to previous year
    for idx in range(len(df)):
        row = df.iloc[idx]
        # Initialize individual tests to 0
        t1 = t2 = t3 = t4 = t5 = t6 = t7 = t8 = t9 = 0

        # 1. ROA > 0
        roa = row.get('ROA(Avg)', np.nan)
        try:
            t1 = 1 if float(roa) > 0 else 0
        except Exception:
            t1 = 0

        # 2. CFO > 0
        cfo = row.get('CFO', np.nan)
        try:
            t2 = 1 if float(cfo) > 0 else 0
        except Exception:
            t2 = 0

        # 3. ΔROA > 0 (requires previous year)
        if idx > 0:
            prev_roa = df.iloc[idx - 1].get('ROA(Avg)', np.nan)
            try:
                t3 = 1 if (float(roa) - float(prev_roa)) > 0 else 0
            except Exception:
                t3 = 0
        else:
            t3 = 0

        # 4. Accruals: CFO > Net Income
        ni = row.get('Net Income', np.nan)
        try:
            t4 = 1 if float(cfo) > float(ni) else 0
        except Exception:
            t4 = 0

        # 5. ΔLeverage < 0 (leverage decreased)
        lev = row.get('Leverage', np.nan)
        if idx > 0:
            prev_lev = df.iloc[idx - 1].get('Leverage', np.nan)
            try:
                t5 = 1 if (float(lev) - float(prev_lev)) < 0 else 0
            except Exception:
                t5 = 0
        else:
            t5 = 0

        # 6. ΔCurrent Ratio > 0
        cur = row.get('Current Ratio', np.nan)
        if idx > 0:
            prev_cur = df.iloc[idx - 1].get('Current Ratio', np.nan)
            try:
                t6 = 1 if (float(cur) - float(prev_cur)) > 0 else 0
            except Exception:
                t6 = 0
        else:
            t6 = 0

        # 7. No Dilution: shares <= previous year's shares (requires previous)
        shares = row.get('Shares', np.nan)
        if idx > 0:
            prev_shares = df.iloc[idx - 1].get('Shares', np.nan)
            try:
                t7 = 1 if float(shares) <= float(prev_shares) else 0
            except Exception:
                t7 = 0
        else:
            t7 = 0

        # 8. ΔGross Margin > 0
        gm = row.get('Gross Margin', np.nan)
        if idx > 0:
            prev_gm = df.iloc[idx - 1].get('Gross Margin', np.nan)
            try:
                t8 = 1 if (float(gm) - float(prev_gm)) > 0 else 0
            except Exception:
                t8 = 0
        else:
            t8 = 0

        # 9. ΔAsset Turnover > 0
        at = row.get('Asset Turnover (for F-score)', np.nan)
        if idx > 0:
            prev_at = df.iloc[idx - 1].get('Asset Turnover (for F-score)', np.nan)
            try:
                t9 = 1 if (float(at) - float(prev_at)) > 0 else 0
            except Exception:
                t9 = 0
        else:
            t9 = 0

        score = int(t1 + t2 + t3 + t4 + t5 + t6 + t7 + t8 + t9)

        der_rec = {
            'Fiscal Year': to_native(row.get('Fiscal Year')),
            '皮奥特罗斯基 F-Score (Piotroski F-Score)': score
        }
        der_data.append(der_rec)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to output path
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()