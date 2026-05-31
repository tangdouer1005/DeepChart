#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Pretax Income,Operating Income,Revenue,Avg Total Assets,Avg Total Equity,Tax Burden,Interest Burden,Operating Margin,Asset Turnover,Equity Multiplier,RESULT_DuPont_ROE
2016,1400000000,1413000000,3249000000,20853000000,49506000000.0,20874500000.0,0.9907997169143666,0.4349030470914127,0.1558049201553733,0.4212216701005938,2.371601715011138,0.0670674746700519
2017,477000000,2231000000,1972000000,27390000000,65630500000.0,25717500000.0,0.2138054683998207,1.131338742393509,0.0719970792259949,0.4173364518021347,2.5519782249441043,0.0185476815398075
2018,2368000000,2873000000,3844000000,30578000000,71711500000.0,30710500000.0,0.8242255482074486,0.7473985431841832,0.1257112957027928,0.4264030176470998,2.3350808355448462,0.0771071783266309
2019,3687000000,4077000000,4591000000,31904000000,67530000000.0,30806000000.0,0.9043414275202356,0.8880418209540405,0.1439004513540621,0.4724418776839923,2.1921054340063626,0.1196844770499253
2020,4495000000,4968000000,5291000000,34608000000,70217500000.0,31936000000.0,0.9047906602254429,0.938952938952939,0.1528837263060564,0.4928685868907324,2.198694263527054,0.140750250501002
2021,7071000000,8211000000,9200000000,43075000000,73872000000.0,34293000000.0,0.8611618560467665,0.8925,0.2135809634358676,0.583103205544726,2.1541422447729857,0.2061936838421835
2022,6933000000,8306000000,8362000000,43653000000,74817000000.0,36244000000.0,0.8346978088129063,0.9933030375508252,0.1915561358898586,0.5834636513091944,2.0642589118198877,0.1912868336828164
2023,5723000000,6664000000,6435000000,40109000000,73826000000.0,37644500000.0,0.8587935174069627,1.0355866355866357,0.1604378069759904,0.5432909814970336,1.9611364209911144,0.1520275206205421
2024,13402000000,7013000000,6825000000,41950000000,77314000000.0,43133500000.0,1.91102238699558,1.0275457875457876,0.1626936829558999,0.5425925446878961,1.792435114238353,0.3107097731461625
"""

INDICATOR_NAME = "净资产收益率-杜邦分析 (Return on Equity - DuPont Analysis, ROE)"

def to_python_value(v):
    """Convert numpy/pandas scalars to native Python types for JSON serialization."""
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    # For plain python numeric types or strings
    return v

def compute_dupont_roe(row):
    """
    Compute ROE using the 5-factor DuPont decomposition:
    ROE = (Net Income / Pretax Income) *
          (Pretax Income / EBIT) *
          (EBIT / Revenue) *
          (Revenue / Total Assets) *
          (Total Assets / Equity)
    Use None when any denominator is zero or missing.
    """
    net = row.get("Net Income")
    pretax = row.get("Pretax Income")
    ebit = row.get("Operating Income")  # treated as EBIT
    revenue = row.get("Revenue")
    assets = row.get("Avg Total Assets")
    equity = row.get("Avg Total Equity")

    # Ensure we operate with floats/None
    try:
        net_f = float(net) if net is not None else None
    except Exception:
        net_f = None
    try:
        pretax_f = float(pretax) if pretax is not None else None
    except Exception:
        pretax_f = None
    try:
        ebit_f = float(ebit) if ebit is not None else None
    except Exception:
        ebit_f = None
    try:
        rev_f = float(revenue) if revenue is not None else None
    except Exception:
        rev_f = None
    try:
        assets_f = float(assets) if assets is not None else None
    except Exception:
        assets_f = None
    try:
        equity_f = float(equity) if equity is not None else None
    except Exception:
        equity_f = None

    # compute each factor with safety for division by zero / missing data
    def safe_div(n, d):
        if n is None or d is None:
            return None
        try:
            if d == 0:
                return None
            return n / d
        except Exception:
            return None

    f1 = safe_div(net_f, pretax_f)           # Net Income / Pretax Income (tax burden)
    f2 = safe_div(pretax_f, ebit_f)          # Pretax Income / EBIT (interest burden)
    f3 = safe_div(ebit_f, rev_f)             # EBIT / Revenue (operating margin)
    f4 = safe_div(rev_f, assets_f)           # Revenue / Total Assets (asset turnover)
    f5 = safe_div(assets_f, equity_f)        # Total Assets / Equity (equity multiplier)

    # If any factor is None, result is None
    for f in (f1, f2, f3, f4, f5):
        if f is None:
            return None

    roe = f1 * f2 * f3 * f4 * f5
    return roe

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV into pandas DataFrame
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: list of dicts with native python types
    scr_records = []
    for _, r in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_value(r[col])
        scr_records.append(rec)

    # Prepare der_data: compute the DuPont ROE per row
    der_records = []
    for _, r in df.iterrows():
        row = {col: (None if pd.isna(r[col]) else r[col]) for col in df.columns}
        roe_value = compute_dupont_roe(row)
        # Convert roe_value to Python float if not None
        roe_python = None if roe_value is None else float(roe_value)
        rec = {}
        # include Fiscal Year if present
        if "Fiscal Year" in df.columns:
            fy = r["Fiscal Year"]
            rec["Fiscal Year"] = to_python_value(fy)
        rec[INDICATOR_NAME] = roe_python
        der_records.append(rec)

    out_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()