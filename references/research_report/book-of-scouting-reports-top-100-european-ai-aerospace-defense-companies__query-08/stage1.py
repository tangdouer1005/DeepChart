
import json
from pathlib import Path

import numpy as np
import pandas as pd


def is_series_c_plus(stage_text):
    return any(
        token in stage_text
        for token in [
            "series c",
            "series d",
            "series e",
            "series f",
            "series g",
            "series h",
            "series i",
            "series j",
            "series k",
        ]
    )


def stage_family(stage):
    if stage is None:
        return "Debt/Loan/Grant/Corporate/Other"
    stage_text = str(stage).lower()
    if "pre-seed" in stage_text or "seed" in stage_text:
        return "Seed/Pre-Seed"
    if "series a" in stage_text or "series b" in stage_text:
        return "Series A-B"
    if is_series_c_plus(stage_text):
        return "Series C+"
    return "Debt/Loan/Grant/Corporate/Other"


def stable_rank(frame, value_col):
    ordered = frame.sort_values([value_col, "entity"], ascending=[False, True]).reset_index(drop=True)
    ordered["rank"] = range(1, len(ordered) + 1)
    return ordered[["entity", "rank"]]


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
df = pd.DataFrame(data["companies"])
segment_order = ["Aerospace (commercial)", "Aerospace (dual-use)", "Defense"]

if query_id == "query_01":
    work = df[df["mosaic"].notna() & df["total_raised_m"].notna() & (df["total_raised_m"] >= 10)].copy()
    work["mosaic_per_10m"] = work["mosaic"] * 10.0 / work["total_raised_m"]
    work = work.sort_values(["mosaic_per_10m", "entity"], ascending=[False, True]).head(15)
    finalize(
        query_id,
        query_text,
        "Top 15 companies by Mosaic per $10M raised",
        "horizontal_bar",
        "horizontal bar chart",
        "Mosaic points per $10M",
        "descending by mosaic_per_10m",
        "top 15 with total_raised_m >= 10",
        {"entity_field": "entity", "value_field": "mosaic_per_10m", "hue_field": "segment", "figsize": [12, 8]},
        work[["entity", "segment", "mosaic_per_10m", "mosaic", "total_raised_m"]],
    )
elif query_id == "query_02":
    work = df[df["commercial_maturity"].notna() & df["mosaic"].notna() & df["total_raised_m"].notna()].copy()
    work["maturity_norm"] = work["commercial_maturity"] / 5.0
    work["mosaic_norm"] = work["mosaic"] / 1000.0
    work["mosaic_pct_rank"] = work["mosaic"].rank(method="average", pct=True)
    work["raised_pct_rank"] = work["total_raised_m"].rank(method="average", pct=True)
    work["rank_gap"] = work["mosaic_pct_rank"] - work["raised_pct_rank"]
    label_names = set(
        work[work["rank_gap"] > 0]
        .sort_values(["rank_gap", "entity"], ascending=[False, True])
        .head(12)["entity"]
    )
    work["label"] = work["entity"].where(work["entity"].isin(label_names), "")
    work = work.sort_values(["rank_gap", "entity"], ascending=[False, True])
    finalize(
        query_id,
        query_text,
        "Commercial maturity vs Mosaic with overperformer labels",
        "bubble",
        "bubble chart",
        "x: maturity share of 5; y: Mosaic share of 1000; bubble size: $M",
        "descending by rank_gap for labels",
        "all companies with non-missing maturity, mosaic, and total_raised_m; labels top 12 positive rank gaps",
        {
            "x_field": "maturity_norm",
            "y_field": "mosaic_norm",
            "size_field": "total_raised_m",
            "hue_field": "segment",
            "label_field": "label",
            "figsize": [12, 8],
        },
        work[["entity", "segment", "maturity_norm", "mosaic_norm", "total_raised_m", "rank_gap", "label"]],
    )
elif query_id == "query_03":
    work = df[df["mosaic"].notna() & df["total_raised_m"].notna()].copy()
    mosaic_ranks = []
    raised_ranks = []
    for segment, group in work.groupby("segment", sort=False):
        mr = stable_rank(group[["entity", "mosaic"]].copy(), "mosaic")
        mr["segment"] = segment
        rr = stable_rank(group[["entity", "total_raised_m"]].copy(), "total_raised_m")
        rr["segment"] = segment
        mosaic_ranks.append(mr)
        raised_ranks.append(rr)
    mr = pd.concat(mosaic_ranks).rename(columns={"rank": "mosaic_rank"})
    rr = pd.concat(raised_ranks).rename(columns={"rank": "total_raised_rank"})
    work = work.merge(mr, on=["entity", "segment"]).merge(rr, on=["entity", "segment"])
    work["abs_rank_gap"] = (work["mosaic_rank"] - work["total_raised_rank"]).abs()
    work = work.sort_values(["abs_rank_gap", "entity"], ascending=[False, True]).head(12)
    finalize(
        query_id,
        query_text,
        "Within-segment Mosaic rank vs Total raised rank gaps",
        "dumbbell",
        "dumbbell chart",
        "rank positions",
        "descending by absolute rank gap",
        "top 12 by within-segment absolute rank gap",
        {
            "entity_field": "entity",
            "left_field": "mosaic_rank",
            "right_field": "total_raised_rank",
            "left_label": "Segment Mosaic rank",
            "right_label": "Segment Total raised rank",
            "figsize": [12, 8],
        },
        work[["entity", "segment", "mosaic_rank", "total_raised_rank", "abs_rank_gap"]],
    )
