#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Net Income,Pretax Income,Operating Income,Revenue,Avg Total Assets,Avg Total Equity,Tax Burden,Interest Burden,Operating Margin,Asset Turnover,Equity Multiplier,RESULT_DuPont_ROE
2016,6527000000,8136000000,8657000000,41863000000,88633000000.0,24308000000.0,0.8022369714847591,0.939817488737438,0.2067935886104674,0.4723184366996491,3.6462481487576106,0.2685124238933685
2017,1248000000,6890000000,7755000000,36212000000,87583000000.0,20067000000.0,0.1811320754716981,0.8884590586718246,0.2141555285540704,0.4134592329561672,4.364528828424777,0.0621916579458812
2018,6434000000,8225000000,9152000000,34300000000,85556000000.0,17026500000.0,0.7822492401215806,0.8987106643356644,0.2668221574344023,0.4009070082752817,5.0248729921005495,0.3778815376031481
2019,8920000000,10786000000,10086000000,37266000000,84798500000.0,17981000000.0,0.8269979603189319,1.0694031330557208,0.2706488488166156,0.4394653207309091,4.716005783882988,0.4960791947055224
2020,7747000000,9749000000,8997000000,33014000000,86838500000.0,19140000000.0,0.7946456046774029,1.0835834166944538,0.2725207487732477,0.3801769952267715,4.537016718913271,0.4047544409613375
2021,9771000000,12425000000,10308000000,38655000000,90825000000.0,21149000000.0,0.7863983903420523,1.2053744664338375,0.2666666666666666,0.4255986787778695,4.294529292165114,0.4620076599366399
2022,9542000000,11686000000,10909000000,43004000000,93558500000.0,23552000000.0,0.8165326031148382,1.0712255935466128,0.2536740768300623,0.4596482414745854,3.972422724184783,0.4051460597826087
2023,10714000000,12952000000,11311000000,45754000000,95233000000.0,25023000000.0,0.827208153180976,1.1450800106091414,0.2472133583948944,0.4804427036846471,3.805818646844903,0.4281660871997762
2024,10631000000,13086000000,9992000000,47061000000,99126000000.0,25398500000.0,0.8123949258749809,1.3096477181745396,0.2123201801916661,0.4747593971309243,3.90282890721893,0.4185680256708072
"""

INDICATOR_NAME = "净资产收益率-杜邦分析 (Return on Equity - DuPont Analysis, ROE)"

def safe_div(numerator, denominator):
    try:
        if denominator is None:
            return None
        if denominator == 0:
            return None
        return numerator / denominator
    except Exception:
        return None

def to_python_native(val):
    # Convert pandas/numpy scalars to native Python types for JSON serialization
    if pd.isna(val):
        return None
    # numpy types and pandas scalars have .item()
    if hasattr(val, "item"):
        try:
            return val.item()
        except Exception:
            pass
    return val

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    scr_data = []
    der_data = []

    for _, row in df.iterrows():
        # Build scr_data record with original fields converted to native types
        scr_record = {}
        for col in df.columns:
            scr_record[col] = to_python_native(row[col])
        scr_data.append(scr_record)

        # Extract required raw inputs for DuPont calculation
        net_income = row.get("Net Income")
        pretax_income = row.get("Pretax Income")  # 税前利润 (EBT)
        ebit = row.get("Operating Income")        # 息税前利润 (EBIT) - using Operating Income as EBIT
        revenue = row.get("Revenue")
        total_assets = row.get("Avg Total Assets")  # use average total assets as '总资产'
        equity = row.get("Avg Total Equity")        # use average total equity as '股东权益'

        # Calculate five components per the reference formula
        tax_burden = safe_div(net_income, pretax_income)           # 净利润 / 税前利润
        interest_burden = safe_div(pretax_income, ebit)            # 税前利润 / 息税前利润
        operating_margin = safe_div(ebit, revenue)                 # 息税前利润 / 销售收入
        asset_turnover = safe_div(revenue, total_assets)           # 销售收入 / 总资产
        equity_multiplier = safe_div(total_assets, equity)        # 总资产 / 股东权益

        # Compute ROE as product of the five components, only if none are None
        components = [tax_burden, interest_burden, operating_margin, asset_turnover, equity_multiplier]
        if all(c is not None for c in components):
            roe = 1.0
            for c in components:
                roe *= c
        else:
            roe = None

        der_record = {
            "Fiscal Year": to_python_native(row.get("Fiscal Year")),
            INDICATOR_NAME: to_python_native(roe)
        }
        der_data.append(der_record)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()