import sys
import io
import json
import pandas as pd
import math

CSV_DATA = """Fiscal Year,Operating Income,Income Tax,Pretax Income,Effective Tax Rate,NOPAT,Avg Invested Capital
2016,-5471000000,1729000000,-2160000000,0.0,-5471000000.0,182403000000.0
2017,3128000000,48000000,9221000000,0.005205509163865,3111717167.33543,183290500000.0
2018,14446000000,5715000000,20575000000,0.2777642770352369,10433417253.948969,180825500000.0
2019,100000000,2691000000,5536000000,0.4860910404624277,51390895.953757234,172585500000.0
2020,-6942000000,1892000000,-7453000000,0.0,-6942000000.0,167730000000.0
2021,16104000000,5950000000,21639000000,0.2749664956790979,11675939553.583809,181309000000.0
2022,50190000000,14066000000,49674000000,0.2831662439102951,35977886218.14229,178599000000.0
2023,33790000000,8173000000,29584000000,0.2762641968631693,24455032787.99351,168790500000.0
2024,29099000000,9757000000,27506000000,0.3547226059768777,18776926888.678837,171286500000.0
"""

INDICATOR_NAME = "投入资本回报率 (Return on Invested Capital, ROIC)"

def safe_divide(numerator, denominator):
    try:
        if denominator is None:
            return None
        if math.isnan(denominator):
            return None
        if denominator == 0:
            return None
        val = numerator / denominator
        if isinstance(val, float) and (math.isinf(val) or math.isnan(val)):
            return None
        return val
    except Exception:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: convert DataFrame rows to native Python types
    scr_data = []
    for _, row in df.iterrows():
        # Convert numpy types to Python native types for JSON serialization
        entry = {
            "Fiscal Year": int(row["Fiscal Year"]) if not pd.isna(row["Fiscal Year"]) else None,
            "Operating Income": None if pd.isna(row["Operating Income"]) else float(row["Operating Income"]),
            "Income Tax": None if pd.isna(row["Income Tax"]) else float(row["Income Tax"]),
            "Pretax Income": None if pd.isna(row["Pretax Income"]) else float(row["Pretax Income"]),
            "Effective Tax Rate": None if pd.isna(row["Effective Tax Rate"]) else float(row["Effective Tax Rate"]),
            "NOPAT": None if pd.isna(row["NOPAT"]) else float(row["NOPAT"]),
            "Avg Invested Capital": None if pd.isna(row["Avg Invested Capital"]) else float(row["Avg Invested Capital"]),
        }
        scr_data.append(entry)

    # Derive ROIC using the reference formula:
    # NOPAT = Operating Income * (1 - Effective Tax Rate)
    # Invested Capital = Avg Invested Capital (provided)
    # ROIC = NOPAT / Invested Capital
    der_data = []
    for row in scr_data:
        yr = row.get("Fiscal Year")
        op_income = row.get("Operating Income")
        eff_tax = row.get("Effective Tax Rate")
        invested_cap = row.get("Avg Invested Capital")

        # Compute NOPAT from Operating Income and Effective Tax Rate when possible
        if op_income is None or eff_tax is None:
            computed_nopat = None
        else:
            try:
                computed_nopat = op_income * (1.0 - eff_tax)
            except Exception:
                computed_nopat = None

        # If computed_nopat is None but NOPAT raw exists in scr_data, prefer computed per reference,
        # but still allow fallback to raw NOPAT only if computation impossible.
        if computed_nopat is None:
            computed_nopat = row.get("NOPAT")

        roic_value = safe_divide(computed_nopat, invested_cap)

        # Keep numeric as float or null
        der_entry = {
            "Fiscal Year": yr
        }
        der_entry[INDICATOR_NAME] = None if roic_value is None else float(roic_value)
        der_data.append(der_entry)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()