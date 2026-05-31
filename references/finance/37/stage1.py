#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,ROA(Avg),CFO,Net Income,Long Term Debt,Avg Total Assets,Leverage,Current Ratio,Current Assets,Current Liabilities,Shares,Gross Margin,Revenue,Cost of Revenue,Asset Turnover (for F-score),1_ROA>0,2_CFO>0,3_dROA>0,4_CFO>NI,5_dLev<0,6_dCurrent>0,7_NoDilute,8_dMargin>0,9_dTurnover>0
2016,0.0320083159521832,17203000000,2371000000,7694000000,74074500000.0,0.1038684027566841,1.044846631367537,45781000000,43816000000,9680000000,0.103083382970431,135987000000,121969000000,1.8358139440698216,1,1,1,1,1,0,0,1,1
2017,0.0282517977569954,18365000000,3033000000,24743000000,107356000000.0,0.2304761727337084,1.039977195376881,60197000000,57883000000,9860000000,0.3706835482891615,177866000000,111934000000,1.6567867655277768,1,1,0,1,0,0,0,1,0
2018,0.0685336000381006,30723000000,10073000000,23495000000,146979000000.0,0.1598527680825152,1.098112324721089,75101000000,68391000000,10000000000,0.4024741612885219,232887000000,139156000000,1.5844916620741738,1,1,1,1,1,1,0,1,0
2019,0.0597479736836677,38514000000,11588000000,23414000000,193948000000.0,0.1207230804133066,1.0970482394205805,96334000000,87812000000,10080000000,0.4099001147860061,280522000000,165536000000,1.4463773795037844,1,1,0,1,1,0,0,1,0
2020,0.0780721868520595,66064000000,21331000000,31816000000,273221500000.0,0.1164476441275668,1.0502274795268425,132733000000,126385000000,10200000000,0.3956779186870571,386064000000,233307000000,1.4130073950988484,1,1,1,1,1,0,0,0,0
2021,0.0899609568800017,46327000000,33364000000,48744000000,370872000000.0,0.1314307901378373,1.1357597739445826,161580000000,142266000000,10300000000,0.420325144416396,469822000000,272344000000,1.2668036411484285,1,1,1,1,0,1,0,1,0
2022,-0.0061637817812921,46752000000,-2722000000,67150000000,441612000000.0,0.1520565564341548,0.9446435811136924,146791000000,155393000000,10189000000,0.4380533986532628,513983000000,288831000000,1.163879151834642,0,1,0,1,0,0,1,1,0
2023,0.0614318207745558,84946000000,30425000000,58314000000,495264500000.0,0.1177431453294148,1.0450772206625152,172351000000,164917000000,10492000000,0.4698208895500056,574785000000,304739000000,1.1605616796681368,1,1,1,1,1,1,0,1,0
2024,0.1027943661580848,115877000000,59248000000,52623000000,576374000000.0,0.0913000933421702,1.063734806137178,190867000000,179431000000,10721000000,0.4885439346415678,637959000000,326288000000,1.1068490251121668,1,1,1,1,1,1,0,1,0
"""

INDICATOR_NAME = "皮奥特罗斯基 F-Score (Piotroski F-Score)"

def to_python_value(v):
    # Convert numpy types to native python types for JSON serialization
    try:
        if pd.isna(v):
            return None
    except Exception:
        pass
    try:
        # numpy scalar has item()
        return v.item()
    except Exception:
        return v

def compute_piotroski_fscore(df):
    """
    Compute Piotroski F-Score for each row in df.
    Returns a list of dicts with Fiscal Year and computed score.
    """
    der = []
    # Iterate rows
    for idx in range(len(df)):
        row = df.iloc[idx]
        # Basic checks
        # 1. ROA > 0
        roa = row.get("ROA(Avg)", None)
        test1 = 1 if (pd.notnull(roa) and roa > 0) else 0

        # 2. CFO > 0
        cfo = row.get("CFO", None)
        test2 = 1 if (pd.notnull(cfo) and cfo > 0) else 0

        # 3. ΔROA > 0 (compare to prior year)
        if idx > 0:
            prev_roa = df.iloc[idx - 1].get("ROA(Avg)", None)
            test3 = 1 if (pd.notnull(roa) and pd.notnull(prev_roa) and (roa - prev_roa) > 0) else 0
        else:
            test3 = 0

        # 4. Accruals: CFO > Net Income
        net_income = row.get("Net Income", None)
        test4 = 1 if (pd.notnull(cfo) and pd.notnull(net_income) and (cfo > net_income)) else 0

        # 5. ΔLeverage < 0 (leverage decrease)
        lev = row.get("Leverage", None)
        if idx > 0:
            prev_lev = df.iloc[idx - 1].get("Leverage", None)
            test5 = 1 if (pd.notnull(lev) and pd.notnull(prev_lev) and (lev - prev_lev) < 0) else 0
        else:
            test5 = 0

        # 6. ΔCurrent Ratio > 0
        cur = row.get("Current Ratio", None)
        if idx > 0:
            prev_cur = df.iloc[idx - 1].get("Current Ratio", None)
            test6 = 1 if (pd.notnull(cur) and pd.notnull(prev_cur) and (cur - prev_cur) > 0) else 0
        else:
            test6 = 0

        # 7. No Dilution: shares not increased (current <= prior)
        shares = row.get("Shares", None)
        if idx > 0:
            prev_shares = df.iloc[idx - 1].get("Shares", None)
            test7 = 1 if (pd.notnull(shares) and pd.notnull(prev_shares) and (shares <= prev_shares)) else 0
        else:
            test7 = 0

        # 8. ΔGross Margin > 0
        gm = row.get("Gross Margin", None)
        if idx > 0:
            prev_gm = df.iloc[idx - 1].get("Gross Margin", None)
            test8 = 1 if (pd.notnull(gm) and pd.notnull(prev_gm) and (gm - prev_gm) > 0) else 0
        else:
            test8 = 0

        # 9. ΔAsset Turnover > 0
        at = row.get("Asset Turnover (for F-score)", None)
        if idx > 0:
            prev_at = df.iloc[idx - 1].get("Asset Turnover (for F-score)", None)
            test9 = 1 if (pd.notnull(at) and pd.notnull(prev_at) and (at - prev_at) > 0) else 0
        else:
            test9 = 0

        score = int(test1 + test2 + test3 + test4 + test5 + test6 + test7 + test8 + test9)

        der_row = {
            "Fiscal Year": to_python_value(row.get("Fiscal Year")),
            INDICATOR_NAME: score
        }
        der.append(der_row)
    return der

def dataframe_to_serializable_records(df):
    recs = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_value(row[col])
        recs.append(rec)
    return recs

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data (raw)
    scr_data = dataframe_to_serializable_records(df)

    # Compute derived Piotroski F-Score
    der_data = compute_piotroski_fscore(df)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()