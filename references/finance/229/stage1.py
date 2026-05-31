#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,ROA(Avg),CFO,Net Income,Long Term Debt,Avg Total Assets,Leverage,Current Ratio,Current Assets,Current Liabilities,Shares,Gross Margin,Revenue,Cost of Revenue,Asset Turnover (for F-score),1_ROA>0,2_CFO>0,3_dROA>0,4_CFO>NI,5_dLev<0,6_dCurrent>0,7_NoDilute,8_dMargin>0,9_dTurnover>0
2016,0.0466162414416034,3156300000,2021800000,15372400000,43371150000.0,0.3544383766628277,1.4428688861487875,7021000000,4866000000,397400000,0.4696209389244887,18274100000,9692200000,0.421342297817789,1,1,0,1,0,1,1,1,1
2017,0.0433820447078779,4005000000,2225000000,18873000000,51288500000.0,0.3679772268637218,1.3366912599318956,9421000000,7048000000,398000000,0.4627115403002199,20918000000,11239000000,0.407849712898603,1,1,0,1,0,0,0,0,0
2018,0.0520455974703501,4543000000,2938000000,17719000000,56450500000.0,0.3138856166021558,1.728485440052058,10625000000,6147000000,406000000,0.4511043599638722,24358000000,13370000000,0.4314930780063949,1,1,1,1,1,1,0,0,1
2019,0.0644953015800999,4973000000,3696000000,17076000000,57306500000.0,0.2979766693132541,1.919154429562692,11893000000,6197000000,403000000,0.4441312348289092,25542000000,14198000000,0.4457086019910481,1,1,1,1,1,1,1,0,1
2020,0.1000525766481209,8289000000,6375000000,19107000000,63716500000.0,0.2998752285514741,2.1309200310559007,21957000000,10304000000,399000000,0.4974548389099261,32218000000,16191000000,0.5056461042273195,1,1,1,1,0,1,1,1,1
2021,0.0941068981269986,9543000000,7725000000,32333000000,82087500000.0,0.3938845743870869,1.496948496576362,20113000000,13436000000,397000000,0.5007268368570044,39211000000,19577000000,0.4776732145576366,1,1,0,1,0,0,1,1,0
2022,0.0722915377294216,9154000000,6950000000,28909000000,96138500000.0,0.3007015919740791,1.4831863609641387,25229000000,17010000000,394000000,0.4232661694311477,44915000000,25904000000,0.4671905636139528,1,1,0,1,1,0,1,0,0
2023,0.0612109454768225,8406000000,5995000000,31308000000,97940000000.0,0.3196651010822953,1.7548529831572937,24589000000,14012000000,388000000,0.4097813659378864,42857000000,25295000000,0.437584235246069,1,1,0,1,0,1,1,0,0
2024,0.0646273597657704,8667000000,6335000000,29061000000,98023500000.0,0.2964697240967727,1.6604410441044104,22137000000,13332000000,383000000,0.4134424776697217,42879000000,25151000000,0.4374359209781328,1,1,1,1,1,0,1,1,0
"""

def to_native(value):
    """Convert numpy/pandas scalar types to native Python types and handle NaN."""
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    try:
        # catch pandas Timestamp, numpy types, etc.
        if hasattr(value, "item"):
            return value.item()
    except Exception:
        pass
    return value

def dataframe_to_pylist(df):
    records = df.to_dict(orient='records')
    py_records = []
    for r in records:
        pr = {}
        for k, v in r.items():
            pr[k] = to_native(v)
        py_records.append(pr)
    return py_records

def compute_piotroski_fscore(df):
    # Ensure columns exist
    # Relevant columns names from CSV:
    # 'Fiscal Year','ROA(Avg)','CFO','Net Income','Leverage','Current Ratio','Shares','Gross Margin','Asset Turnover (for F-score)'
    roa = df['ROA(Avg)']
    cfo = df['CFO']
    ni = df['Net Income']
    leverage = df['Leverage']
    current_ratio = df['Current Ratio']
    shares = df['Shares']
    gross_margin = df['Gross Margin']
    asset_turn = df['Asset Turnover (for F-score)']

    # Compute year-over-year deltas using shift
    prev_roa = roa.shift(1)
    prev_leverage = leverage.shift(1)
    prev_current = current_ratio.shift(1)
    prev_shares = shares.shift(1)
    prev_gross_margin = gross_margin.shift(1)
    prev_asset_turn = asset_turn.shift(1)

    # 1. ROA > 0
    cond1 = roa > 0

    # 2. CFO > 0
    cond2 = cfo > 0

    # 3. ΔROA > 0 (YoY increase). For first available year, treat as False (no previous year).
    cond3 = (roa - prev_roa) > 0
    cond3 = cond3.fillna(False)

    # 4. Accruals: CFO > Net Income (high earnings quality)
    cond4 = cfo > ni

    # 5. ΔLeverage < 0 (long-term leverage decreased)
    cond5 = (leverage - prev_leverage) < 0
    cond5 = cond5.fillna(False)

    # 6. ΔCurrent Ratio > 0 (current ratio improved)
    cond6 = (current_ratio - prev_current) > 0
    cond6 = cond6.fillna(False)

    # 7. No Dilution: no new shares issued this year (shares did not increase)
    # If previous year not available, treat as False (conservative)
    cond7 = shares <= prev_shares
    cond7 = cond7.fillna(False)

    # 8. ΔGross Margin > 0
    cond8 = (gross_margin - prev_gross_margin) > 0
    cond8 = cond8.fillna(False)

    # 9. ΔAsset Turnover > 0
    cond9 = (asset_turn - prev_asset_turn) > 0
    cond9 = cond9.fillna(False)

    # Convert boolean series to integers and sum
    score_series = (
        cond1.astype(int)
        + cond2.astype(int)
        + cond3.astype(int)
        + cond4.astype(int)
        + cond5.astype(int)
        + cond6.astype(int)
        + cond7.astype(int)
        + cond8.astype(int)
        + cond9.astype(int)
    )

    return score_series

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Compute F-Score
    fscore_series = compute_piotroski_fscore(df)

    # Build scr_data (original scraped data) as list of native dicts
    scr_data = dataframe_to_pylist(df)

    # Build der_data with Fiscal Year and calculated indicator
    der_data = []
    indicator_name = "皮奥特罗斯基 F-Score (Piotroski F-Score)"
    for idx, row in df.iterrows():
        fy = row.get('Fiscal Year', None)
        score = to_native(fscore_series.iloc[idx])
        entry = {}
        # Include Fiscal Year if present in source
        if 'Fiscal Year' in df.columns:
            entry['Fiscal Year'] = to_native(fy)
        entry[indicator_name] = score
        der_data.append(entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to file
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()