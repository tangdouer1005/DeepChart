
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


sns.set_theme(style="whitegrid")
final = json.loads(Path("final_chart_data.json").read_text())
records = final.get("records", [])
meta = final.get("metadata", {})
chart_kind = final.get("chart_kind")
title = final.get("title", final.get("query_id", "chart"))
out_path = Path("chart.png")

if final.get("status") != "completed" or not records:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.text(0.5, 0.5, "Incomplete query", ha="center", va="center")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    raise SystemExit(0)

df = pd.DataFrame(records)
fig, ax = plt.subplots(figsize=tuple(meta.get("figsize", [10, 6])))

def annotate(frame, x_field, y_field, label_field):
    for _, row in frame.iterrows():
        label = row.get(label_field, "")
        if isinstance(label, str) and label:
            ax.text(row[x_field], row[y_field], " " + label, fontsize=8, va="center")

if chart_kind == "horizontal_bar":
    sns.barplot(data=df, x=meta["value_field"], y=meta["entity_field"], ax=ax)
    ax.set_xlabel(final.get("value_unit", "value"))
    ax.set_ylabel("")
elif chart_kind in {"bubble", "scatter"}:
    kwargs = {"data": df, "x": meta["x_field"], "y": meta["y_field"], "ax": ax}
    if meta.get("hue_field"):
        kwargs["hue"] = meta["hue_field"]
    if meta.get("size_field"):
        kwargs["size"] = meta["size_field"]
        kwargs["sizes"] = (60, 900)
    sns.scatterplot(**kwargs)
    if meta.get("label_field"):
        annotate(df, meta["x_field"], meta["y_field"], meta["label_field"])
    if ax.get_legend() is not None:
        ax.legend(loc="best", fontsize=8)
elif chart_kind in {"dumbbell", "slope"}:
    left_color, right_color = sns.color_palette("Set2", 2)
    y_labels = list(df[meta["entity_field"]])
    y_positions = list(range(len(y_labels)))
    for y, (_, row) in zip(y_positions, df.iterrows()):
        ax.plot([row[meta["left_field"]], row[meta["right_field"]]], [y, y], color="gray", linewidth=1.5)
        ax.scatter(row[meta["left_field"]], y, color=left_color, s=60, label=meta.get("left_label") if y == 0 else None)
        ax.scatter(row[meta["right_field"]], y, color=right_color, s=60, label=meta.get("right_label") if y == 0 else None)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(y_labels)
    ax.legend(loc="best")
elif chart_kind == "heatmap":
    pivot = df.pivot(index=meta["row_field"], columns=meta["col_field"], values=meta["value_field"])
    if meta.get("row_order"):
        pivot = pivot.reindex(meta["row_order"])
    if meta.get("col_order"):
        pivot = pivot[[col for col in meta["col_order"] if col in pivot.columns]]
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="coolwarm", center=0, ax=ax)
else:
    ax.text(0.5, 0.5, f"Unsupported chart kind: {chart_kind}", ha="center", va="center")
    ax.axis("off")

ax.set_title(title)
fig.tight_layout()
fig.savefig(out_path, dpi=200, bbox_inches="tight")
