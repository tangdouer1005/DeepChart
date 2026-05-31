
import json
from pathlib import Path

import pandas as pd


def to_frame(records):
    return pd.DataFrame(records)


def year_totals(year_df, quarter_count):
    out = year_df[["market"]].copy()
    out["funding_m"] = year_df[[f"q{i}_funding_m" for i in range(1, quarter_count + 1)]].sum(axis=1)
    out["deals"] = year_df[[f"q{i}_deals" for i in range(1, quarter_count + 1)]].sum(axis=1)
    return out


def finalize(query_id, query_text, title, chart_kind, chart_type, value_unit, sort_rule, selection_rule, metadata, records_df, status="completed", notes=None):
    payload = {
        "query_id": query_id,
        "query_text": query_text,
        "status": status,
        "title": title,
        "chart_kind": chart_kind,
        "chart_type": chart_type,
        "value_unit": value_unit,
        "sort_rule": sort_rule,
        "selection_rule": selection_rule,
        "metadata": metadata,
        "records": [] if records_df is None else records_df.to_dict(orient="records"),
    }
    if notes:
        payload["notes"] = notes
    Path("final_chart_data.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2))


data = json.loads(Path("direct_data.json").read_text())
query_id = data["query_id"]
query_text = data["query_text"]
yearly = {year: to_frame(rows) for year, rows in data["years"].items()}
stage = to_frame(data["stage_shares"])
top_deals = to_frame(data["top_deals"])
totals_2025 = year_totals(yearly["2025"], 3)
totals_2024_q3 = year_totals(yearly["2024"], 3)
annual_avgs = {}
for year in ["2021", "2022", "2023", "2024"]:
    totals = year_totals(yearly[year], 4)
    annual_avgs[year] = totals.assign(avg_funding_per_deal_m=totals["funding_m"] / totals["deals"])
annual_avgs["2025 YTD"] = totals_2025.assign(avg_funding_per_deal_m=totals_2025["funding_m"] / totals_2025["deals"])
top5 = (
    top_deals[top_deals["visible_order"] <= 5]
    .groupby("market", as_index=False)["amount_m"]
    .sum()
    .rename(columns={"amount_m": "top5_visible_amount_m"})
)
largest = top_deals.groupby("market", as_index=False)["amount_m"].max().rename(columns={"amount_m": "largest_visible_deal_m"})

if query_id == "query_01":
    out = totals_2025.copy()
    out["avg_funding_per_deal_m"] = out["funding_m"] / out["deals"]
    out = out[out["deals"] >= 50].sort_values(["avg_funding_per_deal_m", "market"], ascending=[False, True]).head(12)
    finalize(
        query_id,
        query_text,
        "Top 12 markets by 2025 YTD average funding per deal",
        "horizontal_bar",
        "ranked bar chart",
        "$M per deal",
        "descending by avg_funding_per_deal_m",
        "top 12 with at least 50 total deals in 2025 YTD",
        {"entity_field": "market", "value_field": "avg_funding_per_deal_m", "figsize": [12, 8]},
        out[["market", "avg_funding_per_deal_m", "funding_m", "deals"]],
    )
elif query_id == "query_02":
    out = totals_2025.merge(top5, on="market", how="left")
    out["top5_visible_amount_m"] = out["top5_visible_amount_m"].fillna(0)
    out["concentration_share_pct"] = out["top5_visible_amount_m"] * 100.0 / out["funding_m"]
    out["avg_funding_per_deal_m"] = out["funding_m"] / out["deals"]
    out["funding_b"] = out["funding_m"] / 1000.0
    label_names = set(out.sort_values(["concentration_share_pct", "market"], ascending=[False, True]).head(10)["market"])
    out["label"] = out["market"].where(out["market"].isin(label_names), "")
    out = out.sort_values(["concentration_share_pct", "market"], ascending=[False, True])
    finalize(
        query_id,
        query_text,
        "Top-deal concentration vs average funding per deal",
        "bubble",
        "bubble chart",
        "x: concentration share %; y: $M per deal; bubble size: $B",
        "descending by concentration_share_pct for labels",
        "all markets; labels top 10 by concentration share",
        {
            "x_field": "concentration_share_pct",
            "y_field": "avg_funding_per_deal_m",
            "size_field": "funding_b",
            "label_field": "label",
            "figsize": [12, 8],
        },
        out[["market", "concentration_share_pct", "avg_funding_per_deal_m", "funding_b", "label", "deals"]],
    )
elif query_id == "query_03":
    out = totals_2024_q3.merge(totals_2025, on="market", suffixes=("_2024", "_2025"))
    out["avg_2024_m_per_deal"] = out["funding_m_2024"] / out["deals_2024"]
    out["avg_2025_m_per_deal"] = out["funding_m_2025"] / out["deals_2025"]
    out = out[out["deals_2025"] >= 40].sort_values(["avg_2025_m_per_deal", "market"], ascending=[False, True])
    finalize(
        query_id,
        query_text,
        "2024 Q1-Q3 vs 2025 Q1-Q3 average funding per deal",
        "slope",
        "slope chart",
        "$M per deal",
        "descending by avg_2025_m_per_deal",
        "complete data in both periods and at least 40 deals in 2025 Q1-Q3",
        {
            "entity_field": "market",
            "left_field": "avg_2024_m_per_deal",
            "right_field": "avg_2025_m_per_deal",
            "left_label": "2024 Q1-Q3",
            "right_label": "2025 Q1-Q3",
            "figsize": [12, 8],
        },
        out[["market", "avg_2024_m_per_deal", "avg_2025_m_per_deal", "deals_2025"]],
    )
elif query_id == "query_04":
    out = totals_2025.merge(top5, on="market", how="left").merge(stage[["market", "late_stage_pct"]], on="market", how="left")
    out["top5_visible_amount_m"] = out["top5_visible_amount_m"].fillna(0)
    out["concentration_share_pct"] = out["top5_visible_amount_m"] * 100.0 / out["funding_m"]
    out["stage_capital_mismatch_pp"] = out["concentration_share_pct"] - out["late_stage_pct"]
    out = out.sort_values(["stage_capital_mismatch_pp", "market"], ascending=[False, True]).head(10)
    finalize(
        query_id,
        query_text,
        "Top 10 markets by stage-capital mismatch",
        "horizontal_bar",
        "ranked bar chart",
        "percentage points",
        "descending by stage_capital_mismatch_pp",
        "top 10 markets",
        {"entity_field": "market", "value_field": "stage_capital_mismatch_pp", "figsize": [12, 8]},
        out[["market", "stage_capital_mismatch_pp", "concentration_share_pct", "late_stage_pct"]],
    )
elif query_id == "query_05":
    out = totals_2024_q3.merge(totals_2025, on="market", suffixes=("_2024", "_2025")).merge(stage[["market", "early_stage_pct"]], on="market", how="left")
    out["funding_growth_pct"] = (out["funding_m_2025"] - out["funding_m_2024"]) * 100.0 / out["funding_m_2024"]
    out["deal_growth_pct"] = (out["deals_2025"] - out["deals_2024"]) * 100.0 / out["deals_2024"]
    out["funding_b"] = out["funding_m_2025"] / 1000.0
    out["early_stage_bucket"] = out["early_stage_pct"].apply(lambda v: "Above 75%" if v > 75 else "75% or below")
    out = out.sort_values(["market"], ascending=[True])
    finalize(
        query_id,
        query_text,
        "Funding growth vs deal growth with early-stage classification",
        "bubble",
        "scatter plot",
        "growth rates in %",
        "market alphabetical order",
        "complete 2024 Q1-Q3 and 2025 Q1-Q3 data",
        {
            "x_field": "funding_growth_pct",
            "y_field": "deal_growth_pct",
            "size_field": "funding_b",
            "hue_field": "early_stage_bucket",
            "figsize": [12, 8],
        },
        out[["market", "funding_growth_pct", "deal_growth_pct", "funding_b", "early_stage_bucket"]],
    )
elif query_id == "query_06":
    us_children = ["Silicon Valley", "New York", "Los Angeles", "Boston", "Seattle", "Austin", "Miami", "Philadelphia"]
    us = totals_2025[totals_2025["market"] == "US"].iloc[0]
    out = totals_2025[totals_2025["market"].isin(us_children)].copy()
    out["funding_share_pct"] = out["funding_m"] * 100.0 / us["funding_m"]
    out["deal_share_pct"] = out["deals"] * 100.0 / us["deals"]
    out["share_gap_pct"] = out["funding_share_pct"] - out["deal_share_pct"]
    out = out.sort_values(["share_gap_pct", "market"], ascending=[False, True])
    finalize(
        query_id,
        query_text,
        "US child-market share of funding vs share of deals",
        "dumbbell",
        "dumbbell chart",
        "percent of US total",
        "descending by funding_share_pct minus deal_share_pct",
        "US ecosystems only",
        {
            "entity_field": "market",
            "left_field": "funding_share_pct",
            "right_field": "deal_share_pct",
            "left_label": "Share of US funding",
            "right_label": "Share of US deals",
            "figsize": [12, 7],
        },
        out[["market", "funding_share_pct", "deal_share_pct", "share_gap_pct"]],
    )
elif query_id == "query_07":
    out = totals_2025.merge(largest, on="market", how="left")
    out["avg_funding_per_deal_m"] = out["funding_m"] / out["deals"]
    out["headline_round_amplification"] = out["largest_visible_deal_m"] / out["avg_funding_per_deal_m"]
    out = out[out["deals"] >= 20].sort_values(["headline_round_amplification", "market"], ascending=[False, True]).head(10)
    finalize(
        query_id,
        query_text,
        "Top 10 markets by headline-round amplification",
        "horizontal_bar",
        "ranked bar chart",
        "multiple",
        "descending by headline_round_amplification",
        "top 10 with at least 20 deals in 2025 YTD",
        {"entity_field": "market", "value_field": "headline_round_amplification", "figsize": [12, 8]},
        out[["market", "headline_round_amplification", "largest_visible_deal_m", "avg_funding_per_deal_m"]],
    )
elif query_id == "query_08":
    markets = annual_avgs["2021"]["market"].tolist()
    rows = []
    for market in markets:
        values = {}
        for period, frame in annual_avgs.items():
            match = frame[frame["market"] == market]
            values[period] = float(match.iloc[0]["avg_funding_per_deal_m"])
        rows.append(
            {
                "market": market,
                "2021→2022": values["2022"] - values["2021"],
                "2022→2023": values["2023"] - values["2022"],
                "2023→2024": values["2024"] - values["2023"],
                "2024→2025 YTD": values["2025 YTD"] - values["2024"],
            }
        )
    out = pd.DataFrame(rows)
    out["swing_abs"] = out["2024→2025 YTD"].abs()
    out = out.sort_values(["swing_abs", "market"], ascending=[False, True]).head(15)
    long = out.melt(id_vars=["market", "swing_abs"], value_vars=["2021→2022", "2022→2023", "2023→2024", "2024→2025 YTD"], var_name="transition", value_name="delta_m_per_deal")
    finalize(
        query_id,
        query_text,
        "Adjacent-period changes in average funding per deal",
        "heatmap",
        "heatmap",
        "$M per deal",
        "top 15 by absolute 2024→2025 YTD swing",
        "markets limited to largest absolute final swing",
        {
            "row_field": "market",
            "col_field": "transition",
            "value_field": "delta_m_per_deal",
            "col_order": ["2021→2022", "2022→2023", "2023→2024", "2024→2025 YTD"],
            "row_order": out["market"].tolist(),
            "figsize": [12, 8],
        },
        long[["market", "transition", "delta_m_per_deal"]],
    )
elif query_id == "query_09":
    out = totals_2025.merge(top5, on="market", how="left").merge(stage[["market", "early_stage_pct", "late_stage_pct"]], on="market", how="left")
    out["top5_visible_amount_m"] = out["top5_visible_amount_m"].fillna(0)
    out["concentration_share_pct"] = out["top5_visible_amount_m"] * 100.0 / out["funding_m"]
    out["early_minus_late_pp"] = out["early_stage_pct"] - out["late_stage_pct"]
    out["label"] = out["market"].where(out["concentration_share_pct"] > 40, "")
    out = out.sort_values(["concentration_share_pct", "market"], ascending=[False, True])
    finalize(
        query_id,
        query_text,
        "Top-5 deal concentration vs early-minus-late stage spread",
        "bubble",
        "bubble chart",
        "x: concentration share %; y: percentage points; bubble size: deal count",
        "descending by concentration_share_pct",
        "all markets; labels only where concentration_share_pct > 40",
        {
            "x_field": "concentration_share_pct",
            "y_field": "early_minus_late_pp",
            "size_field": "deals",
            "label_field": "label",
            "figsize": [12, 8],
        },
        out[["market", "concentration_share_pct", "early_minus_late_pp", "deals", "label"]],
    )
elif query_id == "query_10":
    out = totals_2025.copy()
    global_funding = out["funding_m"].sum()
    global_deals = out["deals"].sum()
    out["funding_share_pct"] = out["funding_m"] * 100.0 / global_funding
    out["deal_share_pct"] = out["deals"] * 100.0 / global_deals
    out["share_gap_pct"] = out["funding_share_pct"] - out["deal_share_pct"]
    out = out.sort_values(["share_gap_pct", "market"], ascending=[False, True]).head(10)
    finalize(
        query_id,
        query_text,
        "Top 10 markets by funding-share minus deal-share gap",
        "horizontal_bar",
        "horizontal bar chart",
        "percentage points",
        "descending by share_gap_pct",
        "top 10 from co-reported 2025 Q1-Q3 market rows",
        {"entity_field": "market", "value_field": "share_gap_pct", "figsize": [12, 8]},
        out[["market", "share_gap_pct", "funding_share_pct", "deal_share_pct"]],
    )
else:
    finalize(query_id, query_text, "Incomplete query", "none", "none", "", "", "", {}, None, status="incomplete", notes="Unknown query id")
