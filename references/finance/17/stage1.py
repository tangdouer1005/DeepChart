#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,ROA(Avg),CFO,Net Income,Long Term Debt,Avg Total Assets,Leverage,Current Ratio,Current Assets,Current Liabilities,Shares,Gross Margin,Revenue,Cost of Revenue,Asset Turnover (for F-score),1_ROA>0,2_CFO>0,3_dROA>0,4_CFO>NI,5_dLev<0,6_dCurrent>0,7_NoDilute,8_dMargin>0,9_dTurnover>0
2016,0.0282794004767098,3203000000,1400000000,20681000000,49506000000.0,0.4177473437563123,4.020420420420421,26776000000,6660000000,1483000000,0.5392029923751979,20853000000,9609000000,0.4212216701005938,1,1,0,1,0,1,1,1,0
2017,0.0072679623041116,5570000000,477000000,27210000000,65630500000.0,0.4145938245175642,2.2606597845601435,20147000000,8912000000,1749000000,0.4770354143848119,27390000000,14324000000,0.4173364518021347,1,1,0,1,1,0,0,0,0
2018,0.0330212030148581,6300000000,2368000000,19359000000,71711500000.0,0.2699567015053373,1.623612960497115,14632000000,9012000000,1770000000,0.517463535875466,30578000000,14755000000,0.4264030176470998,1,1,1,1,1,0,0,1,1
2019,0.0545979564637938,6136000000,3687000000,16661000000,67530000000.0,0.2467199763068266,1.442235110006444,15667000000,10863000000,1781000000,0.5232259277833501,31904000000,15211000000,0.4724418776839923,1,1,1,1,1,0,0,1,1
2020,0.0640153807811443,7901000000,4495000000,18527000000,70217500000.0,0.2638516039448855,1.716721256403796,20441000000,11907000000,1786000000,0.5021093388811836,34608000000,17231000000,0.4928685868907324,1,1,1,1,0,1,0,0,1
2021,0.0957196231319038,10533000000,7071000000,17296000000,73872000000.0,0.2341347195148364,1.8495993895459748,24239000000,13105000000,1789000000,0.5389204875217644,43075000000,19861000000,0.583103205544726,1,1,1,1,1,1,0,1,1
2022,0.0926661052969245,9581000000,6933000000,14522000000,74817000000.0,0.1941002713287087,1.6285105558783652,25224000000,15489000000,1764000000,0.5113737887430417,43653000000,21330000000,0.5834636513091944,1,1,0,1,1,0,1,0,1
2023,0.0775201148646818,7261000000,5723000000,13599000000,73826000000.0,0.1842033971771462,1.6378874358789104,22670000000,13841000000,1749000000,0.4995636889476177,40109000000,20072000000,0.5432909814970336,1,1,0,1,1,1,1,0,0
2024,0.1733450604030318,8558000000,13402000000,12625000000,77314000000.0,0.1632951341283596,1.6709754891573074,23656000000,14157000000,1748000000,0.5083432657926102,41950000000,20625000000,0.5425925446878961,1,1,1,0,1,1,1,1,0
"""

def to_native(value):
    # Convert numpy and pandas types to native Python types for JSON serialization
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
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Build scr_data: list of dicts mirroring input CSV rows
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_data.append(rec)

    # Calculate Piotroski F-Score per row
    der_data = []
    # Columns used (exact names from CSV)
    col_roa = "ROA(Avg)"
    col_cfo = "CFO"
    col_net = "Net Income"
    col_leverage = "Leverage"
    col_current = "Current Ratio"
    col_shares = "Shares"
    col_gross = "Gross Margin"
    col_turn = "Asset Turnover (for F-score)"
    col_year = "Fiscal Year"

    prev_row = None
    for idx, row in df.iterrows():
        score_components = {}

        # 1. ROA > 0
        roa_pos = (row[col_roa] > 0) if not pd.isna(row[col_roa]) else False
        score_components['ROA>0'] = 1 if roa_pos else 0

        # 2. CFO > 0
        cfo_pos = (row[col_cfo] > 0) if not pd.isna(row[col_cfo]) else False
        score_components['CFO>0'] = 1 if cfo_pos else 0

        # 3. ΔROA > 0 (requires prior year)
        if prev_row is None or pd.isna(prev_row[col_roa]) or pd.isna(row[col_roa]):
            d_roa_pos = False
        else:
            d_roa_pos = (row[col_roa] > prev_row[col_roa])
        score_components['dROA>0'] = 1 if d_roa_pos else 0

        # 4. Accruals: CFO > Net Income
        if pd.isna(row[col_cfo]) or pd.isna(row[col_net]):
            accruals_high = False
        else:
            accruals_high = (row[col_cfo] > row[col_net])
        score_components['CFO>NetIncome'] = 1 if accruals_high else 0

        # 5. ΔLeverage < 0 (leverage decreased)
        if prev_row is None or pd.isna(prev_row[col_leverage]) or pd.isna(row[col_leverage]):
            d_lev_decrease = False
        else:
            d_lev_decrease = (row[col_leverage] < prev_row[col_leverage])
        score_components['dLeverage<0'] = 1 if d_lev_decrease else 0

        # 6. ΔCurrent Ratio > 0
        if prev_row is None or pd.isna(prev_row[col_current]) or pd.isna(row[col_current]):
            d_current_up = False
        else:
            d_current_up = (row[col_current] > prev_row[col_current])
        score_components['dCurrent>0'] = 1 if d_current_up else 0

        # 7. No Dilution: current shares <= prior shares (or True for first year)
        if prev_row is None or pd.isna(row[col_shares]):
            no_dilute = True
        elif pd.isna(prev_row[col_shares]):
            no_dilute = True
        else:
            no_dilute = (row[col_shares] <= prev_row[col_shares])
        score_components['NoDilution'] = 1 if no_dilute else 0

        # 8. ΔGross Margin > 0
        if prev_row is None or pd.isna(prev_row[col_gross]) or pd.isna(row[col_gross]):
            d_gross_up = False
        else:
            d_gross_up = (row[col_gross] > prev_row[col_gross])
        score_components['dGrossMargin>0'] = 1 if d_gross_up else 0

        # 9. ΔAsset Turnover > 0
        if prev_row is None or pd.isna(prev_row[col_turn]) or pd.isna(row[col_turn]):
            d_turn_up = False
        else:
            d_turn_up = (row[col_turn] > prev_row[col_turn])
        score_components['dAssetTurnover>0'] = 1 if d_turn_up else 0

        # Sum components for F-Score
        f_score = (
            score_components['ROA>0']
            + score_components['CFO>0']
            + score_components['dROA>0']
            + score_components['CFO>NetIncome']
            + score_components['dLeverage<0']
            + score_components['dCurrent>0']
            + score_components['NoDilution']
            + score_components['dGrossMargin>0']
            + score_components['dAssetTurnover>0']
        )

        der_rec = {
            col_year: to_native(row[col_year]),
            "皮奥特罗斯基 F-Score (Piotroski F-Score)": int(f_score)
        }
        der_data.append(der_rec)

        prev_row = row

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()