#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

csv_data = """Fiscal Year,ROA(Avg),CFO,Net Income,Long Term Debt,Avg Total Assets,Leverage,Current Ratio,Current Assets,Current Liabilities,Shares,Gross Margin,Revenue,Cost of Revenue,Asset Turnover (for F-score),1_ROA>0,2_CFO>0,3_dROA>0,4_CFO>NI,5_dLev<0,6_dCurrent>0,7_NoDilute,8_dMargin>0,9_dTurnover>0
2016,0.0599584725414633,9795000000,7017000000,25777000000,117031000000.0,0.2202578803906657,0.685725896576247,33748000000,49215000000,968000000,0.2346722358084273,184828000000,141454000000,1.5793080465859473,1,1,1,1,1,0,0,0,0
2017,0.0806767124125072,13596000000,10558000000,28835000000,130868000000.0,0.2203365222972766,0.7348750569724353,37084000000,50463000000,985000000,0.2337007044178982,201159000000,154148000000,1.5371137329217226,1,1,1,1,0,1,0,0,0
2018,0.0822993840935463,15713000000,11986000000,34581000000,145639000000.0,0.23744326725671,0.727170215565036,38692000000,53209000000,983000000,0.2379965259207856,226247000000,172401000000,1.553478120558367,1,1,1,1,0,0,1,1,1
2019,0.0848732022937045,18463000000,13839000000,36808000000,163055000000.0,0.225739781055472,0.6900715418730374,42634000000,61782000000,966000000,0.2378559187297392,242155000000,184557000000,1.4851123853914323,1,1,1,1,1,0,1,0,0
2020,0.0829952206219118,22174000000,15403000000,38648000000,185589000000.0,0.2082451007333408,0.7417564208782105,53718000000,72420000000,961000000,0.2605574373592698,257141000000,190141000000,1.3855400912769615,1,1,0,1,1,1,1,1,0
2021,0.0844210552021392,22343000000,17285000000,42383000000,204747500000.0,0.2070013064872587,0.7888162264343739,61758000000,78292000000,956000000,0.2421861145978574,287597000000,217945000000,1.404642303324827,1,1,1,1,1,1,1,0,1
2022,0.0878773386094677,26206000000,20120000000,54513000000,228955500000.0,0.2380943021678885,0.7739950917220435,69069000000,89237000000,950000000,0.24560867714291,324162000000,244545000000,1.4158297136343088,1,1,1,1,0,0,1,1,1
2023,0.0861760600664196,29068000000,22381000000,58263000000,259712500000.0,0.2243365259662126,0.7918610051083248,78437000000,99054000000,938000000,0.2447594598812772,371622000000,280664000000,1.4308976271839051,1,1,0,1,1,1,1,0,1
2024,0.0503673089766048,24204000000,14405000000,72359000000,285999000000.0,0.2530043811341997,0.8266341585637329,85779000000,103769000000,929000000,0.2233422771174034,400278000000,310879000000,1.3995783202039167,1,1,0,1,0,1,1,0,0
"""

def numpy_to_native(v):
    """
    Convert numpy/pandas scalar types to native Python types for JSON serialization.
    """
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.bool_ , bool)):
        return bool(v)
    if pd.isna(v):
        return None
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded multi-line string
    df = pd.read_csv(io.StringIO(csv_data))

    # Prepare previous-year comparisons by shifting
    df['prev_ROA'] = df['ROA(Avg)'].shift(1)
    df['prev_Leverage'] = df['Leverage'].shift(1)
    df['prev_CurrentRatio'] = df['Current Ratio'].shift(1)
    df['prev_GrossMargin'] = df['Gross Margin'].shift(1)
    df['prev_AssetTurnover'] = df['Asset Turnover (for F-score)'].shift(1)
    df['prev_Shares'] = df['Shares'].shift(1)

    der_rows = []
    for idx, row in df.iterrows():
        # Indicator 1: ROA > 0
        ind1 = 1 if row['ROA(Avg)'] > 0 else 0

        # Indicator 2: CFO > 0
        ind2 = 1 if row['CFO'] > 0 else 0

        # Indicator 3: ΔROA > 0 (requires previous year)
        ind3 = 0
        if not pd.isna(row['prev_ROA']):
            ind3 = 1 if (row['ROA(Avg)'] - row['prev_ROA']) > 0 else 0

        # Indicator 4: Accruals quality: CFO > Net Income
        ind4 = 1 if row['CFO'] > row['Net Income'] else 0

        # Indicator 5: ΔLeverage < 0 (long-term leverage decreased)
        ind5 = 0
        if not pd.isna(row['prev_Leverage']):
            ind5 = 1 if (row['Leverage'] - row['prev_Leverage']) < 0 else 0

        # Indicator 6: ΔCurrent Ratio > 0
        ind6 = 0
        if not pd.isna(row['prev_CurrentRatio']):
            ind6 = 1 if (row['Current Ratio'] - row['prev_CurrentRatio']) > 0 else 0

        # Indicator 7: No Dilution: current shares <= previous shares
        ind7 = 0
        if not pd.isna(row['prev_Shares']):
            # If shares decreased or unchanged -> no dilution
            ind7 = 1 if row['Shares'] <= row['prev_Shares'] else 0
        else:
            # If no prior year, we cannot confirm dilution; conservative -> 0
            ind7 = 0

        # Indicator 8: ΔGross Margin > 0
        ind8 = 0
        if not pd.isna(row['prev_GrossMargin']):
            ind8 = 1 if (row['Gross Margin'] - row['prev_GrossMargin']) > 0 else 0

        # Indicator 9: ΔAsset Turnover > 0
        ind9 = 0
        if not pd.isna(row['prev_AssetTurnover']):
            ind9 = 1 if (row['Asset Turnover (for F-score)'] - row['prev_AssetTurnover']) > 0 else 0

        fscore = int(ind1 + ind2 + ind3 + ind4 + ind5 + ind6 + ind7 + ind8 + ind9)

        der_row = {
            'Fiscal Year': numpy_to_native(row['Fiscal Year']),
            '皮奥特罗斯基 F-Score (Piotroski F-Score)': numpy_to_native(fscore)
        }
        der_rows.append(der_row)

    # Prepare scraped data (original CSV rows) as native Python types
    scr_records = df.drop(columns=['prev_ROA','prev_Leverage','prev_CurrentRatio','prev_GrossMargin','prev_AssetTurnover','prev_Shares']).to_dict(orient='records')
    # Convert numpy types to native Python
    scr_clean = []
    for r in scr_records:
        clean = {}
        for k, v in r.items():
            clean[k] = numpy_to_native(v)
        scr_clean.append(clean)

    output_obj = {
        "scr_data": scr_clean,
        "der_data": der_rows
    }

    # Write JSON to specified output file (ensure Chinese characters preserved)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()