elif query_id == "query_04":
    work = df[df["founded_year"].notna()].copy()
    work["cohort"] = work["founded_year"].apply(lambda y: "Founded before 2015" if y < 2015 else ("2015-2019" if y <= 2019 else "2020 or later"))
    counts = work.groupby(["segment", "cohort"]).size().rename("company_count").reset_index()
    totals = work.groupby("segment").size().rename("segment_total").reset_index()
    out = counts.merge(totals, on="segment")
    out["share_pct"] = out["company_count"] * 100.0 / out["segment_total"]
    cohort_order = ["Founded before 2015", "2015-2019", "2020 or later"]
    out["segment"] = pd.Categorical(out["segment"], categories=segment_order, ordered=True)
    out["cohort"] = pd.Categorical(out["cohort"], categories=cohort_order, ordered=True)
    out = out.sort_values(["segment", "cohort"])
    finalize(
        query_id,
        query_text,
        "Founder cohort shares by segment",
        "stacked_bar",
        "stacked bar chart",
        "percent of companies within segment",
        "segment order preserved",
        "exclude missing founded_year",
        {
            "x_field": "segment",
            "stack_field": "cohort",
            "value_field": "share_pct",
            "stack_order": cohort_order,
            "figsize": [10, 7],
        },
        out[["segment", "cohort", "company_count", "segment_total", "share_pct"]],
    )
elif query_id == "query_05":
    work = df[
        (df["founded_year"].notna())
        & (df["founded_year"] >= 2020)
        & df["total_raised_m"].notna()
        & df["headcount"].notna()
        & df["mosaic"].notna()
    ].copy()
    work["raised_per_employee_m"] = work["total_raised_m"] / work["headcount"]
    label_names = set(
        work.sort_values(["raised_per_employee_m", "entity"], ascending=[False, True]).head(10)["entity"]
    )
    work["label"] = work["entity"].where(work["entity"].isin(label_names), "")
    work = work.sort_values(["raised_per_employee_m", "entity"], ascending=[False, True])
    finalize(
        query_id,
        query_text,
        "Young companies by capital intensity and Mosaic",
        "scatter",
        "scatter plot",
        "$M per employee",
        "descending by raised_per_employee_m for labels",
        "founded in 2020 or later; labels top 10 by raised_per_employee_m",
        {
            "x_field": "raised_per_employee_m",
            "y_field": "mosaic",
            "hue_field": "segment",
            "label_field": "label",
            "figsize": [12, 8],
        },
        work[["entity", "segment", "raised_per_employee_m", "mosaic", "label", "total_raised_m", "headcount", "founded_year"]],
    )
elif query_id == "query_06":
    work = df[df["mosaic"].notna()].copy()
    work["stage_family"] = work["stage"].apply(stage_family)
    medians = work.groupby(["segment", "stage_family"])["mosaic"].median().rename("median_mosaic").reset_index()
    seg_medians = work.groupby("segment")["mosaic"].median().rename("segment_median_mosaic").reset_index()
    out = medians.merge(seg_medians, on="segment")
    out["delta_mosaic"] = out["median_mosaic"] - out["segment_median_mosaic"]
    stage_order = ["Seed/Pre-Seed", "Series A-B", "Series C+", "Debt/Loan/Grant/Corporate/Other"]
    out["segment"] = pd.Categorical(out["segment"], categories=segment_order, ordered=True)
    out["stage_family"] = pd.Categorical(out["stage_family"], categories=stage_order, ordered=True)
    out = out.sort_values(["segment", "stage_family"])
    finalize(
        query_id,
        query_text,
        "Median Mosaic residuals by segment and stage family",
        "heatmap",
        "heatmap",
        "Mosaic points",
        "segment and stage_family order preserved",
        "use non-missing mosaic only",
        {
            "row_field": "segment",
            "col_field": "stage_family",
            "value_field": "delta_mosaic",
            "row_order": segment_order,
            "col_order": stage_order,
            "figsize": [11, 5],
        },
        out[["segment", "stage_family", "median_mosaic", "segment_median_mosaic", "delta_mosaic"]],
    )
