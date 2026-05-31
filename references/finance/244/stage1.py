#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Pretax Income,Operating Income,Revenue,Avg Total Assets,Avg Total Equity,Tax Burden,Interest Burden,Operating Margin,Asset Turnover,Equity Multiplier,RESULT_DuPont_ROE
2016,-674914000,-746348000,-667340000,7000132000.0,15366007500.0,2918307500.0,0.9042886160343432,1.1183924236521114,-0.0953324880159402,0.4555595850125675,5.265383274380784,-0.2312689803936014
2017,-1962000000,-2209000000,-1632000000,11759000000.0,25659724000.0,4495076500.0,0.8881846989588049,1.3535539215686274,-0.1387873118462454,0.4582668153406482,5.708406519889039,-0.4364775549426133
2018,-976000000,-1005000000,-388000000,21461268000.0,29197686000.0,4580121000.0,0.9711442786069652,2.5902061855670104,-0.0180790808818938,0.7350331803691567,6.3748721922412095,-0.2130948068839229
2019,-862000000,-665000000,-69000000,24578000000.0,32024500000.0,5770500000.0,1.2962406015037593,9.63768115942029,-0.0028073887216209,0.7674749020281347,5.549692401005112,-0.1493804696300147
2020,721000000,1154000000,1994000000,31536000000.0,43228500000.0,14421500000.0,0.6247833622183708,0.5787362086258776,0.0632293252156265,0.7295187202886985,2.99750372707416,0.0499947994314045
2021,5644000000,6343000000,6687000000,53823000000.0,57139500000.0,26207000000.0,0.8897997792842504,0.9485569014505756,0.1242405663006521,0.9419578400231012,2.1803144198115008,0.215362307780364
2022,12587000000,13719000000,13656000000,81462000000.0,72234500000.0,37446500000.0,0.917486697281143,1.0046133567662563,0.167636443986153,1.127743668191792,1.9290053810102408,0.3361328829129557
2023,14974000000,9973000000,8891000000,96773000000.0,94478000000.0,53669000000.0,1.5014539255991175,1.1216960971769203,0.0918747997891974,1.0242913694193356,1.7603830889340215,0.2790065028228586
2024,7130000000,8990000000,7076000000,97690000000.0,114344000000.0,67773500000.0,0.7931034482758621,1.2704918032786885,0.0724332070836318,0.8543517805918981,1.6871491069518323,0.1052033611957476
"""

INDICATOR_NAME = "净资产收益率-杜邦分析 (Return on Equity - DuPont Analysis, ROE)"

def safe_div(a, b):
    """Return a/b or None if b is zero or either is NaN/None."""
    try:
        if a is None or b is None:
            return None
        if isinstance(a, (float, int, np.floating, np.integer)) and np.isnan(a):
            return None
        if isinstance(b, (float, int, np.floating, np.integer)) and np.isnan(b):
            return None
        if abs(b) < 1e-15:
            return None
        return a / b
    except Exception:
        return None

def numpy_to_native(v):
    """Convert numpy scalar types to native Python types; keep None for missing."""
    if v is None:
        return None
    if isinstance(v, (np.generic,)):
        return v.item()
    # pandas may use numpy dtypes inside Python types; ensure standard numeric types
    if isinstance(v, (np.ndarray,)):
        return v.tolist()
    return v

def series_to_record(s: pd.Series):
    """Convert a pandas Series (row) to a JSON-serializable dict with native types."""
    rec = {}
    for k, v in s.items():
        if pd.isna(v):
            rec[k] = None
        else:
            # convert numpy types to native
            if isinstance(v, (np.generic,)):
                rec[k] = v.item()
            else:
                rec[k] = v
    return rec

def calculate_dupont_roe(row):
    """
    ROE = (NetIncome / PretaxIncome) *
          (PretaxIncome / OperatingIncome) *
          (OperatingIncome / Revenue) *
          (Revenue / AvgTotalAssets) *
          (AvgTotalAssets / AvgTotalEquity)
    Each intermediate division returns None if denominator is zero or invalid.
    If any factor is None -> overall result is None.
    """
    net_income = row.get("Net Income")
    pretax = row.get("Pretax Income")
    operating = row.get("Operating Income")
    revenue = row.get("Revenue")
    avg_assets = row.get("Avg Total Assets")
    avg_equity = row.get("Avg Total Equity")

    f1 = safe_div(net_income, pretax)
    f2 = safe_div(pretax, operating)
    f3 = safe_div(operating, revenue)
    f4 = safe_div(revenue, avg_assets)
    f5 = safe_div(avg_assets, avg_equity)

    factors = (f1, f2, f3, f4, f5)
    if any(f is None for f in factors):
        return None
    # Multiply factors
    roe = 1.0
    for f in factors:
        roe *= f
    return float(roe)

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows as list of dicts with native types
    scr_records = [series_to_record(df.iloc[i]) for i in range(len(df))]

    # Calculate der_data
    der_records = []
    for i in range(len(df)):
        row = df.iloc[i].to_dict()
        roe_value = calculate_dupont_roe(row)
        # convert roe_value to native float or None
        roe_native = numpy_to_native(roe_value)
        rec = {}
        # include Fiscal Year if exists
        if "Fiscal Year" in row:
            rec["Fiscal Year"] = numpy_to_native(row["Fiscal Year"])
        rec[INDICATOR_NAME] = roe_native
        der_records.append(rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()