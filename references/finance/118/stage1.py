import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,ROA(Avg),CFO,Net Income,Long Term Debt,Avg Total Assets,Leverage,Current Ratio,Current Assets,Current Liabilities,Shares,Gross Margin,Revenue,Cost of Revenue,Asset Turnover (for F-score),1_ROA>0,2_CFO>0,3_dROA>0,4_CFO>NI,5_dLev<0,6_dCurrent>0,7_NoDilute,8_dMargin>0,9_dTurnover>0
2016,0.1204577978945375,18767000000,16540000000,22442000000,137309500000.0,0.163440985510835,2.473922471183475,65032000000,26287000000,2788900000,0.696911948810683,71890000000,21789000000,0.523561734621421,1,1,1,1,0,1,1,1,0
2017,0.008709896787723,21056000000,1300000000,30675000000,149255500000.0,0.2055200645872346,1.4110095949176409,43088000000,30537000000,2745300000,0.6672465663832571,76450000000,25439000000,0.5122089303241757,1,1,0,1,0,0,1,0,0
2018,0.0986085728927953,22201000000,15297000000,27684000000,155128500000.0,0.1784585037565631,1.4739993595901375,46033000000,31230000000,2728700000,0.6679251296257707,81581000000,27091000000,0.5258930499553596,1,1,1,1,1,1,1,1,1
2019,0.0973278142924276,23416000000,15119000000,26494000000,155341000000.0,0.1705538138675559,1.2588699810922033,45274000000,35964000000,2684300000,0.6641928368612827,82059000000,27556000000,0.5282507515723472,1,1,0,1,1,0,1,0,1
2020,0.0884728009572427,23536000000,14714000000,32635000000,166311000000.0,0.1962287521571032,1.205775068834867,51237000000,42493000000,2670700000,0.6557807807807807,82584000000,28427000000,0.4965636668650901,1,1,0,1,0,0,1,0,0
2021,0.1169924239028107,23410000000,20878000000,29985000000,178456000000.0,0.1680246111086206,1.3483173395834254,60979000000,45226000000,2674000000,0.7027940055880112,78740000000,23402000000,0.4412292105617071,1,1,1,1,1,1,0,1,0
2022,0.0971369478824892,21194000000,17941000000,26888000000,184698000000.0,0.1455781870946084,0.9908963836421634,55294000000,55802000000,2663900000,0.6925115639454932,79990000000,24596000000,0.4330853609676336,1,1,0,1,1,0,1,0,0
2023,0.1980807807604751,22791000000,35153000000,25881000000,177468000000.0,0.1458347420380012,1.1558489261483946,53495000000,46282000000,2560400000,0.6860108737772872,85159000000,26739000000,0.4798555232492618,1,1,1,0,0,1,1,0,1
2024,0.0809176729121963,24266000000,14066000000,30651000000,173831000000.0,0.1763264319942933,1.1107291190556627,55893000000,50321000000,2429400000,0.6907150336069173,88821000000,27471000000,0.5109617962273703,1,1,0,1,0,0,1,1,1
"""

INDICATOR_NAME = "皮奥特罗斯基 F-Score (Piotroski F-Score)"

def normalize_value(v):
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    # plain python types
    return v

def row_to_pytypes(row_dict):
    return {k: normalize_value(v) for k, v in row_dict.items()}

def compute_piotroski_scores(df):
    scores = []
    # ensure sorted by Fiscal Year ascending if not already
    df_sorted = df.copy().reset_index(drop=True)
    # iterate rows
    for i in range(len(df_sorted)):
        r = df_sorted.loc[i]
        score = 0
        # 1. ROA > 0
        roa = r.get("ROA(Avg)")
        try:
            cond1 = (roa is not None) and (not pd.isna(roa)) and (float(roa) > 0)
        except Exception:
            cond1 = False
        score += 1 if cond1 else 0

        # 2. CFO > 0
        cfo = r.get("CFO")
        try:
            cond2 = (cfo is not None) and (not pd.isna(cfo)) and (float(cfo) > 0)
        except Exception:
            cond2 = False
        score += 1 if cond2 else 0

        # For year-over-year comparisons, need previous row
        if i == 0:
            # can't compute deltas for first year -> treat as 0
            cond3 = False
            cond5 = False
            cond6 = False
            cond7 = False
            cond8 = False
            cond9 = False
        else:
            prev = df_sorted.loc[i-1]
            # 3. delta ROA > 0
            try:
                prev_roa = prev.get("ROA(Avg)")
                cond3 = (not pd.isna(roa)) and (not pd.isna(prev_roa)) and (float(roa) - float(prev_roa) > 0)
            except Exception:
                cond3 = False

            # 4. Accruals: CFO > Net Income
            # (this is not Y-o-Y; computed for current year)
            # handled below outside this block

            # 5. delta Leverage < 0 (leverage decreased)
            try:
                lev = r.get("Leverage")
                prev_lev = prev.get("Leverage")
                cond5 = (not pd.isna(lev)) and (not pd.isna(prev_lev)) and (float(lev) - float(prev_lev) < 0)
            except Exception:
                cond5 = False

            # 6. delta Current Ratio > 0
            try:
                cur = r.get("Current Ratio")
                prev_cur = prev.get("Current Ratio")
                cond6 = (not pd.isna(cur)) and (not pd.isna(prev_cur)) and (float(cur) - float(prev_cur) > 0)
            except Exception:
                cond6 = False

            # 7. No Dilution: shares did not increase (current Shares <= previous Shares)
            try:
                sh = r.get("Shares")
                prev_sh = prev.get("Shares")
                cond7 = (not pd.isna(sh)) and (not pd.isna(prev_sh)) and (float(sh) <= float(prev_sh))
            except Exception:
                cond7 = False

            # 8. delta Gross Margin > 0
            try:
                gm = r.get("Gross Margin")
                prev_gm = prev.get("Gross Margin")
                cond8 = (not pd.isna(gm)) and (not pd.isna(prev_gm)) and (float(gm) - float(prev_gm) > 0)
            except Exception:
                cond8 = False

            # 9. delta Asset Turnover > 0
            try:
                at = r.get("Asset Turnover (for F-score)")
                prev_at = prev.get("Asset Turnover (for F-score)")
                cond9 = (not pd.isna(at)) and (not pd.isna(prev_at)) and (float(at) - float(prev_at) > 0)
            except Exception:
                cond9 = False

        # 4. Accruals (CFO > Net Income)
        try:
            ni = r.get("Net Income")
            cond4 = (not pd.isna(cfo)) and (not pd.isna(ni)) and (float(cfo) > float(ni))
        except Exception:
            cond4 = False

        # Add each condition to score (cond3..cond9 may be defined above)
        score += 1 if cond3 else 0
        score += 1 if cond4 else 0
        score += 1 if cond5 else 0
        score += 1 if cond6 else 0
        score += 1 if cond7 else 0
        score += 1 if cond8 else 0
        score += 1 if cond9 else 0

        # prepare output dict; include Fiscal Year if present
        out = {}
        if "Fiscal Year" in df_sorted.columns:
            # convert to native type
            fy = r.get("Fiscal Year")
            out["Fiscal Year"] = normalize_value(fy)
        out[INDICATOR_NAME] = int(score)
        scores.append(out)

    return scores

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA), dtype=object)
    # Convert numeric-looking columns to numeric types where appropriate
    # We'll attempt to convert each column to numeric if possible
    for col in df.columns:
        # keep Fiscal Year as int if possible
        if col == "Fiscal Year":
            try:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype(pd.Int64Dtype())
            except Exception:
                pass
        else:
            # try numeric conversion
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Prepare scr_data as list of dicts with native Python types
    scr_records = []
    for rec in df.to_dict(orient="records"):
        scr_records.append(row_to_pytypes(rec))

    der_records = compute_piotroski_scores(df)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # write JSON
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()