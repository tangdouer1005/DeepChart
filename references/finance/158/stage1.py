#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,ROA(Avg),CFO,Net Income,Long Term Debt,Avg Total Assets,Leverage,Current Ratio,Current Assets,Current Liabilities,Shares,Gross Margin,Revenue,Cost of Revenue,Asset Turnover (for F-score),1_ROA>0,2_CFO>0,3_dROA>0,4_CFO>NI,5_dLev<0,6_dCurrent>0,7_NoDilute,8_dMargin>0,9_dTurnover>0
2016,0.1786688584219362,16108000000,10217000000,112000000.0,57184000000.0,0.0019585898153329,11.965565217391305,34401000000.0,2875000000.0,2925000000,0.8629061437151747,27638000000,3789000000,0.4833170117515389,1,1,1,1,1,1,0,1,1
2017,0.2131852694250259,24216000000,15934000000,72000000.0,74742500000.0,0.000963307355253,12.915691489361702,48563000000.0,3760000000.0,2956000000,0.8658401593978304,40653000000,5454000000,0.5439074154597451,1,1,1,1,1,1,0,1,1
2022,0.1319253711822674,50475000000,23200000000,9923000000.0,175857000000.0,0.0564265283724844,2.203396729075705,59549000000.0,27026000000.0,2702000000,0.7834729737841848,116609000000,25249000000,0.6630898969048715,1,1,0,1,0,0,1,0,0
2023,0.1882653184061634,71113000000,39098000000,18385000000.0,207675000000.0,0.0885277476826772,2.6709949937421777,85365000000.0,31960000000.0,2629000000,0.8075714222176098,134902000000,25959000000,0.6495822800048152,1,1,1,1,0,1,1,1,0
2024,0.2466396533755737,91328000000,62360000000,28826000000.0,252838500000.0,0.1140095357313067,2.9778842719371355,100045000000.0,33596000000.0,2614000000,0.8166515705071702,164501000000,30161000000,0.6506168957654788,1,1,1,1,0,1,1,1,1
"""

def to_native(v):
    # Convert numpy/pandas scalar to native python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    return v

def compute_piotroski_f_scores(df):
    scores = []
    # Ensure DataFrame is sorted by Fiscal Year ascending as in CSV
    # If Fiscal Year column exists, sort by it to guarantee previous-year comparisons make sense
    year_col = None
    for c in df.columns:
        if c.lower().strip() in ("fiscal year", "year"):
            year_col = c
            break
    if year_col is not None:
        try:
            df = df.sort_values(by=year_col).reset_index(drop=True)
        except Exception:
            df = df.reset_index(drop=True)
    else:
        df = df.reset_index(drop=True)

    for i in range(len(df)):
        row = df.iloc[i]
        prev = df.iloc[i - 1] if i > 0 else None

        # Raw values used for each subscore
        roa = float(row["ROA(Avg)"]) if not pd.isna(row["ROA(Avg)"]) else None
        cfo = float(row["CFO"]) if not pd.isna(row["CFO"]) else None
        ni = float(row["Net Income"]) if not pd.isna(row["Net Income"]) else None
        lev = float(row["Leverage"]) if not pd.isna(row["Leverage"]) else None
        cur = float(row["Current Ratio"]) if not pd.isna(row["Current Ratio"]) else None
        shares = row["Shares"] if "Shares" in df.columns else None
        gm = float(row["Gross Margin"]) if not pd.isna(row["Gross Margin"]) else None
        at = float(row["Asset Turnover (for F-score)"]) if not pd.isna(row["Asset Turnover (for F-score)"]) else None

        # 1. ROA > 0
        s1 = 1 if (roa is not None and roa > 0) else 0

        # 2. CFO > 0
        s2 = 1 if (cfo is not None and cfo > 0) else 0

        # 3. ΔROA > 0
        if prev is None:
            s3 = 0
        else:
            prev_roa = float(prev["ROA(Avg)"]) if not pd.isna(prev["ROA(Avg)"]) else None
            s3 = 1 if (prev_roa is not None and roa is not None and (roa - prev_roa) > 0) else 0

        # 4. Accruals: CFO > Net Income
        s4 = 1 if (cfo is not None and ni is not None and cfo > ni) else 0

        # 5. ΔLeverage < 0 (long-term debt ratio decreased)
        if prev is None:
            s5 = 0
        else:
            prev_lev = float(prev["Leverage"]) if not pd.isna(prev["Leverage"]) else None
            s5 = 1 if (prev_lev is not None and lev is not None and lev < prev_lev) else 0

        # 6. ΔCurrent Ratio > 0
        if prev is None:
            s6 = 0
        else:
            prev_cur = float(prev["Current Ratio"]) if not pd.isna(prev["Current Ratio"]) else None
            s6 = 1 if (prev_cur is not None and cur is not None and cur > prev_cur) else 0

        # 7. No Dilution: shares did not increase (this year <= previous year)
        if prev is None:
            s7 = 0
        else:
            prev_shares = prev["Shares"] if "Shares" in df.columns else None
            # if either is missing, treat as 0 (cannot confirm no dilution)
            if pd.isna(prev_shares) or pd.isna(shares):
                s7 = 0
            else:
                try:
                    s7 = 1 if float(shares) <= float(prev_shares) else 0
                except Exception:
                    s7 = 0

        # 8. ΔGross Margin > 0
        if prev is None:
            s8 = 0
        else:
            prev_gm = float(prev["Gross Margin"]) if not pd.isna(prev["Gross Margin"]) else None
            s8 = 1 if (prev_gm is not None and gm is not None and gm > prev_gm) else 0

        # 9. ΔAsset Turnover > 0
        if prev is None:
            s9 = 0
        else:
            prev_at = float(prev["Asset Turnover (for F-score)"]) if not pd.isna(prev["Asset Turnover (for F-score)"]) else None
            s9 = 1 if (prev_at is not None and at is not None and at > prev_at) else 0

        total = int(s1 + s2 + s3 + s4 + s5 + s6 + s7 + s8 + s9)

        entry = {}
        if year_col:
            entry[year_col] = to_native(row[year_col])
        entry["皮奥特罗斯基 F-Score (Piotroski F-Score)"] = total
        scores.append(entry)

    return scores

def dataframe_to_scr_data(df):
    rows = []
    for _, r in df.iterrows():
        d = {}
        for c in df.columns:
            d[c] = to_native(r[c])
        rows.append(d)
    return rows

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))
    # Compute derived data
    der = compute_piotroski_f_scores(df)
    scr = dataframe_to_scr_data(df)

    out = {"scr_data": scr, "der_data": der}

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()