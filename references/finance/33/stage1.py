#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import math
import numpy as np

CSV_DATA = """Fiscal Year,Operating Income,Income Tax,Pretax Income,Effective Tax Rate,NOPAT,Avg Invested Capital
2016,4186000000,1425000000,3892000000,0.3661356628982528,2653356115.107913,9404500000.0
2017,4106000000,1558000000,3806000000,0.4093536521282186,2425193904.3615346,25477000000.0
2018,12421000000,1354000000,11261000000,0.1202379895213568,10927523932.155226,41454000000.0
2019,14541000000,2374000000,13976000000,0.1698626216370921,12071027618.775042,47742500000.0
2020,22899000000,2863000000,24178000000,0.1184134337000579,20187450781.702374,74951000000.0
2021,24879000000,4791000000,38151000000,0.1255799323739875,21754696862.467564,132952500000.0
2022,12248000000,3217000000,-5936000000,0.0,12248000000.0,170425500000.0
2023,36852000000,7120000000,37557000000,0.1895785073355166,29865652847.67153,189953000000.0
2024,68593000000,9265000000,68513000000,0.1352298104009458,59317181615.16792,232856000000.0
"""

def normalize_value(v):
    # Convert numpy / pandas scalar types to native Python types and handle NaN
    if v is None:
        return None
    if isinstance(v, (float, int, str, bool)):
        if isinstance(v, float):
            if math.isnan(v):
                return None
        return v
    # numpy types
    try:
        if isinstance(v, (np.floating, np.integer)):
            pyval = v.item()
            if isinstance(pyval, float) and math.isnan(pyval):
                return None
            return pyval
    except Exception:
        pass
    # pandas NaT etc
    try:
        if pd.isna(v):
            return None
    except Exception:
        pass
    # fallback to string
    return str(v)

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python this.py output.json\n")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are numeric where possible
    for col in df.columns:
        # Try converting to numeric; leave non-convertible as is
        df[col] = pd.to_numeric(df[col], errors='ignore')

    # Calculation per reference:
    # NOPAT = Operating Income * (1 - Effective Tax Rate)
    # Invested Capital = use Avg Invested Capital column (no breakdown provided)
    # ROIC = NOPAT / Invested Capital

    # Prepare columns expected
    op_income_col = 'Operating Income'
    eff_tax_col = 'Effective Tax Rate'
    avg_inv_cap_col = 'Avg Invested Capital'

    # Compute NOPAT according to reference; do not use precomputed NOPAT column directly for calculation
    # (we still preserve original data in scr_data)
    # Result will be float or None if insufficient data
    def compute_roic_row(row):
        try:
            op_income = row.get(op_income_col, None)
            eff_tax = row.get(eff_tax_col, None)
            invested = row.get(avg_inv_cap_col, None)
            # Validate inputs
            if op_income is None or invested is None:
                return None
            # convert to numeric
            op_income = float(op_income)
            invested = float(invested)
            # Effective tax rate may be missing; if so try to derive from Income Tax / Pretax Income
            if eff_tax is None or (isinstance(eff_tax, float) and math.isnan(eff_tax)):
                # attempt derive
                pretax = row.get('Pretax Income', None)
                income_tax = row.get('Income Tax', None)
                if pretax is not None and income_tax is not None:
                    try:
                        pretax_f = float(pretax)
                        income_tax_f = float(income_tax)
                        if pretax_f != 0:
                            eff_tax = income_tax_f / pretax_f
                        else:
                            eff_tax = 0.0
                    except Exception:
                        eff_tax = 0.0
                else:
                    eff_tax = 0.0
            else:
                eff_tax = float(eff_tax)

            nopat = op_income * (1.0 - eff_tax)

            # Avoid division by zero or near-zero invested capital
            if invested == 0 or math.isclose(invested, 0.0):
                return None

            roic = nopat / invested
            return float(roic)
        except Exception:
            return None

    records = df.to_dict(orient='records')

    scr_data = []
    der_data = []
    indicator_key = "投入资本回报率 (Return on Invested Capital, ROIC)"

    for rec in records:
        # Normalize scr_data values to plain Python types
        norm_rec = {}
        for k, v in rec.items():
            norm_rec[k] = normalize_value(v)
        scr_data.append(norm_rec)

        roic_val = compute_roic_row(rec)
        # Prepare der record: include Fiscal Year if present
        der_rec = {}
        if 'Fiscal Year' in rec:
            fy = rec.get('Fiscal Year')
            der_rec['Fiscal Year'] = normalize_value(fy)
        der_rec[indicator_key] = normalize_value(roic_val)
        der_data.append(der_rec)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to file
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()