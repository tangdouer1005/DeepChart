#!/usr/bin/env python3
import sys
import io
import json
import math
import pandas as pd

CSV_DATA = """Fiscal Year,Net Income,Pretax Income,Operating Income,Revenue,Avg Total Assets,Avg Total Equity,Tax Burden,Interest Burden,Operating Margin,Asset Turnover,Equity Multiplier,RESULT_DuPont_ROE
2016,-47426000,64279000,114923000,6667216000,11727951000.0,4489026000.0,-0.7378148384386813,0.559322328863674,0.0172370296687552,0.5684894147323774,2.6125825513151404,-0.0105648753203924
2017,323000000,179000000,218000000,8391984000,15173921500.0,6251498000.0,1.8044692737430168,0.8211009174311926,0.0259771705951774,0.5530530785993588,2.4272456777559555,0.0516676163057238
2018,127478000,202108000,235768000,10480012000,19297362500.0,8446245000.0,0.6307419795356938,0.8572325336771742,0.0224969208050525,0.5430800193549766,2.2847268223926727,0.015092860791985
2019,1110000000,983000000,535000000,13282000000,25873401000.0,12498681500.0,1.1291963377416072,1.8373831775700933,0.0402800783014606,0.5133457329401728,2.0700904331388874,0.0888093676120957
2020,126000000,706000000,202000000,17098000000,42931500000.0,24745000000.0,0.178470254957507,3.495049504950495,0.0118142472803836,0.3982623481592769,1.734956556880178,0.005091937765205
2021,4072000000,2561000000,-1715000000,21252000000,60713500000.0,37689000000.0,1.590003904724717,-1.4932944606413994,-0.0806982872200263,0.3500374710731551,1.6109076918994931,0.1080421343097455
2022,1444000000,1532000000,-663000000,26492000000,80755000000.0,49812000000.0,0.9425587467362924,-2.310708898944193,-0.0250264230711158,0.3280539904649867,1.6211956958162692,0.0289889986348671
2023,208000000,660000000,2925000000,31352000000,97029000000.0,58245000000.0,0.3151515151515151,0.2256410256410256,0.0932954835417198,0.3231198919910542,1.665876899304661,0.0035711219847197
2024,4136000000,4950000000,5011000000,34857000000,99336000000.0,59002500000.0,0.8355555555555556,0.9878267810816204,0.1437587858966635,0.3508999758395748,1.6835896784034574,0.0700987246303122
"""

INDICATOR_NAME = "净资产收益率-杜邦分析 (Return on Equity - DuPont Analysis, ROE)"

def safe_div(numer, denom):
    try:
        if denom is None:
            return None
        # treat NaN as None
        if denom == 0:
            return None
        # use math.isnan if float
        if isinstance(denom, float) and math.isnan(denom):
            return None
        if numer is None:
            return None
        if isinstance(numer, float) and math.isnan(numer):
            return None
        return numer / denom
    except Exception:
        return None

def compute_dupont_row(row):
    """
    Computes ROE using DuPont five-factor decomposition:
    ROE = (Net Income / Pretax Income) *
          (Pretax Income / EBIT) *
          (EBIT / Revenue) *
          (Revenue / Avg Total Assets) *
          (Avg Total Assets / Avg Total Equity)
    Where EBIT is represented by Operating Income column.
    """
    net_income = row.get("Net Income")
    pretax_income = row.get("Pretax Income")
    ebit = row.get("Operating Income")
    revenue = row.get("Revenue")
    avg_total_assets = row.get("Avg Total Assets")
    avg_total_equity = row.get("Avg Total Equity")

    # compute each component safely
    tax_burden = safe_div(net_income, pretax_income)            # 净利润 / 税前利润
    interest_burden = safe_div(pretax_income, ebit)            # 税前利润 / 息税前利润(EBIT)
    operating_margin = safe_div(ebit, revenue)                # EBIT / Revenue
    asset_turnover = safe_div(revenue, avg_total_assets)      # Revenue / Avg Total Assets
    equity_multiplier = safe_div(avg_total_assets, avg_total_equity)  # Avg Total Assets / Avg Total Equity

    components = [tax_burden, interest_burden, operating_margin, asset_turnover, equity_multiplier]

    # if any component is None, we cannot compute a valid ROE via the decomposition
    if any(c is None for c in components):
        return None

    # multiply components to get ROE
    roe = 1.0
    for c in components:
        roe *= c

    return roe

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)

    out_path = sys.argv[1]

    # Load CSV data from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: convert DataFrame rows to list of dicts, with NaN -> None
    df_scr = df.where(pd.notnull(df), None)
    scr_data = df_scr.to_dict(orient="records")

    # Prepare der_data by computing ROE via DuPont decomposition for each row
    der_data = []
    for idx, row in df.iterrows():
        row_dict = row.to_dict()
        roe_value = compute_dupont_row(row_dict)
        # If roe_value is a float, keep it as Python float; if None, leave as None (will become null in JSON)
        der_entry = {"Fiscal Year": int(row_dict["Fiscal Year"]) if not pd.isnull(row_dict["Fiscal Year"]) else None,
                     INDICATOR_NAME: roe_value}
        der_data.append(der_entry)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to specified file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()