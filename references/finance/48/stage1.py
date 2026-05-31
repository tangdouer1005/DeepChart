#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,ROA(Avg),CFO,Net Income,Long Term Debt,Avg Total Assets,Leverage,Current Ratio,Current Assets,Current Liabilities,Shares,Gross Margin,Revenue,Cost of Revenue,Asset Turnover (for F-score),1_ROA>0,2_CFO>0,3_dROA>0,4_CFO>NI,5_dLev<0,6_dCurrent>0,7_NoDilute,8_dMargin>0,9_dTurnover>0
2017,0.077082434182132,6726000000,2679000000,6573000000.0,34755000000.0,0.1891238670694864,0.9898256644755644,17317000000,17495000000,440937000,0.1328657236969579,129025000000,111882000000,3.712415479787081,1,1,1,1,0,1,1,0,1
2018,0.0812159062933257,5774000000,3134000000,6487000000.0,38588500000.0,0.16810707853376,1.0182174043962662,20289000000,19926000000,441834000,0.130135051138611,141576000000,123152000000,3.66886507638286,1,1,1,1,1,1,0,0,0
2019,0.0848660558970196,6356000000,3659000000,5124000000.0,43115000000.0,0.1188449495535196,1.0106726341610364,23485000000,23237000000,442923000,0.1297747915889013,152703000000,132886000000,3.5417604082106,1,1,1,1,1,0,0,0,0
2020,0.0792820634731962,8861000000,4002000000,7514000000.0,50478000000.0,0.1488569277705138,1.1318628240218966,28120000000,24844000000,443901000,0.1308579344091244,166761000000,144939000000,3.30363722809937,1,1,0,1,0,1,0,1,0
2021,0.0872117327388002,8958000000,5007000000,6692000000.0,57412000000.0,0.116560997700829,1.0021738392038313,29505000000,29441000000,444346000,0.1288476948282285,195929000000,170684000000,3.412683759492789,1,1,1,1,1,0,0,0,1
2022,0.0946902798256558,7392000000,5844000000,6484000000.0,61717000000.0,0.105060194111833,1.0218138633664604,32696000000,31998000000,444757000,0.1214871736122738,226954000000,199382000000,3.677333635789167,1,1,1,1,1,1,0,0,1
2023,0.0945028537098227,11068000000,6292000000,5377000000.0,66580000000.0,0.0807599879843797,1.0683679242473871,35879000000,33583000000,444452000,0.1225968880267448,242290000000,212586000000,3.63908080504656,1,1,0,1,1,1,1,1,0
2024,0.1061336214658743,11339000000,7367000000,5794000000.0,69412500000.0,0.0834719971186745,0.965655312429506,34246000000,35464000000,444759000,0.1261333134213391,254453000000,222358000000,3.665809472357284,1,1,1,1,0,0,0,1,1
"""

def to_python_native_records(df):
    # Replace NaN with None, convert numpy scalars to Python scalars
    df_clean = df.where(pd.notnull(df), None)
    df_converted = df_clean.applymap(lambda x: x.item() if hasattr(x, "item") else x)
    return df_converted.to_dict(orient="records")

def compute_piotroski_fscore(df):
    """
    Compute Piotroski F-Score for each row in DataFrame.
    Uses columns:
      - 'ROA(Avg)' for ROA
      - 'CFO' for operating cash flow
      - 'Net Income' for net income
      - 'Leverage' for leverage (long-term debt ratio)
      - 'Current Ratio' for current ratio
      - 'Shares' for share count (dilution)
      - 'Gross Margin' for gross margin
      - 'Asset Turnover (for F-score)' for asset turnover
    """
    scores = []
    prev = None  # store previous row as dict
    for idx, row in df.iterrows():
        score_components = {}

        # 1. ROA > 0
        roa = row.get("ROA(Avg)")
        comp1 = 1 if (roa is not None and roa > 0) else 0
        score_components['ROA>0'] = comp1

        # 2. CFO > 0
        cfo = row.get("CFO")
        comp2 = 1 if (cfo is not None and cfo > 0) else 0
        score_components['CFO>0'] = comp2

        # 3. ΔROA > 0 (compare to previous fiscal year)
        if prev is None:
            comp3 = 1  # convention: first available year assume positive (matches many datasets)
        else:
            prev_roa = prev.get("ROA(Avg)")
            comp3 = 1 if (roa is not None and prev_roa is not None and (roa - prev_roa) > 0) else 0
        score_components['dROA>0'] = comp3

        # 4. Accruals: CFO > Net Income
        ni = row.get("Net Income")
        comp4 = 1 if (cfo is not None and ni is not None and cfo > ni) else 0
        score_components['CFO>NI'] = comp4

        # 5. ΔLeverage < 0 (leverage decreased vs prior year)
        lev = row.get("Leverage")
        if prev is None:
            comp5 = 1  # assume favorable for the first year by convention
        else:
            prev_lev = prev.get("Leverage")
            comp5 = 1 if (lev is not None and prev_lev is not None and (lev - prev_lev) < 0) else 0
        score_components['dLeverage<0'] = comp5

        # 6. ΔCurrent Ratio > 0
        cur = row.get("Current Ratio")
        if prev is None:
            comp6 = 1
        else:
            prev_cur = prev.get("Current Ratio")
            comp6 = 1 if (cur is not None and prev_cur is not None and (cur - prev_cur) > 0) else 0
        score_components['dCurrentRatio>0'] = comp6

        # 7. No Dilution: shares did not increase (current <= previous)
        shares = row.get("Shares")
        if prev is None:
            comp7 = 1
        else:
            prev_shares = prev.get("Shares")
            comp7 = 1 if (shares is not None and prev_shares is not None and shares <= prev_shares) else 0
        score_components['NoDilution'] = comp7

        # 8. ΔGross Margin > 0
        gm = row.get("Gross Margin")
        if prev is None:
            comp8 = 1
        else:
            prev_gm = prev.get("Gross Margin")
            comp8 = 1 if (gm is not None and prev_gm is not None and (gm - prev_gm) > 0) else 0
        score_components['dGrossMargin>0'] = comp8

        # 9. ΔAsset Turnover > 0
        at = row.get("Asset Turnover (for F-score)")
        if prev is None:
            comp9 = 1
        else:
            prev_at = prev.get("Asset Turnover (for F-score)")
            comp9 = 1 if (at is not None and prev_at is not None and (at - prev_at) > 0) else 0
        score_components['dAssetTurnover>0'] = comp9

        total_score = sum(score_components.values())

        # Build result dict for this fiscal year
        result = {
            "Fiscal Year": int(row["Fiscal Year"]) if not pd.isnull(row["Fiscal Year"]) else None,
            "皮奥特罗斯基 F-Score (Piotroski F-Score)": int(total_score)
        }

        scores.append(result)
        prev = row.to_dict()

    return scores

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV into DataFrame
    df = pd.read_csv(io.StringIO(CSV_DATA), dtype=float, keep_default_na=True)
    # Fiscal Year and Shares should be integers where possible; keep Fiscal Year as int
    # Re-read Fiscal Year and Shares columns separately to preserve their integer nature
    df_meta = pd.read_csv(io.StringIO(CSV_DATA), usecols=["Fiscal Year", "Shares"])
    df["Fiscal Year"] = df_meta["Fiscal Year"].astype(int)
    # Shares might be large int; keep as int
    try:
        df["Shares"] = df_meta["Shares"].astype(int)
    except Exception:
        df["Shares"] = df_meta["Shares"]

    # Prepare scr_data as list of records with native Python types
    scr_records = to_python_native_records(df)

    # Compute derived Piotroski F-Score
    der_records = compute_piotroski_fscore(df)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()