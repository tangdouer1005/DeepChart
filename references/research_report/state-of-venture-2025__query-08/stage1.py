
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def to_millions(value, unit):
    if value is None or unit is None:
        return None
    return value * 1000.0 if unit == "B" else value


def annual_totals(rows, year):
    out = defaultdict(lambda: {"funding_m": 0.0, "deals": 0})
    for row in rows:
        if row["year"] != year:
            continue
        entity = row["entity"]
        out[entity]["funding_m"] += to_millions(row["funding_value"], row["funding_unit"])
        out[entity]["deals"] += row["deals"]
    return dict(out)


def quarter_value(rows, year, quarter):
    out = {}
    for row in rows:
        if row["year"] == year and row["quarter"] == quarter:
            out[row["entity"]] = to_millions(row["funding_value"], row["funding_unit"])
    return out


def stage_lookup(rows):
    return {row["entity"]: row for row in rows}


def top_lookup(rows):
    out = defaultdict(list)
    for row in rows:
        out[row["entity"]].append(row)
    return dict(out)


def disclosed_amounts(rows):
    amounts = [to_millions(row["amount_value"], row["amount_unit"]) for row in rows]
    return [value for value in amounts if value is not None]


def top_sum(rows, limit=None):
    values = disclosed_amounts(rows)
    if limit is not None:
        values = values[:limit]
    return float(sum(values))


def largest_amount(rows):
    values = disclosed_amounts(rows)
    return max(values) if values else None


def cagr(start, end, periods):
    if start is None or end is None or start <= 0 or end <= 0:
        return None
    return ((end / start) ** (1 / periods) - 1) * 100.0


def sort_desc(rows, field):
    return sorted(rows, key=lambda row: row[field], reverse=True)


