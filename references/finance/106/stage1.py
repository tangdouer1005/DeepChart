#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Avg Total Equity,Dividends,ROE(Avg),Retention Ratio
2016,7009000000,7819000000.0,3031000000,0.8964061900498785,0.5675559994293051
2017,7957000000,5324500000.0,3404000000,1.4944126209033712,0.5722005781073269
2018,8630000000,2893500000.0,4212000000,2.982547088301365,0.5119351100811125
2019,11121000000,-212000000.0,4704000000,-52.45754716981132,0.5770164553547343
2020,11242000000,-2497000000.0,5958000000,-4.502202643171806,0.4700231275573742
2021,12866000000,91500000.0,6451000000,140.6120218579235,0.4986009637805068
2022,16433000000,801500000.0,6985000000,20.50280723643169,0.5749406681677114
2023,17105000000,-67000000.0,7789000000,-255.29850746268656,0.5446360713241742
2024,15143000000,1303000000.0,8383000000,11.6216423637759,0.4464108829161989
"""

INDICATOR_NAME = "可持续增长率 (Sustainable Growth Rate, SGR)"

def to_native(obj):
    """
    Convert numpy types to native Python types for JSON serialization.
    """
    if isinstance(obj, dict):
        return {to_native(k): to_native(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_native(x) for x in obj]
    if isinstance(obj, (np.integer, )):
        return int(obj)
    if isinstance(obj, (np.floating, )):
        # Convert NaN to None for JSON
        if np.isnan(obj):
            return None
        return float(obj)
    if obj is pd.NaT:
        return None
    return obj

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns parsed as numeric types
    numeric_cols = ["Net Income", "Avg Total Equity", "Dividends"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Prepare scr_data: original data as list of dicts with native types
    scr_records = df.to_dict(orient="records")
    scr_records = [to_native(rec) for rec in scr_records]

    der_records = []
    for idx, row in df.iterrows():
        fiscal_year = None
        if "Fiscal Year" in df.columns:
            fiscal_year = int(row["Fiscal Year"]) if not pd.isna(row["Fiscal Year"]) else None

        net_income = row.get("Net Income", None)
        dividends = row.get("Dividends", None)
        equity = row.get("Avg Total Equity", None)

        # Calculate retention ratio: 1 - (Dividends / Net Income)
        retention = None
        try:
            if pd.notna(net_income) and net_income != 0:
                retention = 1.0 - (dividends / net_income)
            else:
                retention = None
        except Exception:
            retention = None

        # Calculate ROE: Net Income / Avg Total Equity
        roe_calc = None
        try:
            if pd.notna(equity) and equity != 0 and pd.notna(net_income):
                roe_calc = net_income / equity
            else:
                roe_calc = None
        except Exception:
            roe_calc = None

        # Calculate SGR = ROE * retention
        sgr = None
        if (roe_calc is not None) and (retention is not None):
            try:
                sgr = roe_calc * retention
            except Exception:
                sgr = None

        record = {}
        if fiscal_year is not None:
            record["Fiscal Year"] = fiscal_year
        # Use the exact indicator name requested
        record[INDICATOR_NAME] = to_native(sgr)
        der_records.append(record)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()