elif query_id == "query_07":
    work = df[
        df["commercial_maturity"].notna()
        & (df["commercial_maturity"] >= 3)
        & df["headcount"].notna()
        & df["total_raised_m"].notna()
    ].copy()
    work["funding_per_employee_m"] = work["total_raised_m"] / work["headcount"]
    work = work.sort_values(["funding_per_employee_m", "entity"], ascending=[False, True]).head(12)
    finalize(
        query_id,
        query_text,
        "Top companies by funding concentration per employee",
        "horizontal_bar",
        "ranked bar chart",
        "$M per employee",
        "descending by funding_per_employee_m",
        "top 12 with commercial_maturity >= 3 and non-missing headcount,total_raised_m",
        {"entity_field": "entity", "value_field": "funding_per_employee_m", "hue_field": "segment", "figsize": [12, 8]},
        work[["entity", "segment", "funding_per_employee_m", "commercial_maturity", "headcount", "total_raised_m"]],
    )
elif query_id == "query_08":
    work = df[df["mosaic"].notna() & df["total_raised_m"].notna()].copy()
    mosaic_cut = work["mosaic"].quantile(0.75)
    raised_cut = work["total_raised_m"].quantile(0.75)
    work["top_mosaic"] = work["mosaic"] >= mosaic_cut
    work["top_raised"] = work["total_raised_m"] >= raised_cut
    denom = work.groupby("segment").size().rename("denominator").reset_index()
    mosaic_share = work.groupby("segment")["top_mosaic"].mean().mul(100).rename("top_quartile_mosaic_share_pct").reset_index()
    raised_share = work.groupby("segment")["top_raised"].mean().mul(100).rename("top_quartile_raised_share_pct").reset_index()
    out = denom.merge(mosaic_share, on="segment").merge(raised_share, on="segment")
    out["segment"] = pd.Categorical(out["segment"], categories=segment_order, ordered=True)
    out = out.sort_values("segment")
    finalize(
        query_id,
        query_text,
        "Segment shares in top-quartile Mosaic vs Total raised",
        "slope",
        "slope chart",
        "percent of qualifying companies",
        "segment order preserved",
        "rows with non-missing mosaic and total_raised_m only",
        {
            "entity_field": "segment",
            "left_field": "top_quartile_mosaic_share_pct",
            "right_field": "top_quartile_raised_share_pct",
            "left_label": "Top-quartile Mosaic share",
            "right_label": "Top-quartile Total raised share",
            "figsize": [10, 5],
        },
        out[["segment", "denominator", "top_quartile_mosaic_share_pct", "top_quartile_raised_share_pct"]],
    )
elif query_id == "query_09":
    work = df[
        df["founded_year"].notna()
        & df["total_raised_m"].notna()
        & df["headcount"].notna()
        & df["mosaic"].notna()
    ].copy()
    work["company_age_years"] = 2026 - work["founded_year"]
    seg_med = work.groupby("segment")["mosaic"].median().rename("segment_median_mosaic").reset_index()
    work = work.merge(seg_med, on="segment")
    work["segment_mosaic_position"] = np.where(
        work["mosaic"] >= work["segment_median_mosaic"],
        "Above segment median",
        "Below segment median",
    )
    work = work.sort_values(["mosaic", "entity"], ascending=[False, True]).head(20)
    finalize(
        query_id,
        query_text,
        "Top 20 Mosaic companies by age and headcount",
        "bubble",
        "bubble chart",
        "x: years; y: employees; bubble size: $M",
        "top 20 by mosaic descending",
        "non-missing founded_year,total_raised_m,headcount,mosaic",
        {
            "x_field": "company_age_years",
            "y_field": "headcount",
            "size_field": "total_raised_m",
            "hue_field": "segment_mosaic_position",
            "label_field": "entity",
            "figsize": [12, 8],
        },
        work[["entity", "segment", "company_age_years", "headcount", "total_raised_m", "mosaic", "segment_mosaic_position"]],
    )
elif query_id == "query_10":
    work = df[df["commercial_maturity"].notna() & (df["commercial_maturity"] > 0) & df["mosaic"].notna()].copy()
    work["maturity_adjusted_mosaic"] = work["mosaic"] / work["commercial_maturity"]
    work = work.sort_values(["maturity_adjusted_mosaic", "entity"], ascending=[False, True]).head(10)
    finalize(
        query_id,
        query_text,
        "Top companies by maturity-adjusted Mosaic",
        "horizontal_bar",
        "horizontal bar chart",
        "Mosaic points per maturity point",
        "descending by maturity_adjusted_mosaic",
        "top 10 excluding missing or zero maturity",
        {
            "entity_field": "entity",
            "value_field": "maturity_adjusted_mosaic",
            "hue_field": "segment",
            "figsize": [12, 7],
        },
        work[["entity", "segment", "maturity_adjusted_mosaic", "commercial_maturity", "mosaic"]],
    )
else:
    finalize(query_id, query_text, "Incomplete query", "none", "none", "", "", "", {}, None, status="incomplete", notes="Unknown query id")
