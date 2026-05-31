import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Current Assets,Cash & Equiv,Current Liabilities,Short Term Debt,CapEx,NOPAT,NCWC,Change in NCWC,Reinvestment
2016,34010000000,8555000000,26532000000,16025000000,2262000000,6969438298.918387,14948000000,-14000000.0,2248000000.0
2017,36545000000,6006000000,27194000000,16503000000,1675000000,1444073294.629898,19848000000,4900000000.0,6575000000.0
2018,24930000000,9077000000,28782000000,18838000000,1548000000,7205878662.613981,5909000000,-13939000000.0,-12391000000.0
2019,20411000000,6480000000,26973000000,15528000000,2054000000,8401882996.476914,2486000000,-3423000000.0,-1369000000.0
2020,19240000000,6795000000,14601000000,2990000000,1177000000,7168806646.835572,834000000,-1652000000.0,-475000000.0
2021,22545000000,9684000000,19950000000,4955000000,1367000000,8133571991.951711,-2134000000,-2968000000.0,-1601000000.0
2022,22591000000,9519000000,19724000000,3113000000,1484000000,8934625962.6904,-3539000000,-1405000000.0,79000000.0
2023,26732000000,9366000000,23571000000,6878000000,1852000000,9346945105.003088,673000000,4212000000.0,6064000000.0
2024,25997000000,10828000000,25249000000,2437000000,2064000000,8131194253.400581,-7643000000,-8316000000.0,-6252000000.0
"""

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are numeric (pandas should infer, but be explicit)
    numeric_cols = [
        "Current Assets", "Cash & Equiv", "Current Liabilities", "Short Term Debt",
        "CapEx", "NOPAT", "NCWC", "Change in NCWC", "Reinvestment"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Calculate Change in NCWC according to reference:
    # Change in NCWC = current NCWC - prior NCWC
    # For the first row where prior doesn't exist, fall back to provided "Change in NCWC" if present.
    computed_change = df["NCWC"].diff()
    # Use provided column to fill NaN (first row), otherwise use computed diff
    if "Change in NCWC" in df.columns:
        computed_change = computed_change.fillna(df["Change in NCWC"])
    df["Computed Change in NCWC"] = computed_change

    # Calculate Reinvestment Rate:
    # Reinvestment Rate = (CapEx + Change in NCWC) / NOPAT
    # Use computed change in NCWC
    def safe_div(numerator, denominator):
        try:
            if pd.isna(numerator) or pd.isna(denominator):
                return None
            denom = float(denominator)
            if denom == 0:
                return None
            return float(numerator) / denom
        except Exception:
            return None

    reinvest_rates = []
    for _, row in df.iterrows():
        capex = row.get("CapEx")
        change_ncwc = row.get("Computed Change in NCWC")
        nopat = row.get("NOPAT")
        numerator = None
        if pd.isna(capex) and pd.isna(change_ncwc):
            numerator = None
        else:
            capex_val = 0.0 if pd.isna(capex) else float(capex)
            change_val = 0.0 if pd.isna(change_ncwc) else float(change_ncwc)
            numerator = capex_val + change_val
        rate = safe_div(numerator, nopat)
        reinvest_rates.append(rate)

    df["Calculated Reinvestment Rate"] = reinvest_rates

    # Prepare scr_data: original CSV rows as list of dicts
    # Use original columns from df (excluding our computed helper columns)
    original_columns = ["Fiscal Year", "Current Assets", "Cash & Equiv", "Current Liabilities",
                        "Short Term Debt", "CapEx", "NOPAT", "NCWC", "Change in NCWC", "Reinvestment"]
    scr_df = df[original_columns].copy()

    # Convert to native python types for JSON serialization
    scr_data = []
    for rec in scr_df.to_dict(orient="records"):
        # Convert numpy types to native Python types where necessary
        clean_rec = {}
        for k, v in rec.items():
            if pd.isna(v):
                clean_rec[k] = None
            else:
                # Ensure ints that are whole floats become int
                if isinstance(v, float) and v.is_integer():
                    clean_rec[k] = int(v)
                else:
                    clean_rec[k] = v
        scr_data.append(clean_rec)

    # Prepare der_data: each entry contains Fiscal Year and calculated indicator
    der_data = []
    for year, rate in zip(df["Fiscal Year"], df["Calculated Reinvestment Rate"]):
        entry = {"Fiscal Year": int(year) if not pd.isna(year) else None,
                 "资本再投资率 (Reinvestment Rate)": (None if rate is None else float(rate))}
        der_data.append(entry)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to output file with ensure_ascii=False to keep Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()