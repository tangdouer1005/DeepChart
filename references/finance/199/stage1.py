#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,ROA(Avg),CFO,Net Income,Long Term Debt,Avg Total Assets,Leverage,Current Ratio,Current Assets,Current Liabilities,Shares,Gross Margin,Revenue,Cost of Revenue,Asset Turnover (for F-score),1_ROA>0,2_CFO>0,3_dROA>0,4_CFO>NI,5_dLev<0,6_dCurrent>0,7_NoDilute,8_dMargin>0,9_dTurnover>0
2016,0.0842748601229479,1175000000,614000000,87000000.0,7285684000.0,0.0119412261086261,2.4827727645611155,6053000000,2438000000,22760000000,0.5610778443113772,5010000000,2199000000,0.6876499172898523,1,1,0,1,1,0,0,1,1
2017,0.1935971181221312,1672000000,1666000000,1983000000.0,8605500000.0,0.2304340247516123,4.692688290269379,8536000000,1819000000,25960000000,0.5879884225759768,6910000000,2847000000,0.8029748416710244,1,1,1,1,0,1,0,1,1
2018,0.2890617588464093,3502000000,3047000000,1985000000.0,10541000000.0,0.188312304335452,8.026886383347788,9255000000,1153000000,25280000000,0.5993411570928556,9714000000,3892000000,0.9215444454985297,1,1,1,1,1,1,1,1,1
2019,0.337586108506909,3743000000,4141000000,1988000000.0,12266500000.0,0.1620674193942852,7.943566591422122,10557000000,1329000000,25000000000,0.6120689655172413,11716000000,4545000000,0.955121672848816,1,1,1,0,1,0,1,1,1
2020,0.1827033031659424,4761000000,2796000000,1991000000.0,15303500000.0,0.1301009572973502,7.673766816143497,13690000000,1784000000,24720000000,0.619893753434695,10918000000,4150000000,0.713431567941974,1,1,0,1,1,0,1,1,0
2021,0.1879148050145317,5822000000,4332000000,5964000000.0,23053000000.0,0.2587081941612805,4.090445859872611,16055000000,3925000000,25120000000,0.623448275862069,16675000000,6279000000,0.7233331887389928,1,1,1,1,0,0,0,1,1
2022,0.2672586258872537,9108000000,9752000000,10946000000.0,36489000000.0,0.2999808161363698,6.650288350634371,28829000000,4335000000,25350000000,0.6492903321691313,26914000000,9439000000,0.7375921510592234,1,1,1,0,0,1,0,1,1
2023,0.1023322283264416,5641000000,4368000000,9703000000.0,42684500000.0,0.2273190502407197,3.515617857687033,23073000000,6563000000,25070000000,0.5692889449099132,26974000000,11618000000,0.6319389942484976,1,1,0,1,1,0,1,0,0
2024,0.5567299597792535,28090000000,29760000000,8459000000.0,53455000000.0,0.1582452530165559,4.171291505973097,44345000000,10631000000,24940000000,0.7271757329043695,60922000000,16621000000,1.1396875876905808,1,1,1,0,1,1,1,1,1
"""

def load_data(csv_text: str) -> pd.DataFrame:
    df = pd.read_csv(io.StringIO(csv_text))
    return df

def to_native(obj):
    # Convert numpy types to native Python types for JSON serialization
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        # convert nan to None
        if np.isnan(obj):
            return None
        return float(obj)
    if isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    return obj

def dataframe_records_native(df: pd.DataFrame):
    # Use pandas to_json then json.loads to get native types reliably
    # This preserves numeric types as native Python types.
    text = df.to_json(orient='records')
    return json.loads(text)

def compute_piotroski_fscore(df: pd.DataFrame):
    der = []
    n = len(df)
    for i in range(n):
        row = df.iloc[i]
        # Extract current values (ensure numeric)
        roa = row.get("ROA(Avg)")
        cfo = row.get("CFO")
        ni = row.get("Net Income")
        leverage = row.get("Leverage")
        current_ratio = row.get("Current Ratio")
        shares = row.get("Shares")
        gross_margin = row.get("Gross Margin")
        asset_turn = row.get("Asset Turnover (for F-score)")

        # Previous year values if available
        if i > 0:
            prow = df.iloc[i-1]
            prev_roa = prow.get("ROA(Avg)")
            prev_leverage = prow.get("Leverage")
            prev_current = prow.get("Current Ratio")
            prev_shares = prow.get("Shares")
            prev_gross_margin = prow.get("Gross Margin")
            prev_asset_turn = prow.get("Asset Turnover (for F-score)")
        else:
            prev_roa = prev_leverage = prev_current = prev_shares = prev_gross_margin = prev_asset_turn = None

        # Criterion 1: ROA > 0
        c1 = 1 if (pd.notnull(roa) and roa > 0) else 0

        # Criterion 2: CFO > 0
        c2 = 1 if (pd.notnull(cfo) and cfo > 0) else 0

        # Criterion 3: dROA > 0 (current ROA > prior ROA)
        if prev_roa is None or pd.isnull(prev_roa) or pd.isnull(roa):
            c3 = 0
        else:
            c3 = 1 if (roa - prev_roa) > 0 else 0

        # Criterion 4: Accruals: CFO > Net Income
        if pd.notnull(cfo) and pd.notnull(ni):
            c4 = 1 if cfo > ni else 0
        else:
            c4 = 0

        # Criterion 5: dLeverage < 0 (leverage decreased)
        if prev_leverage is None or pd.isnull(prev_leverage) or pd.isnull(leverage):
            c5 = 0
        else:
            c5 = 1 if (leverage - prev_leverage) < 0 else 0

        # Criterion 6: dCurrent > 0 (current ratio increased)
        if prev_current is None or pd.isnull(prev_current) or pd.isnull(current_ratio):
            c6 = 0
        else:
            c6 = 1 if (current_ratio - prev_current) > 0 else 0

        # Criterion 7: No Dilution (shares did not increase)
        if prev_shares is None or pd.isnull(prev_shares) or pd.isnull(shares):
            c7 = 0
        else:
            # No dilution if current shares <= prior shares
            c7 = 1 if shares <= prev_shares else 0

        # Criterion 8: dGross Margin > 0
        if prev_gross_margin is None or pd.isnull(prev_gross_margin) or pd.isnull(gross_margin):
            c8 = 0
        else:
            c8 = 1 if (gross_margin - prev_gross_margin) > 0 else 0

        # Criterion 9: dAsset Turnover > 0
        if prev_asset_turn is None or pd.isnull(prev_asset_turn) or pd.isnull(asset_turn):
            c9 = 0
        else:
            c9 = 1 if (asset_turn - prev_asset_turn) > 0 else 0

        score = int(c1 + c2 + c3 + c4 + c5 + c6 + c7 + c8 + c9)

        der_entry = {
            "Fiscal Year": to_native(row.get("Fiscal Year")),
            "皮奥特罗斯基 F-Score (Piotroski F-Score)": score
        }
        der.append(der_entry)
    return der

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = load_data(CSV_DATA)

    # Prepare scr_data: original data as native types
    scr_data = dataframe_records_native(df)

    # Compute derived Piotroski F-Score
    der_data = compute_piotroski_fscore(df)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()