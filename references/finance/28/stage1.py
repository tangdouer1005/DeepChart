import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Working Capital,Total Assets,Retained Earnings,Operating Income,Market Value of Equity,Total Liabilities,Revenue,X1 (WC/TA),X2 (RE/TA),X3 (EBIT/TA),X4 (MVE/TL),X5 (S/TA)
2016,3097298000,20609004000,7879960000,4810445000,7555262000,12419628000,34797661000,0.150288582602051,0.3823552074617483,0.2334147249425542,0.6083323912761316,1.6884688362426443
2017,2273010000,22689890000,7081855000,5191402000,8949477000,12979690000,36176841000,0.1001772154911284,0.3121149992353422,0.2287980241420297,0.6894985165285149,1.5944035427232128
2018,3433808000,24449083000,7952413000,5898779000,10364753000,13724495000,40992534000,0.1404473124820264,0.3252642645124972,0.2412679035855864,0.7552010474702348,1.6766491405833095
2019,4388705000,29789880000,10421538000,6305074000,14409008000,14962189000,43215013000,0.1473220100248809,0.3498348432420674,0.2116515407245682,0.9630280702910516,1.4506608620108574
2020,5087166000,37078593000,12375533000,6513644000,17000536000,19579420000,44327039000,0.1371995426040033,0.3337649031072996,0.1756712828882153,0.8682859859995853,1.1954887015265114
2021,3957644000,43175843000,13988748000,7621529000,19529454000,23078729000,50533389000,0.0916633868619542,0.323994785695325,0.1765229922667636,0.8462101184168331,1.1704088557112828
2022,4087375000,47263390000,18203842000,9367181000,22106097000,24516302000,61594305000,0.0864807835409182,0.3851573490602346,0.198191052313429,0.9016897001839838,1.303213861722572
2023,5372893000,51245305000,19316224000,8809889000,25692839000,24786712000,64111745000,0.104846541551465,0.3769364627647352,0.1719160223556089,1.0365569664907552,1.2510754887691662
2024,1881654000,55932363000,23082423000,9595847000,28288646000,26764115000,64896464000,0.0336415967263889,0.4126845668937677,0.1715616234558157,1.0569617564414142,1.1602668029598535
"""

INDICATOR_NAME = "奥特曼破产预测模型 (Altman Z-Score)"

def to_python_native(value):
    if pd.isna(value):
        return None
    # numpy scalar types
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value

def compute_altman_z(row):
    # Use raw accounting fields to compute the five X ratios per reference
    # X1 = (Current Assets - Current Liabilities) / Total Assets
    # Here "Working Capital" is provided as Current Assets - Current Liabilities
    try:
        wc = float(row["Working Capital"])
    except Exception:
        wc = np.nan
    try:
        total_assets = float(row["Total Assets"])
    except Exception:
        total_assets = np.nan
    try:
        retained = float(row["Retained Earnings"])
    except Exception:
        retained = np.nan
    try:
        ebit = float(row["Operating Income"])  # Operating Income ~ EBIT
    except Exception:
        ebit = np.nan
    try:
        mve = float(row["Market Value of Equity"])
    except Exception:
        mve = np.nan
    try:
        total_liabilities = float(row["Total Liabilities"])
    except Exception:
        total_liabilities = np.nan
    try:
        revenue = float(row["Revenue"])
    except Exception:
        revenue = np.nan

    # Defensive handling for divisions
    X1 = wc / total_assets if (total_assets != 0 and not np.isnan(total_assets)) else None
    X2 = retained / total_assets if (total_assets != 0 and not np.isnan(total_assets)) else None
    X3 = ebit / total_assets if (total_assets != 0 and not np.isnan(total_assets)) else None
    X4 = mve / total_liabilities if (total_liabilities != 0 and not np.isnan(total_liabilities)) else None
    X5 = revenue / total_assets if (total_assets != 0 and not np.isnan(total_assets)) else None

    # If any X is None, propagate as NaN in result
    components = []
    for x in (X1, X2, X3, X4, X5):
        if x is None or np.isnan(x):
            components.append(np.nan)
        else:
            components.append(float(x))

    z = (1.2 * components[0] +
         1.4 * components[1] +
         3.3 * components[2] +
         0.6 * components[3] +
         1.0 * components[4])

    # If any component is nan, z will be nan
    if any(np.isnan(c) for c in components):
        z_value = None
    else:
        z_value = float(z)
    return z_value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Build scr_data: list of row dicts with native python types
    scr_records = []
    for _, row in df.iterrows():
        row_dict = {}
        for col in df.columns:
            row_dict[col] = to_python_native(row[col])
        scr_records.append(row_dict)

    # Build der_data: compute Altman Z per row
    der_records = []
    for _, row in df.iterrows():
        z = compute_altman_z(row)
        der_row = {}
        # include Year if present
        if "Fiscal Year" in df.columns:
            der_row["Fiscal Year"] = to_python_native(row["Fiscal Year"])
        der_row[INDICATOR_NAME] = to_python_native(z)
        der_records.append(der_row)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON with ensure_ascii=False to keep Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()