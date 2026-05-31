#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Working Capital,Total Assets,Retained Earnings,Operating Income,Market Value of Equity,Total Liabilities,Revenue,X1 (WC/TA),X2 (RE/TA),X3 (EBIT/TA),X4 (MVE/TL),X5 (S/TA)
2016,1133634000,13586610000,1128603000,379793000,2679800000,10906810000,8830669000,0.0834375903923053,0.0830672993484025,0.0279534777254959,0.2456997050466635,0.6499538148220932
2017,2203662000,19012742000,1731117000,838679000,3581956000,15430786000,11692713000,0.1159044813210004,0.0910503598060711,0.0441114174904387,0.232130495491286,0.6149935132975559
2018,3206815000,25974400000,2942359000,1605226000,5238765000,20735635000,15794341000,0.1234605996673647,0.1132791902796599,0.0618003110755205,0.2526455061540194,0.6080733722434397
2019,-677192000,33975712000,4811749000,2604254000,7582157000,26393555000,20156447000,-0.0199316499975041,0.141623198360052,0.0766504613648714,0.2872730482877354,0.593260473834956
2020,1955795000,39280359000,7573144000,4585289000,11065240000,28215119000,24996056000,0.0497906600089882,0.1927972195977129,0.1167323598035343,0.3921741389784675,0.6363499885528032
2021,-419141000,44584663000,12689372000,6194509000,15849248000,28735415000,29697844000,-0.0094010130793183,0.2846129396559529,0.1389381142120553,0.551557999075357,0.6660999994549696
2022,1335499000,48594768000,17181296000,5632831000,20777401000,27817367000,31615550000,0.0274823618871891,0.3535626716028359,0.1159143511087448,0.7469219139252108,0.6505957596093472
2023,1057478000,48731992000,22589286000,6954003000,20588313000,28143679000,33723297000,0.0216998722317774,0.4635411989725353,0.142698927636695,0.7315430580344524,0.6920155654626226
2024,2344979000,53630374000,31300917000,10417614000,24743567000,28886807000,39000966000,0.0437248302612993,0.5836415945933922,0.1942483936434976,0.8565698174948861,0.7272178635189082
"""

def to_python_native(val):
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer, int)):
        return int(val)
    if isinstance(val, (np.floating, float)):
        return float(val)
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))
    # Ensure column names are clean
    df.columns = [c.strip() for c in df.columns]

    # Prepare scr_data: source data as array of dicts with native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_native(row[col])
        scr_records.append(rec)

    # Calculate Altman Z-Score for each row
    der_records = []
    for _, row in df.iterrows():
        # Use the raw input fields to compute components
        # X1 = (Current Assets - Current Liabilities) / Total Assets
        # In the CSV Working Capital = Current Assets - Current Liabilities
        total_assets = row["Total Assets"]
        working_capital = row["Working Capital"]
        retained_earnings = row["Retained Earnings"]
        ebit = row["Operating Income"]  # EBIT approximated by Operating Income
        market_value_equity = row["Market Value of Equity"]
        total_liabilities = row["Total Liabilities"]
        revenue = row["Revenue"]

        # Defensive checks for division by zero
        ta_nonzero = float(total_assets) if total_assets != 0 else np.nan
        tl_nonzero = float(total_liabilities) if total_liabilities != 0 else np.nan

        X1 = (working_capital / ta_nonzero) if not np.isnan(ta_nonzero) else None
        X2 = (retained_earnings / ta_nonzero) if not np.isnan(ta_nonzero) else None
        X3 = (ebit / ta_nonzero) if not np.isnan(ta_nonzero) else None
        X4 = (market_value_equity / tl_nonzero) if not np.isnan(tl_nonzero) else None
        X5 = (revenue / ta_nonzero) if not np.isnan(ta_nonzero) else None

        # Compute Z using Altman weights
        # Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
        # If any component is None (due to division by zero), result becomes None
        components = [X1, X2, X3, X4, X5]
        if any(v is None or (isinstance(v, float) and np.isnan(v)) for v in components):
            z_score = None
        else:
            z_score = (
                1.2 * X1 +
                1.4 * X2 +
                3.3 * X3 +
                0.6 * X4 +
                1.0 * X5
            )

        der_rec = {
            "Fiscal Year": to_python_native(row["Fiscal Year"]),
            "奥特曼破产预测模型 (Altman Z-Score)": to_python_native(z_score) if z_score is not None else None
        }
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()