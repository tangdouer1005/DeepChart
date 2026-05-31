import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Avg Receivables,Revenue,Avg Inventory,Cost of Revenue,Avg Payables,DSO,DIO,DPO
2016,37550000000.0,119468000000,22450000000.0,87652000000,14057500000.0,114.72318947333176,93.48617259161227,58.53816798247615
2017,38573000000.0,99279000000,20909500000.0,75593000000,14803500000.0,141.81392842393657,100.96129932665724,71.47854298678449
2018,34223000000.0,97012000000,19359500000.0,69403000000,16162500000.0,128.761338803447,101.8142947711194,85.00082849444549
2019,23750000000.0,90221000000,16700000000.0,64852000000,16539500000.0,96.08350605734806,93.99093320175167,93.08760716708814
2020,21177500000.0,75834000000,14995000000.0,57871000000,16192000000.0,101.9303676451196,94.575435019267,102.12507127922449
2021,21478000000.0,56469000000,15868500000.0,43378000000,16350500000.0,138.82785245001682,133.52396376043157,137.5797063027341
2022,19128000000.0,76555000000,15369000000.0,55535000000,13138000000.0,91.19874599960812,101.01170433060231,86.34860898532457
2023,14666500000.0,35348000000,11587500000.0,22939000000,8397500000.0,151.4448483648297,184.3775883865905,133.61905488469418
2024,11943500000.0,38702000000,9023500000.0,24308000000,7137500000.0,112.63959226913336,135.49356179035706,107.1740784926773
"""

INDICATOR_NAME = "现金循环周期 (Cash Conversion Cycle, CCC)"

def to_native(obj):
    """Convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    return obj

def convert_record(rec):
    """Convert all values in a dict record to native Python types."""
    new = {}
    for k, v in rec.items():
        if pd.isna(v):
            new[k] = None
        else:
            new[k] = to_native(v)
    return new

def compute_ccc(row):
    """
    Compute Cash Conversion Cycle (CCC) for a row.
    DSO = (Avg Receivables / Revenue) * 365
    DIO = (Avg Inventory / Cost of Revenue) * 365
    DPO = (Avg Payables / Cost of Revenue) * 365
    CCC = DSO + DIO - DPO
    If any denominator is zero or missing, return None for that component and for CCC.
    """
    try:
        ar = row.get("Avg Receivables", None)
        rev = row.get("Revenue", None)
        inv = row.get("Avg Inventory", None)
        cogs = row.get("Cost of Revenue", None)
        ap = row.get("Avg Payables", None)

        # Validate denominators
        if rev is None or rev == 0 or pd.isna(rev):
            return None
        if cogs is None or cogs == 0 or pd.isna(cogs):
            return None

        dso = (ar / rev) * 365 if (ar is not None and not pd.isna(ar)) else None
        dio = (inv / cogs) * 365 if (inv is not None and not pd.isna(inv)) else None
        dpo = (ap / cogs) * 365 if (ap is not None and not pd.isna(ap)) else None

        if dso is None or dio is None or dpo is None:
            return None

        ccc = dso + dio - dpo
        return float(ccc)
    except Exception:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows as list of dicts with native types
    scr_records = df.to_dict(orient="records")
    scr_data = [convert_record(rec) for rec in scr_records]

    # Compute CCC for each row and prepare der_data
    der_data = []
    for rec in scr_records:
        ccc_value = compute_ccc(rec)
        # Include the Fiscal Year if present
        der_entry = {}
        if "Fiscal Year" in rec:
            der_entry["Fiscal Year"] = to_native(rec["Fiscal Year"])
        der_entry[INDICATOR_NAME] = to_native(ccc_value) if ccc_value is not None else None
        der_data.append(der_entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to specified output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()