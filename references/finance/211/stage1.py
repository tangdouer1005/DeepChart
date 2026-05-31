#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Operating Income,Income Tax,Pretax Income,Effective Tax Rate,NOPAT,Avg Invested Capital
2016,13441000000,3342000000,13369000000,0.2499813000224399,10081001346.398384,83401500000.0
2017,13766000000,3063000000,13257000000,0.2310477483593573,10585396696.085089,81036500000.0
2018,13363000000,3465000000,13326000000,0.260018009905448,9888379333.6335,81126000000.0
2019,5487000000,2103000000,6069000000,0.3465150766188828,3585671774.5921893,77044000000.0
2020,15706000000,2731000000,15834000000,0.1724769483390173,12997077049.387394,69177500000.0
2021,17986000000,3263000000,17615000000,0.1852398523985239,14654276014.760147,66798000000.0
2022,17813000000,3202000000,17995000000,0.1779383161989441,14643384773.548208,69685000000.0
2023,18134000000,3615000000,18353000000,0.1969705225303765,14562136544.434153,72216500000.0
2024,18545000000,3787000000,18761000000,0.201854911785086,14801600660.94558,73433500000.0
"""

def to_native(value):
    """
    Convert pandas / numpy scalar types to native Python types for JSON serialization.
    """
    try:
        # pandas / numpy scalars have .item()
        if hasattr(value, "item"):
            return value.item()
    except Exception:
        pass
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Calculation for ROIC
    # NOPAT (税后营业利润) = Operating Income * (1 - Effective Tax Rate)
    nopat_calc = df["Operating Income"] * (1 - df["Effective Tax Rate"])

    # Invested Capital: use Avg Invested Capital column from the provided data
    invested_capital = df["Avg Invested Capital"]

    # ROIC = NOPAT / Invested Capital
    # Guard against division by zero
    roic = []
    for n, ic in zip(nopat_calc, invested_capital):
        try:
            value = float(n) / float(ic) if float(ic) != 0 else None
        except Exception:
            value = None
        roic.append(value)

    # Prepare scr_data using original CSV rows
    scr_records = []
    for row in df.to_dict(orient="records"):
        converted = {k: to_native(v) for k, v in row.items()}
        scr_records.append(converted)

    # Prepare der_data with calculated ROIC per row
    der_records = []
    for row, roic_val in zip(scr_records, roic):
        entry = {}
        # include year if present
        if "Fiscal Year" in row:
            entry["Fiscal Year"] = to_native(row["Fiscal Year"])
        entry["投入资本回报率 (Return on Invested Capital, ROIC)"] = to_native(roic_val)
        der_records.append(entry)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()