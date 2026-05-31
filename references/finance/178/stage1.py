#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,ROA(Avg),CFO,Net Income,Long Term Debt,Avg Total Assets,Leverage,Current Ratio,Current Assets,Current Liabilities,Shares,Gross Margin,Revenue,Cost of Revenue,Asset Turnover (for F-score),1_ROA>0,2_CFO>0,3_dROA>0,4_CFO>NI,5_dLev<0,6_dCurrent>0,7_NoDilute,8_dMargin>0,9_dTurnover>0
2016,0.1115746701216299,33325000000,20539000000,40783000000.0,184083000000.0,0.2215468022576772,2.3528817157201343,139660000000,59357000000,8013000000,0.6403887925927552,91154000000,32780000000,0.4951788052128659,1,1,1,1,0,0,1,0,0
2017,0.117250103500621,39507000000,25489000000,76073000000.0,217390000000.0,0.3499378996273977,2.4772730794861064,159851000000,64527000000,7832000000,0.6452247569146017,96571000000,34261000000,0.4442292653755922,1,1,1,1,0,1,1,1,0
2018,0.0662927506430848,43884000000,16571000000,72242000000.0,249967000000.0,0.2890061488116431,2.900800164136233,169662000000,58488000000,7794000000,0.652473722363175,110360000000,38353000000,0.441498277772666,1,1,0,1,1,1,1,1,0
2019,0.143893334115628,52185000000,39240000000,66662000000.0,272702000000.0,0.2444499856986747,2.5288389513108616,175552000000,69420000000,7753000000,0.6590195720063889,125843000000,42910000000,0.4614670959508914,1,1,1,1,1,0,1,1,1
2020,0.1506497217908132,60675000000,44281000000,59578000000.0,293933500000.0,0.2026921055272706,2.515765454294012,181915000000,72310000000,7683000000,0.6778100199279796,143015000000,46078000000,0.4865556324814967,1,1,1,1,1,0,1,1,1
2021,0.1929521800059834,76740000000,61271000000,50074000000.0,317545000000.0,0.1576910359161693,2.0799936835218875,184406000000,88657000000,7608000000,0.689258007710247,168088000000,52232000000,0.5293359996221008,1,1,1,1,1,0,1,1,1
2022,0.2082336724308958,89035000000,72738000000,47032000000.0,349309500000.0,0.1346427738151982,1.7846069708251824,169684000000,95082000000,7540000000,0.684016744842891,198270000000,62650000000,0.5676055188879776,1,1,1,1,1,0,1,0,1
2023,0.1863015179913905,87582000000,72361000000,41990000000.0,388408000000.0,0.1081079689398776,1.76916725076573,184257000000,104149000000,7472000000,0.6892008588349102,211915000000,65863000000,0.5455989577969558,1,1,0,1,1,0,1,1,0
2024,0.1907418689179874,118548000000,88136000000,42688000000.0,462069500000.0,0.0923843707494218,1.2749549031815206,159734000000,125286000000,7469000000,0.6976444382797138,245122000000,74114000000,0.5304872968243954,1,1,1,1,1,0,1,1,0
"""

INDICATOR_NAME = "皮奥特罗斯基 F-Score (Piotroski F-Score)"

def _convert_numpy(val):
    # Convert numpy and pandas scalar types to native Python types for JSON serialization
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, (np.bool_ , bool)):
        return bool(val)
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA), dtype=object)

    # Convert numeric-like columns where possible
    # We'll attempt to convert typical numeric columns to floats/ints
    numeric_cols = [
        "ROA(Avg)","CFO","Net Income","Long Term Debt","Avg Total Assets","Leverage",
        "Current Ratio","Current Assets","Current Liabilities","Shares","Gross Margin",
        "Revenue","Cost of Revenue","Asset Turnover (for F-score)"
    ]
    for col in numeric_cols:
        if col in df.columns:
            # Convert to numeric where possible; coerce errors to NaN
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Prepare scr_data as list of dicts with converted basic Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = _convert_numpy(row[col])
        scr_records.append(rec)

    # Calculate Piotroski F-Score for each row
    der_records = []
    prev = None  # store previous row's relevant metrics
    for idx, row in df.iterrows():
        # Extract current values (use None if missing)
        year = row.get("Fiscal Year", None)
        try:
            year_val = int(year) if not pd.isna(year) else None
        except Exception:
            year_val = year

        roa = row.get("ROA(Avg)", None)
        cfo = row.get("CFO", None)
        net_income = row.get("Net Income", None)
        leverage = row.get("Leverage", None)
        current_ratio = row.get("Current Ratio", None)
        gross_margin = row.get("Gross Margin", None)
        asset_turnover = row.get("Asset Turnover (for F-score)", None)
        shares = row.get("Shares", None)

        # Define helper to safely compare numeric values; returns False if comparison not possible
        def gt(a, b):
            try:
                return (a is not None) and (b is not None) and (float(a) > float(b))
            except Exception:
                return False

        def lt(a, b):
            try:
                return (a is not None) and (b is not None) and (float(a) < float(b))
            except Exception:
                return False

        def ge(a, b):
            try:
                return (a is not None) and (b is not None) and (float(a) >= float(b))
            except Exception:
                return False

        # 1. ROA > 0
        score_roa_pos = 1 if gt(roa, 0) else 0

        # 2. CFO > 0
        score_cfo_pos = 1 if gt(cfo, 0) else 0

        # 3. ΔROA > 0 (compare to previous year's ROA)
        if prev is not None:
            prev_roa = prev.get("ROA(Avg)", None)
            score_droa = 1 if gt(roa, prev_roa) else 0
        else:
            score_droa = 0

        # 4. Accruals: CFO > Net Income
        score_accruals = 1 if ( (cfo is not None) and (net_income is not None) and (float(cfo) > float(net_income)) ) else 0

        # 5. ΔLeverage < 0 (leverage decreased vs prior year)
        if prev is not None:
            prev_lev = prev.get("Leverage", None)
            # decrease means current < previous
            score_dlev = 1 if lt(leverage, prev_lev) else 0
        else:
            score_dlev = 0

        # 6. ΔCurrent Ratio > 0
        if prev is not None:
            prev_current = prev.get("Current Ratio", None)
            score_dcurrent = 1 if gt(current_ratio, prev_current) else 0
        else:
            score_dcurrent = 0

        # 7. No Dilution: current shares <= previous shares
        if prev is not None:
            prev_shares = prev.get("Shares", None)
            # If shares decreased or equal -> no dilution (1). If increased -> dilution (0).
            if (shares is None) or (prev_shares is None):
                score_nodilute = 0
            else:
                try:
                    score_nodilute = 1 if float(shares) <= float(prev_shares) else 0
                except Exception:
                    score_nodilute = 0
        else:
            score_nodilute = 0

        # 8. ΔGross Margin > 0
        if prev is not None:
            prev_margin = prev.get("Gross Margin", None)
            score_dmargin = 1 if gt(gross_margin, prev_margin) else 0
        else:
            score_dmargin = 0

        # 9. ΔAsset Turnover > 0
        if prev is not None:
            prev_turn = prev.get("Asset Turnover (for F-score)", None)
            score_dturn = 1 if gt(asset_turnover, prev_turn) else 0
        else:
            score_dturn = 0

        # Sum up the 9 binary scores
        total_score = int(
            score_roa_pos + score_cfo_pos + score_droa + score_accruals +
            score_dlev + score_dcurrent + score_nodilute + score_dmargin + score_dturn
        )

        # Build derived record; include Year if available
        der_rec = {}
        if year_val is not None:
            der_rec["Year"] = year_val
        elif "Fiscal Year" in row:
            # fallback: include raw fiscal year value
            der_rec["Year"] = _convert_numpy(row.get("Fiscal Year"))

        der_rec[INDICATOR_NAME] = total_score

        # Optionally include breakdown? Requirement says dictionary contains the calculated indicator value.
        # We'll include only Year and the indicator value to meet spec.
        der_records.append(der_rec)

        # update prev
        prev = {
            "ROA(Avg)": roa,
            "Leverage": leverage,
            "Current Ratio": current_ratio,
            "Gross Margin": gross_margin,
            "Asset Turnover (for F-score)": asset_turnover,
            "Shares": shares
        }

    # Final JSON object
    out_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()