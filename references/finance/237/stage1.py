#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Working Capital,Total Assets,Retained Earnings,Operating Income,Market Value of Equity,Total Liabilities,Revenue,X1 (WC/TA),X2 (RE/TA),X3 (EBIT/TA),X4 (MVE/TL),X5 (S/TA)
2016,5195000000,65891000000,-20610000000,4050000000,18236000000,47655000000,37490000000,0.0788423305155484,-0.3127893035467666,0.0614651469851724,0.3826670863498059,0.5689699655491646
2017,-2600000000,70563000000,-16074000000,4888000000,22559000000,48004000000,40604000000,-0.0368465059592137,-0.2277964372263084,0.0692714312033218,0.4699400049995834,0.575429049218429
2018,-1986000000,72468000000,-12954000000,5309000000,24718000000,47750000000,43310000000,-0.027405199536347,-0.1787547607219738,0.0732599216205773,0.5176544502617801,0.5976430976430976
2019,-3201000000,86921000000,-8833000000,5722000000,28789000000,58132000000,44998000000,-0.0368265436430782,-0.1016210121834769,0.0658298915106821,0.495234982453726,0.5176884757423408
2020,2182000000,200162000000,-5836000000,6636000000,65344000000,134818000000,68397000000,0.0109011700522576,-0.0291563833295031,0.033153145951779,0.4846830541915768,0.3417082163447607
2021,-2608000000,206563000000,-2812000000,6892000000,69102000000,137461000000,80118000000,-0.012625688046746,-0.0136132802099117,0.033365123473226,0.5027025847331243,0.3878622986691711
2022,-5675000000,211338000000,-223000000,6543000000,69656000000,141682000000,79571000000,-0.0268527193405823,-0.0010551817467753,0.0309598841665956,0.4916361993760675,0.376510613330305
2023,-1913000000,207682000000,7347000000,14266000000,64715000000,142967000000,78558000000,-0.0092111978890804,0.0353762001521557,0.0686915572846948,0.452656906838641,0.3782609951753161
2024,-1770000000,208035000000,14384000000,18010000000,61741000000,146294000000,81400000000,-0.0085081837190857,0.0691422116470786,0.0865719710625615,0.4220337129342283,0.3912803134088014
"""

def to_native(obj):
    # Convert numpy / pandas scalar types to native python types for JSON serialization
    try:
        # For pandas / numpy scalars
        if hasattr(obj, "item"):
            return obj.item()
    except Exception:
        pass
    # Fallback: return as-is (json.dump will error if not serializable)
    return obj

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data preserving original headers and converting scalars to native types
    # Replace NaN with None
    df_clean = df.where(pd.notnull(df), None)

    scr_records = []
    for _, row in df_clean.iterrows():
        rec = {}
        for col in df_clean.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Calculate Altman Z-Score for each row
    der_records = []
    indicator_name = "奥特曼破产预测模型 (Altman Z-Score)"

    for _, row in df.iterrows():
        # Extract required raw inputs (use the raw numeric columns)
        # X1 = (Current Assets - Current Liabilities) / Total Assets
        # Here Working Capital is provided = Current Assets - Current Liabilities
        working_capital = row["Working Capital"]
        total_assets = row["Total Assets"]
        retained_earnings = row["Retained Earnings"]
        ebit = row["Operating Income"]  # treated as EBIT per reference
        market_value_equity = row["Market Value of Equity"]
        total_liabilities = row["Total Liabilities"]
        revenue = row["Revenue"]

        # Defensive checks to avoid division by zero
        ta = float(total_assets) if total_assets != 0 else None
        tl = float(total_liabilities) if total_liabilities != 0 else None

        X1 = (float(working_capital) / ta) if (ta is not None and ta != 0) else None
        X2 = (float(retained_earnings) / ta) if (ta is not None and ta != 0) else None
        X3 = (float(ebit) / ta) if (ta is not None and ta != 0) else None
        X4 = (float(market_value_equity) / tl) if (tl is not None and tl != 0) else None
        X5 = (float(revenue) / ta) if (ta is not None and ta != 0) else None

        # Compute Z using the Altman formula
        # Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
        components = []
        for weight, x in [(1.2, X1), (1.4, X2), (3.3, X3), (0.6, X4), (1.0, X5)]:
            if x is None:
                components.append(0.0)
            else:
                components.append(weight * x)
        Z = sum(components)

        # Prepare output record; include the fiscal year if present
        out_rec = {}
        if "Fiscal Year" in df.columns:
            out_rec["Fiscal Year"] = to_native(row["Fiscal Year"])
        out_rec[indicator_name] = to_native(float(Z))
        der_records.append(out_rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON with UTF-8 and ensure Chinese characters preserved
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()