def write_output(payload):
    (ROOT / "final_chart_data.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


direct = json.loads((ROOT / "direct_data.json").read_text(encoding="utf-8"))
qk = direct["query_key"]


if qk == "005_q01":
    totals = annual_totals(direct["quarterly_rows"], 2025)
    exclude = set(direct["params"]["exclude_entities"])
    rows = []
    for entity, vals in totals.items():
        if entity in exclude:
            continue
        rows.append({"label": entity, "value": vals["funding_m"] / vals["deals"]})
    rows = sort_desc(rows, "value")[:10]
    write_output({
        "status": "complete",
        "chart_type": "barh",
        "title": "Top 10 markets by 2025 average funding per deal",
        "x_label": "Average funding per deal ($M)",
        "y_label": "Market",
        "value_format": "float2",
        "data": rows,
    })

elif qk == "005_q02":
    totals = annual_totals(direct["quarterly_rows"], 2025)
    stage = stage_lookup(direct["stage_rows"])
    deals = top_lookup(direct["top_deals_rows"])
    ranked = sorted(totals.items(), key=lambda item: item[1]["funding_m"], reverse=True)[:12]
    rows = []
    for entity, vals in ranked:
        rows.append({
            "label": entity,
            "x": top_sum(deals.get(entity, []), 5) / vals["funding_m"] * 100.0,
            "y": stage[entity]["late_pct"],
            "size": vals["funding_m"] / 1000.0,
            "annual_funding_b": vals["funding_m"] / 1000.0,
        })
    rows = sort_desc(rows, "x")
    write_output({
        "status": "complete",
        "chart_type": "bubble",
        "title": "Top-12 markets by 2025 funding: concentration vs late-stage share",
        "x_label": "Top-5 deal concentration share of 2025 funding (%)",
        "y_label": "Late-stage deal share in 2025 (%)",
        "size_label": "Annual funding ($B)",
        "data": rows,
    })

elif qk == "005_q03":
    totals_2024 = annual_totals(direct["quarterly_rows"], 2024)
    totals_2025 = annual_totals(direct["quarterly_rows"], 2025)
    rows = []
    for entity in sorted(set(totals_2024) & set(totals_2025)):
        funding_growth = (totals_2025[entity]["funding_m"] / totals_2024[entity]["funding_m"] - 1) * 100.0
        deal_growth = (totals_2025[entity]["deals"] / totals_2024[entity]["deals"] - 1) * 100.0
        rows.append({
            "label": entity,
            "left": funding_growth,
            "right": deal_growth,
            "abs_gap": abs(funding_growth - deal_growth),
        })
    rows = sort_desc(rows, "abs_gap")[:10]
    write_output({
        "status": "complete",
        "chart_type": "dumbbell",
        "title": "Top 10 markets by 2024-2025 funding/deal growth divergence",
        "x_label": "Growth rate (%)",
        "left_label": "Funding growth",
        "right_label": "Deal growth",
        "data": rows,
    })

elif qk == "005_q04":
    totals = annual_totals(direct["quarterly_rows"], 2025)
    stage = stage_lookup(direct["stage_rows"])
    deals = top_lookup(direct["top_deals_rows"])
    rows = []
    for entity, vals in totals.items():
        if vals["deals"] < 100:
            continue
        rows.append({
            "label": entity,
            "x": stage[entity]["early_pct"],
            "y": vals["funding_m"] / vals["deals"],
            "size": top_sum(deals.get(entity, []), 5) / 1000.0,
        })
    rows = sort_desc(rows, "size")
    write_output({
        "status": "complete",
        "chart_type": "bubble",
        "title": "Markets with 100+ 2025 deals: early-stage share vs average funding per deal",
        "x_label": "Early-stage share in 2025 (%)",
        "y_label": "Average funding per deal ($M)",
        "size_label": "Top-5 deal sum ($B)",
        "data": rows,
    })

elif qk == "005_q05":
    totals = annual_totals(direct["quarterly_rows"], 2025)
    rows = []
    for child, parent in direct["params"]["parent_map"].items():
        if child not in totals or parent not in totals:
            continue
        rows.append({
            "label": f"{child} / {parent}",
            "value": totals[child]["funding_m"] / totals[parent]["funding_m"] * 100.0,
        })
    rows = sort_desc(rows, "value")[:8]
    write_output({
        "status": "complete",
        "chart_type": "barh",
        "title": "Top 8 child markets by share of parent 2025 funding",
        "x_label": "Child share of parent annual funding (%)",
        "y_label": "Child / parent pair",
        "value_format": "float2",
        "data": rows,
    })

elif qk == "005_q06":
    totals_2024 = annual_totals(direct["quarterly_rows"], 2024)
    totals_2025 = annual_totals(direct["quarterly_rows"], 2025)
    q4_2024 = quarter_value(direct["quarterly_rows"], 2024, "Q4")
    q4_2025 = quarter_value(direct["quarterly_rows"], 2025, "Q4")
    rows = []
    for entity in sorted(set(totals_2024) & set(totals_2025)):
        start = q4_2024[entity] / totals_2024[entity]["funding_m"] * 100.0
        end = q4_2025[entity] / totals_2025[entity]["funding_m"] * 100.0
        rows.append({"label": entity, "start": start, "end": end, "delta": end - start})
    rows = sort_desc(rows, "delta")[:10]
    write_output({
        "status": "complete",
        "chart_type": "slope",
        "title": "Top 10 markets by increase in Q4 concentration share",
        "y_label": "Q4 share of annual funding (%)",
        "start_label": "2024 Q4 share",
        "end_label": "2025 Q4 share",
        "data": rows,
    })

elif qk == "005_q07":
    totals = annual_totals(direct["quarterly_rows"], 2025)
    rows = []
    for entity, vals in totals.items():
        for quarter in ["Q1", "Q2", "Q3", "Q4"]:
            match = next(row for row in direct["quarterly_rows"] if row["entity"] == entity and row["year"] == 2025 and row["quarter"] == quarter)
            funding_share = to_millions(match["funding_value"], match["funding_unit"]) / vals["funding_m"] * 100.0
            deal_share = match["deals"] / vals["deals"] * 100.0
            rows.append({"label": entity, "quarter": quarter, "value": funding_share - deal_share})
    q4_gap = {row["label"]: row["value"] for row in rows if row["quarter"] == "Q4"}
    row_order = [k for k, _ in sorted(q4_gap.items(), key=lambda item: item[1], reverse=True)]
    write_output({
        "status": "complete",
        "chart_type": "heatmap",
        "title": "2025 funding share minus deal share by quarter",
        "x_label": "Quarter",
        "y_label": "Market",
        "value_label": "Share gap (pp)",
        "row_order": row_order,
        "col_order": ["Q1", "Q2", "Q3", "Q4"],
        "data": rows,
    })

elif qk == "005_q08":
    totals = annual_totals(direct["quarterly_rows"], 2025)
    deals = top_lookup(direct["top_deals_rows"])
    rows = []
    for entity, vals in totals.items():
        biggest = largest_amount(deals.get(entity, []))
        if biggest is None:
            continue
        avg = vals["funding_m"] / vals["deals"]
        rows.append({"label": entity, "value": biggest / avg})
    rows = sort_desc(rows, "value")[:10]
    write_output({
        "status": "complete",
        "chart_type": "barh",
        "title": "Top 10 markets by headline-round amplification",
        "x_label": "Largest top deal / average funding per deal (x)",
        "y_label": "Market",
        "value_format": "float2",
        "data": rows,
    })

elif qk == "005_q09":
    totals_2021 = annual_totals(direct["quarterly_rows"], 2021)
    totals_2025 = annual_totals(direct["quarterly_rows"], 2025)
    stage = stage_lookup(direct["stage_rows"])
    rows = []
    for entity in sorted(set(totals_2021) & set(totals_2025)):
        funding_cagr = cagr(totals_2021[entity]["funding_m"], totals_2025[entity]["funding_m"], 4)
        deal_cagr = cagr(totals_2021[entity]["deals"], totals_2025[entity]["deals"], 4)
        if funding_cagr is None or deal_cagr is None:
            continue
        rows.append({
            "label": entity,
            "x": funding_cagr,
            "y": deal_cagr,
            "hue": stage[entity]["late_pct"],
            "abs_funding_cagr": abs(funding_cagr),
        })
    label_entities = [row["label"] for row in sort_desc(rows, "abs_funding_cagr")[:8]]
    write_output({
        "status": "complete",
        "chart_type": "scatter",
        "title": "Funding CAGR vs deal CAGR, 2021-2025",
        "x_label": "Annual funding CAGR (%)",
        "y_label": "Annual deal-count CAGR (%)",
        "hue_label": "Late-stage share in 2025 (%)",
        "label_entities": label_entities,
        "data": rows,
    })

elif qk == "005_q10":
    totals = annual_totals(direct["quarterly_rows"], 2025)
    stage = stage_lookup(direct["stage_rows"])
    deals = top_lookup(direct["top_deals_rows"])
    ranked = sorted(totals.items(), key=lambda item: item[1]["funding_m"], reverse=True)[:12]
    rows = []
    for entity, vals in ranked:
        rows.append({
            "label": entity,
            "x": stage[entity]["early_pct"] - stage[entity]["late_pct"],
            "y": top_sum(deals.get(entity, []), 5) / vals["funding_m"] * 100.0,
            "size": vals["deals"],
        })
    write_output({
        "status": "complete",
        "chart_type": "bubble",
        "title": "Top-12 markets by 2025 funding: stage skew vs concentration",
        "x_label": "Early-stage share minus late-stage share (pp)",
        "y_label": "Top-5 deal concentration share (%)",
        "size_label": "Annual deal count",
        "data": rows,
    })

elif qk == "006_q01":
    totals = annual_totals(direct["quarterly_rows"], 2025)
    rows = [{"label": entity, "value": vals["funding_m"] / vals["deals"]} for entity, vals in totals.items()]
    rows = sort_desc(rows, "value")[:12]
    write_output({
        "status": "complete",
        "chart_type": "barh",
        "title": "Top 12 venture markets by 2025 average funding per deal",
        "x_label": "Average funding per deal ($M)",
        "y_label": "Market",
        "value_format": "float2",
        "data": rows,
    })

elif qk == "006_q02":
    totals = annual_totals(direct["quarterly_rows"], 2025)
    stage = stage_lookup(direct["stage_rows"])
    deals = top_lookup(direct["top_deals_rows"])
    rows = []
    for entity, vals in totals.items():
        rows.append({
            "label": entity,
            "x": top_sum(deals.get(entity, [])) / vals["funding_m"] * 100.0,
            "y": stage[entity]["late_pct"],
            "size": vals["funding_m"] / 1000.0,
        })
    rows = sort_desc(rows, "x")
    write_output({
        "status": "complete",
        "chart_type": "bubble",
        "title": "Sector Spotlights: concentration vs late-stage share",
        "x_label": "Visible top-deal concentration share of annual funding (%)",
        "y_label": "Late-stage share in 2025 (%)",
        "size_label": "Annual funding ($B)",
        "data": rows,
    })

elif qk == "006_q03":
    totals_2024 = annual_totals(direct["quarterly_rows"], 2024)
    totals_2025 = annual_totals(direct["quarterly_rows"], 2025)
    rows = []
    for entity in sorted(set(totals_2024) & set(totals_2025)):
        funding_growth = (totals_2025[entity]["funding_m"] / totals_2024[entity]["funding_m"] - 1) * 100.0
        deal_growth = (totals_2025[entity]["deals"] / totals_2024[entity]["deals"] - 1) * 100.0
        rows.append({"label": entity, "left": funding_growth, "right": deal_growth, "abs_gap": abs(funding_growth - deal_growth)})
    rows = sort_desc(rows, "abs_gap")[:10]
    write_output({
        "status": "complete",
        "chart_type": "dumbbell",
        "title": "Top 10 venture markets by growth divergence, 2024-2025",
        "x_label": "Growth rate (%)",
        "left_label": "Funding growth",
        "right_label": "Deal growth",
        "data": rows,
    })

elif qk == "006_q04":
    totals = annual_totals(direct["quarterly_rows"], 2025)
    size_rows = direct["size_rows"]
    size_lookup = {row["entity"]: row for row in size_rows if row["year"] == 2025}
    deals = top_lookup(direct["top_deals_rows"])
    rows = []
    for entity, vals in totals.items():
        rows.append({
            "label": entity,
            "x": size_lookup[entity]["average_value"],
            "y": size_lookup[entity]["median_value"],
            "size": top_sum(deals.get(entity, [])) / vals["funding_m"] * 100.0,
        })
    write_output({
        "status": "complete",
        "chart_type": "bubble",
        "title": "Sector Spotlights: average vs median deal size with concentration",
        "x_label": "Average deal size in 2025 ($M)",
        "y_label": "Median deal size in 2025 ($M)",
        "size_label": "Visible top-deal concentration share (%)",
        "data": rows,
    })

elif qk == "006_q05":
    write_output({
        "status": "incomplete",
        "chart_type": "incomplete",
        "title": "Parent-child funding share ranking",
        "note": direct["params"]["incomplete_reason"],
        "data": [],
    })

elif qk == "006_q06":
    rows = []
    size_lookup = defaultdict(dict)
    for row in direct["size_rows"]:
        size_lookup[row["entity"]][row["year"]] = row
    for entity, by_year in size_lookup.items():
        if 2024 not in by_year or 2025 not in by_year:
            continue
        rows.append({
            "label": entity,
            "start": by_year[2024]["average_value"],
            "end": by_year[2025]["average_value"],
        })
    rows = sorted(rows, key=lambda row: row["end"], reverse=True)
    write_output({
        "status": "complete",
        "chart_type": "slope",
        "title": "Sector Spotlights: average deal size from 2024 to 2025",
        "y_label": "Average deal size ($M)",
        "start_label": "2024 average",
        "end_label": "2025 average",
        "data": rows,
    })

elif qk == "006_q07":
    totals = annual_totals(direct["quarterly_rows"], 2025)
    stage = stage_lookup(direct["stage_rows"])
    deals = top_lookup(direct["top_deals_rows"])
    ranked = sorted(totals.items(), key=lambda item: item[1]["funding_m"], reverse=True)[:15]
    rows = []
    for entity, vals in ranked:
        avg = vals["funding_m"] / vals["deals"]
        biggest = largest_amount(deals.get(entity, []))
        if biggest is None:
            continue
        rows.append({
            "label": entity,
            "x": stage[entity]["early_pct"] - stage[entity]["late_pct"],
            "y": biggest / avg,
            "size": vals["deals"],
        })
    write_output({
        "status": "complete",
        "chart_type": "bubble",
        "title": "Top-15 markets: stage gap vs headline-round amplification",
        "x_label": "Early-stage share minus late-stage share (pp)",
        "y_label": "Largest top deal / average deal size (x)",
        "size_label": "Annual deal count",
        "data": rows,
    })

elif qk == "006_q08":
    totals = annual_totals(direct["quarterly_rows"], 2025)
    rows = []
    for entity, vals in totals.items():
        for quarter in ["Q1", "Q2", "Q3", "Q4"]:
            match = next(row for row in direct["quarterly_rows"] if row["entity"] == entity and row["year"] == 2025 and row["quarter"] == quarter)
            funding_share = to_millions(match["funding_value"], match["funding_unit"]) / vals["funding_m"] * 100.0
            deal_share = match["deals"] / vals["deals"] * 100.0
            rows.append({"label": entity, "quarter": quarter, "value": funding_share - deal_share})
    q4_gap = {row["label"]: row["value"] for row in rows if row["quarter"] == "Q4"}
    row_order = [k for k, _ in sorted(q4_gap.items(), key=lambda item: item[1], reverse=True)]
    write_output({
        "status": "complete",
        "chart_type": "heatmap",
        "title": "2025 venture-market funding share minus deal share by quarter",
        "x_label": "Quarter",
        "y_label": "Market",
        "value_label": "Share gap (pp)",
        "row_order": row_order,
        "col_order": ["Q1", "Q2", "Q3", "Q4"],
        "data": rows,
    })

elif qk == "006_q09":
    totals = annual_totals(direct["quarterly_rows"], 2025)
    deals = top_lookup(direct["top_deals_rows"])
    rows = []
    for entity, vals in totals.items():
        concentration = top_sum(deals.get(entity, [])) / vals["funding_m"] * 100.0
        rows.append({"label": entity, "value": concentration})
    rows = sort_desc(rows, "value")[:10]
    write_output({
        "status": "complete",
        "chart_type": "lollipop",
        "title": "Top 10 markets by visible top-deal concentration share",
        "x_label": "Visible top-deal concentration share (%)",
        "y_label": "Market",
        "value_format": "float2",
        "data": rows,
    })

elif qk == "006_q10":
    totals = annual_totals(direct["quarterly_rows"], 2025)
    deals = top_lookup(direct["top_deals_rows"])
    rows = []
    for entity, vals in totals.items():
        top_rows = deals.get(entity, [])
        if direct["params"].get("require_complete_top_coverage"):
            if any(row["amount_value"] is None or row["amount_unit"] is None for row in top_rows):
                continue
        rows.append({
            "label": entity,
            "x": vals["funding_m"] / vals["deals"],
            "y": top_sum(top_rows) / vals["funding_m"] * 100.0,
            "size": vals["funding_m"] / 1000.0,
            "hue": direct["params"]["entity_type_label"],
        })
    extra_rows = []
    for entity, vals in annual_totals(direct["extra_quarterly_rows"], 2025).items():
        top_rows = [row for row in direct["extra_top_deals_rows"] if row["entity"] == entity]
        extra_rows.append({
            "label": entity,
            "x": vals["funding_m"] / vals["deals"],
            "y": top_sum(top_rows) / vals["funding_m"] * 100.0,
            "size": vals["funding_m"] / 1000.0,
            "hue": "Sector",
        })
    all_rows = rows + extra_rows
    label_entities = [row["label"] for row in sorted(all_rows, key=lambda row: row["size"], reverse=True)[:12]]
    write_output({
        "status": "complete",
        "chart_type": "bubble",
        "title": "Sectors and markets with complete stage-mix and top-deal coverage",
        "x_label": "Average funding per deal in 2025 ($M)",
        "y_label": "Visible top-deal concentration share (%)",
        "size_label": "Annual funding ($B)",
        "label_entities": label_entities,
        "data": all_rows,
    })

else:
    write_output({"status": "incomplete", "chart_type": "incomplete", "title": qk, "note": "Unsupported query key", "data": []})
