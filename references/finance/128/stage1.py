#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,ROA(Avg),CFO,Net Income,Long Term Debt,Avg Total Assets,Leverage,Current Ratio,Current Assets,Current Liabilities,Shares,Gross Margin,Revenue,Cost of Revenue,Asset Turnover (for F-score),1_ROA>0,2_CFO>0,3_dROA>0,4_CFO>NI,5_dLev<0,6_dCurrent>0,7_NoDilute,8_dMargin>0,9_dTurnover>0
2016,0.0736407432897453,8796000000,6527000000,29684000000,88633000000.0,0.3349091196281294,1.28184833408714,34010000000,26532000000,4367000000,0.606693261352507,41863000000,16465000000,0.4723184366996491,1,1,0,1,0,1,1,1,0
2017,0.0142493406254638,7106000000,1248000000,31182000000,87583000000.0,0.3560279963006519,1.3438626167536956,36545000000,27194000000,4324000000,0.6210924555396001,36212000000,13721000000,0.4134592329561672,1,1,0,1,0,1,1,1,0
2018,0.0752022067417831,7627000000,6434000000,25364000000,85556000000.0,0.2964607976062462,0.866166353971232,24930000000,28782000000,4299000000,0.6190379008746356,34300000000,13067000000,0.4009070082752817,1,1,1,1,1,0,1,0,0
2019,0.1051905399270034,10471000000,8920000000,27516000000,84798500000.0,0.3244868718196666,0.7567196826456086,20411000000,26973000000,4314000000,0.6077121236515859,37266000000,14619000000,0.4394653207309091,1,1,1,1,0,0,0,0,1
2020,0.0892115824202398,9844000000,7747000000,40125000000,86838500000.0,0.4620646372288789,1.317717964522978,19240000000,14601000000,4323000000,0.5931120130853578,33014000000,13433000000,0.3801769952267715,1,1,0,1,0,1,0,0,0
2021,0.1075805119735755,12625000000,9771000000,38116000000,90825000000.0,0.419664189375172,1.130075187969925,22545000000,19950000000,4340000000,0.6027163368257664,38655000000,15357000000,0.4255986787778695,1,1,1,1,1,0,0,1,1
2022,0.1019896642207816,11018000000,9542000000,36377000000,93558500000.0,0.3888155539047762,1.145355911579801,22591000000,19724000000,4350000000,0.5814342851827737,43004000000,18000000000,0.4596482414745854,1,1,0,1,1,1,0,0,1
2023,0.1125030189115117,11599000000,10714000000,35547000000,95233000000.0,0.3732634695956233,1.1341054685842773,26732000000,23571000000,4339000000,0.5952266468505486,45754000000,18520000000,0.4804427036846471,1,1,1,1,1,0,1,1,1
2024,0.1072473417670439,6805000000,10631000000,42375000000,99126000000.0,0.4274862296471158,1.0296249356410154,25997000000,25249000000,4320000000,0.6106330082233696,47061000000,18324000000,0.4747593971309243,1,1,0,0,0,0,1,1,0
"""

INDICATOR_NAME = "皮奥特罗斯基 F-Score (Piotroski F-Score)"

def to_python_native(val):
    """Convert numpy/pandas scalar types to native Python types for JSON serialization."""
    if pd.isna(val):
        return None
    # numpy generic types
    if isinstance(val, (np.generic,)):
        try:
            py = val.item()
            # If it's a numpy integer or float, item() gives Python int/float
            return py
        except Exception:
            pass
    # pandas Timestamp etc
    if isinstance(val, (pd.Timestamp,)):
        return val.isoformat()
    # regular python types
    return val

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA), dtype=object)

    # Convert numeric-looking columns to numeric where appropriate
    # We'll attempt to coerce columns (except Fiscal Year) to numeric
    for col in df.columns:
        if col == "Fiscal Year":
            # keep as is (int-like)
            try:
                df[col] = df[col].astype(int)
            except Exception:
                pass
            continue
        # coerce numeric
        df[col] = pd.to_numeric(df[col], errors='ignore')

    # Ensure rows are sorted by Fiscal Year ascending
    if "Fiscal Year" in df.columns:
        try:
            df = df.sort_values("Fiscal Year").reset_index(drop=True)
        except Exception:
            pass

    # Prepare previous-year shifted series for comparisons
    prev_roa = df["ROA(Avg)"].shift(1)
    prev_leverage = df["Leverage"].shift(1) if "Leverage" in df.columns else None
    prev_current_ratio = df["Current Ratio"].shift(1) if "Current Ratio" in df.columns else None
    prev_shares = df["Shares"].shift(1) if "Shares" in df.columns else None
    prev_gross_margin = df["Gross Margin"].shift(1) if "Gross Margin" in df.columns else None
    prev_asset_turn = df["Asset Turnover (for F-score)"].shift(1) if "Asset Turnover (for F-score)" in df.columns else None

    f_scores = []
    der_records = []

    for idx, row in df.iterrows():
        # Extract values, coercing to numeric when possible
        roa = row.get("ROA(Avg)")
        try:
            roa = float(roa)
        except Exception:
            roa = None

        cfo = row.get("CFO")
        try:
            cfo = float(cfo)
        except Exception:
            cfo = None

        net_income = row.get("Net Income")
        try:
            net_income = float(net_income)
        except Exception:
            net_income = None

        leverage = row.get("Leverage")
        try:
            leverage = float(leverage)
        except Exception:
            leverage = None

        current_ratio = row.get("Current Ratio")
        try:
            current_ratio = float(current_ratio)
        except Exception:
            current_ratio = None

        shares = row.get("Shares")
        try:
            shares = float(shares)
        except Exception:
            shares = None

        gross_margin = row.get("Gross Margin")
        try:
            gross_margin = float(gross_margin)
        except Exception:
            gross_margin = None

        asset_turn = row.get("Asset Turnover (for F-score)")
        try:
            asset_turn = float(asset_turn)
        except Exception:
            asset_turn = None

        # Previous year values
        prev_roa_val = prev_roa.iloc[idx] if idx < len(prev_roa) else None
        prev_leverage_val = prev_leverage.iloc[idx] if prev_leverage is not None else None
        prev_current_ratio_val = prev_current_ratio.iloc[idx] if prev_current_ratio is not None else None
        prev_shares_val = prev_shares.iloc[idx] if prev_shares is not None else None
        prev_gross_margin_val = prev_gross_margin.iloc[idx] if prev_gross_margin is not None else None
        prev_asset_turn_val = prev_asset_turn.iloc[idx] if prev_asset_turn is not None else None

        # Coerce previous values to numeric if possible
        try:
            prev_roa_val = float(prev_roa_val) if not pd.isna(prev_roa_val) else None
        except Exception:
            prev_roa_val = None
        try:
            prev_leverage_val = float(prev_leverage_val) if not pd.isna(prev_leverage_val) else None
        except Exception:
            prev_leverage_val = None
        try:
            prev_current_ratio_val = float(prev_current_ratio_val) if not pd.isna(prev_current_ratio_val) else None
        except Exception:
            prev_current_ratio_val = None
        try:
            prev_shares_val = float(prev_shares_val) if not pd.isna(prev_shares_val) else None
        except Exception:
            prev_shares_val = None
        try:
            prev_gross_margin_val = float(prev_gross_margin_val) if not pd.isna(prev_gross_margin_val) else None
        except Exception:
            prev_gross_margin_val = None
        try:
            prev_asset_turn_val = float(prev_asset_turn_val) if not pd.isna(prev_asset_turn_val) else None
        except Exception:
            prev_asset_turn_val = None

        # 1. ROA > 0
        score_roa_pos = 1 if (roa is not None and roa > 0) else 0

        # 2. CFO > 0
        score_cfo_pos = 1 if (cfo is not None and cfo > 0) else 0

        # 3. ΔROA > 0 (year-over-year increase)
        score_droa_pos = 0
        if (roa is not None) and (prev_roa_val is not None):
            if roa > prev_roa_val:
                score_droa_pos = 1

        # 4. Accruals: CFO > Net Income
        score_accrual = 0
        if (cfo is not None) and (net_income is not None):
            if cfo > net_income:
                score_accrual = 1

        # 5. ΔLeverage < 0 (leverage decreased)
        score_dlev_neg = 0
        if (leverage is not None) and (prev_leverage_val is not None):
            if leverage < prev_leverage_val:
                score_dlev_neg = 1

        # 6. ΔCurrent Ratio > 0
        score_dcurrent_pos = 0
        if (current_ratio is not None) and (prev_current_ratio_val is not None):
            if current_ratio > prev_current_ratio_val:
                score_dcurrent_pos = 1

        # 7. No Dilution: shares not increased this year (<= prev year). If no prev year, assume no dilution.
        score_nodilute = 1
        if prev_shares_val is not None and shares is not None:
            if shares <= prev_shares_val:
                score_nodilute = 1
            else:
                score_nodilute = 0
        # if prev_shares_val is None, keep score_nodilute = 1

        # 8. ΔGross Margin > 0
        score_dgm_pos = 0
        if (gross_margin is not None) and (prev_gross_margin_val is not None):
            if gross_margin > prev_gross_margin_val:
                score_dgm_pos = 1

        # 9. ΔAsset Turnover > 0
        score_dassetturn_pos = 0
        if (asset_turn is not None) and (prev_asset_turn_val is not None):
            if asset_turn > prev_asset_turn_val:
                score_dassetturn_pos = 1

        # Sum to get F-Score
        components = [
            score_roa_pos,
            score_cfo_pos,
            score_droa_pos,
            score_accrual,
            score_dlev_neg,
            score_dcurrent_pos,
            score_nodilute,
            score_dgm_pos,
            score_dassetturn_pos
        ]
        f_score = int(sum(components))

        fiscal_year = row.get("Fiscal Year")
        try:
            fiscal_year_py = int(fiscal_year)
        except Exception:
            fiscal_year_py = to_python_native(fiscal_year)

        der_record = {
            "Fiscal Year": fiscal_year_py,
            INDICATOR_NAME: f_score
        }
        der_records.append(der_record)
        f_scores.append(f_score)

    # Prepare scr_data: original rows as list of dicts with native types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            val = row[col]
            rec[col] = to_python_native(val)
        scr_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()