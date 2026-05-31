#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Pretax Income,Operating Income,Revenue,Avg Total Assets,Avg Total Equity,Tax Burden,Interest Burden,Operating Margin,Asset Turnover,Equity Multiplier,RESULT_DuPont_ROE
2016,2021800000,2023900000,2858900000,18274100000,43371150000.0,21444750000.0,0.99896239932803,0.7079296232816817,0.1564454610623779,0.421342297817789,2.022460042667786,0.0942794856549971
2017,2225000000,2429000000,3267000000,20918000000,51288500000.0,23476150000.0,0.9160148209139564,0.7434955616773798,0.156181279281002,0.407849712898603,2.184706606492121,0.0947770396764375
2018,2938000000,3262000000,3872000000,24358000000,56450500000.0,26499500000.0,0.9006744328632741,0.8424586776859504,0.1589621479596026,0.4314930780063949,2.130247740523406,0.110870016415404
2019,3696000000,4070000000,4259000000,25542000000,57306500000.0,28630500000.0,0.9081081081081082,0.9556233857713078,0.1667449690705504,0.4457086019910481,2.001589214299436,0.1290931000157175
2020,6375000000,7227000000,7897000000,32218000000,63716500000.0,32091000000.0,0.8821087588210876,0.9151576548056224,0.2451114283940654,0.5056461042273195,1.9854943753700411,0.1986538281761241
2021,7725000000,8837000000,10318000000,39211000000,82087500000.0,37650000000.0,0.8741654407604391,0.8564644310912968,0.2631404452832113,0.4776732145576366,2.1802788844621515,0.2051792828685259
2022,6950000000,7663000000,8525000000,44915000000,96138500000.0,42385500000.0,0.9069555004567402,0.8988856304985338,0.1898029611488366,0.4671905636139528,2.268193132085265,0.1639711693857569
2023,5995000000,6298000000,6859000000,42857000000,97940000000.0,45356500000.0,0.95188948872658,0.9182096515527044,0.1600438668128893,0.437584235246069,2.1593376914003506,0.1321751016943547
2024,6335000000,6995000000,7662000000,42879000000,98023500000.0,48159500000.0,0.9056468906361688,0.9129470112242234,0.1786888686769747,0.4374359209781328,2.035392809310728,0.1315420633519866
"""

IND_NAME = "净资产收益率-杜邦分析 (Return on Equity - DuPont Analysis, ROE)"

def to_native(val):
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    return val

def safe_div(numer, denom):
    try:
        if denom is None:
            return None
        if denom == 0:
            return None
        return numer / denom
    except Exception:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: convert dataframe rows to native python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Calculate DuPont ROE per the provided formula:
    # ROE = (Net Income / Pretax Income) * (Pretax Income / EBIT) * (EBIT / Revenue) * (Revenue / Total Assets) * (Total Assets / Equity)
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = to_native(row.get("Fiscal Year"))
        net_income = to_native(row.get("Net Income"))
        pretax = to_native(row.get("Pretax Income"))
        ebit = to_native(row.get("Operating Income"))  # 息税前利润 (EBIT)
        revenue = to_native(row.get("Revenue"))
        total_assets = to_native(row.get("Avg Total Assets"))
        equity = to_native(row.get("Avg Total Equity"))

        # Compute each ratio safely
        tax_burden = safe_div(net_income, pretax)           # 净利润 / 税前利润
        pretax_to_ebit = safe_div(pretax, ebit)             # 税前利润 / 息税前利润
        ebit_margin = safe_div(ebit, revenue)               # 息税前利润 / 销售收入
        asset_turnover = safe_div(revenue, total_assets)    # 销售收入 / 总资产
        equity_multiplier = safe_div(total_assets, equity)  # 总资产 / 股东权益

        # If any component is None, the product will be None
        components = [tax_burden, pretax_to_ebit, ebit_margin, asset_turnover, equity_multiplier]
        if any(comp is None for comp in components):
            roe = None
        else:
            roe = float(tax_burden * pretax_to_ebit * ebit_margin * asset_turnover * equity_multiplier)

        der_rec = {"Fiscal Year": fiscal_year, IND_NAME: roe}
        der_records.append(der_rec)

    out_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON with ensure_ascii=False to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()