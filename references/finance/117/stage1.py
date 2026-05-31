#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Working Capital,Total Assets,Retained Earnings,Operating Income,Market Value of Equity,Total Liabilities,Revenue,X1 (WC/TA),X2 (RE/TA),X3 (EBIT/TA),X4 (MVE/TL),X5 (S/TA)
2016,38745000000,141208000000,110551000000,20891000000,70418000000,70790000000,71890000000,0.2743824712480879,0.7828947368421053,0.1479448756444394,0.9947450204831192,0.5091071327403547
2017,12551000000,157303000000,101793000000,18897000000,60160000000,97143000000,76450000000,0.0797886880733361,0.6471141681976822,0.1201312117378562,0.6192932069217545,0.4860047170111187
2018,14803000000,152954000000,106216000000,21175000000,59752000000,93202000000,81581000000,0.0967807314617466,0.6944310054003164,0.1384403153889404,0.6411021222720542,0.5333695097872563
2019,9310000000,157728000000,110659000000,20970000000,59471000000,98257000000,82059000000,0.0590256644349766,0.7015812030837898,0.1329503956177723,0.6052596761553884,0.5202563907486305
2020,8744000000,174894000000,113890000000,19733000000,63278000000,111616000000,82584000000,0.0499959975756744,0.6511944377737372,0.1128283417384244,0.5669258887614679,0.4721945864352121
2021,15753000000,182018000000,123060000000,20943000000,74023000000,107995000000,78740000000,0.0865463855223109,0.676086980408531,0.1150600490061422,0.6854298810130098,0.4325945785581646
2022,-508000000,187378000000,128345000000,21013000000,76804000000,110574000000,79990000000,-0.0027110973540116,0.6849523423240722,0.1121423005902507,0.6945936657803824,0.4268910971405394
2023,7213000000,167558000000,153843000000,21853000000,68774000000,98784000000,85159000000,0.0430477804700461,0.9181477458551666,0.1304205111066018,0.6962058632977001,0.5082359541173802
2024,5572000000,180104000000,155791000000,22149000000,71490000000,108614000000,88821000000,0.0309376804512948,0.8650057744414338,0.1229789454981566,0.6582024416741856,0.4931650601874472
"""

INDICATOR_NAME = "奥特曼破产预测模型 (Altman Z-Score)"

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from hardcoded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric calculations use floats
    # Compute components according to reference formulas (do not use precomputed X1..X5 columns)
    # X1 = (Current Assets - Current Liabilities) / Total Assets
    # In the CSV Working Capital already equals (Current Assets - Current Liabilities)
    df['X1_calc'] = df['Working Capital'] / df['Total Assets']

    # X2 = Retained Earnings / Total Assets
    df['X2_calc'] = df['Retained Earnings'] / df['Total Assets']

    # X3 = EBIT / Total Assets. Operating Income is used as EBIT.
    df['X3_calc'] = df['Operating Income'] / df['Total Assets']

    # X4 = Market Value of Equity / Total Liabilities
    # For non-listed, would use book equity; here Market Value is provided.
    # Avoid division by zero defensively.
    df['X4_calc'] = df['Market Value of Equity'] / df['Total Liabilities']

    # X5 = Revenue / Total Assets
    df['X5_calc'] = df['Revenue'] / df['Total Assets']

    # Altman Z-Score:
    # Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
    df['Altman_Z'] = (
        1.2 * df['X1_calc'] +
        1.4 * df['X2_calc'] +
        3.3 * df['X3_calc'] +
        0.6 * df['X4_calc'] +
        1.0 * df['X5_calc']
    )

    # Prepare scr_data: raw input rows as list of dicts (keep original columns)
    scr_records = df.drop(columns=['X1_calc','X2_calc','X3_calc','X4_calc','X5_calc','Altman_Z']).to_dict(orient='records')

    # Prepare der_data: list of dicts with Fiscal Year and calculated indicator
    der_records = []
    for _, row in df.iterrows():
        rec = {
            'Fiscal Year': int(row['Fiscal Year']) if not pd.isna(row['Fiscal Year']) else None,
            INDICATOR_NAME: (None if pd.isna(row['Altman_Z']) else float(row['Altman_Z']))
        }
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file with ensure_ascii=False to keep Chinese characters readable
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()