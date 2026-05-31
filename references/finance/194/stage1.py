import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Net Income,Pretax Income,Operating Income,Revenue,Avg Total Assets,Avg Total Equity,Tax Burden,Interest Burden,Operating Margin,Asset Turnover,Equity Multiplier,RESULT_DuPont_ROE
2016,614000000,743000000,747000000,5010000000,7285684000.0,4443491000.0,0.8263795423956931,0.994645247657296,0.1491017964071856,0.6876499172898523,1.6396306417634243,0.138179642987912
2017,1666000000,1905000000,1934000000,6910000000,8605500000.0,5115500000.0,0.8745406824146982,0.9850051706308168,0.2798842257597684,0.8029748416710244,1.68224025021992,0.3256768644316294
2018,3047000000,3196000000,3210000000,9714000000,10541000000.0,6616500000.0,0.9533792240300376,0.9956386292834892,0.3304508956145769,0.9215444454985297,1.593138366205698,0.4605153782211139
2019,4141000000,3896000000,3804000000,11716000000,12266500000.0,8406500000.0,1.0628850102669405,1.0241850683491065,0.3246841925571868,0.955121672848816,1.459168500565039,0.4925950157616131
2020,2796000000,2970000000,2846000000,10918000000,15303500000.0,10773000000.0,0.9414141414141414,1.0435699226985242,0.2606704524638212,0.713431567941974,1.4205420959806925,0.2595377332219437
2021,4332000000,4409000000,4532000000,16675000000,23053000000.0,14548500000.0,0.9825357223860286,0.9728596646072374,0.271784107946027,0.7233331887389928,1.5845619823349486,0.2977626559439117
2022,9752000000,9941000000,10041000000,26914000000,36489000000.0,21752500000.0,0.9809878281862991,0.9900408325863956,0.3730772088875678,0.7375921510592234,1.677462360648201,0.448316285484427
2023,4368000000,4181000000,4224000000,26974000000,42684500000.0,24356500000.0,1.0447261420712748,0.9898200757575758,0.1565952398606065,0.6319389942484976,1.7524890686264447,0.1793361115102744
2024,29760000000,33818000000,32972000000,60922000000,53455000000.0,32539500000.0,0.8800047312082323,1.025658134174451,0.5412166376678376,1.1396875876905808,1.6427726301879255,0.9145807403309824
"""

INDICATOR_NAME = "净资产收益率-杜邦分析 (Return on Equity - DuPont Analysis, ROE)"

def to_python_native(val):
    # Convert pandas/numpy types to native Python types for JSON serialization
    if pd.isna(val):
        return None
    # booleans first
    if isinstance(val, (bool,)):
        return bool(val)
    # integers
    try:
        if int(val) == val:
            return int(val)
    except Exception:
        pass
    try:
        return float(val)
    except Exception:
        return val

def compute_dupont_roe(row):
    """
    ROE = (Net Income / Pretax Income) *
          (Pretax Income / EBIT) *
          (EBIT / Revenue) *
          (Revenue / Total Assets) *
          (Total Assets / Equity)
    Where EBIT is represented by Operating Income in the CSV.
    """
    net_income = row.get("Net Income")
    pretax = row.get("Pretax Income")
    ebit = row.get("Operating Income")
    revenue = row.get("Revenue")
    total_assets = row.get("Avg Total Assets")
    equity = row.get("Avg Total Equity")

    # Helper to safe-divide
    def safe_div(a, b):
        try:
            if b is None:
                return None
            if b == 0:
                return None
            return a / b
        except Exception:
            return None

    # compute each component
    comp_tax_burden = safe_div(net_income, pretax)          # 净利润 / 税前利润
    comp_interest_burden = safe_div(pretax, ebit)          # 税前利润 / 息税前利润(EBIT)
    comp_operating_margin = safe_div(ebit, revenue)        # 息税前利润 / 销售收入
    comp_asset_turnover = safe_div(revenue, total_assets)  # 销售收入 / 总资产
    comp_equity_multiplier = safe_div(total_assets, equity) # 总资产 / 股东权益

    # If any component is None (due to division by zero), overall ROE is None
    components = [comp_tax_burden, comp_interest_burden, comp_operating_margin,
                  comp_asset_turnover, comp_equity_multiplier]
    if any(c is None for c in components):
        return None

    roe = 1.0
    for c in components:
        roe *= c
    return roe

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Build scr_data: list of dicts with original CSV values (converted to native types)
    scr_records = []
    for _, r in df.iterrows():
        record = {}
        for col in df.columns:
            record[col] = to_python_native(r[col])
        scr_records.append(record)

    # Build der_data: compute the DuPont ROE per row
    der_records = []
    for _, r in df.iterrows():
        roe_value = compute_dupont_roe(r)
        # Prepare output record; include Fiscal Year if present
        out_rec = {}
        if "Fiscal Year" in df.columns:
            out_rec["Fiscal Year"] = to_python_native(r["Fiscal Year"])
        out_rec[INDICATOR_NAME] = to_python_native(roe_value)
        der_records.append(out_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to the specified path
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()