
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parent
payload = json.loads((ROOT / "final_chart_data.json").read_text(encoding="utf-8"))
out_path = ROOT / "chart.png"

sns.set_theme(style="whitegrid")

if payload["status"] != "complete" or payload["chart_type"] == "incomplete":
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis("off")
    ax.text(0.5, 0.5, payload.get("note", "Incomplete query"), ha="center", va="center", wrap=True)
    ax.set_title(payload.get("title", "Incomplete"))
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    raise SystemExit(0)

chart_type = payload["chart_type"]
rows = payload["data"]
df = pd.DataFrame(rows)

if chart_type == "barh":
    fig, ax = plt.subplots(figsize=(11, max(4, len(df) * 0.45)))
    sns.barplot(data=df, x="value", y="label", ax=ax, color="#4C7E9E")
    ax.set_title(payload["title"])
    ax.set_xlabel(payload["x_label"])
    ax.set_ylabel(payload["y_label"])
    fig.tight_layout()

elif chart_type in {"bubble", "scatter"}:
    fig, ax = plt.subplots(figsize=(11, 7))
    kwargs = {"data": df, "x": "x", "y": "y", "ax": ax}
    if "size" in df.columns:
        kwargs["size"] = "size"
        kwargs["sizes"] = (60, 1000)
    if "hue" in df.columns:
        kwargs["hue"] = "hue"
        kwargs["palette"] = "viridis"
    sns.scatterplot(**kwargs)
    labels = payload.get("label_entities") or df["label"].tolist()
    for _, row in df[df["label"].isin(labels)].iterrows():
        ax.text(row["x"], row["y"], f" {row['label']}", fontsize=8)
    ax.set_title(payload["title"])
    ax.set_xlabel(payload["x_label"])
    ax.set_ylabel(payload["y_label"])
    fig.tight_layout()

elif chart_type == "dumbbell":
    df = df.sort_values("left")
    fig, ax = plt.subplots(figsize=(11, max(4, len(df) * 0.5)))
    y_positions = range(len(df))
    for y, (_, row) in zip(y_positions, df.iterrows()):
        ax.plot([row["left"], row["right"]], [y, y], color="#999999", linewidth=2)
        ax.scatter(row["left"], y, color="#1f77b4", s=50)
        ax.scatter(row["right"], y, color="#d62728", s=50)
    ax.set_yticks(list(y_positions))
    ax.set_yticklabels(df["label"].tolist())
    ax.set_xlabel(payload["x_label"])
    ax.set_title(payload["title"])
    fig.tight_layout()

elif chart_type == "slope":
    fig, ax = plt.subplots(figsize=(10, max(4, len(df) * 0.45)))
    for _, row in df.iterrows():
        ax.plot([0, 1], [row["start"], row["end"]], marker="o")
        ax.text(0, row["start"], f" {row['label']}", va="center", fontsize=8)
    ax.set_xticks([0, 1])
    ax.set_xticklabels([payload["start_label"], payload["end_label"]])
    ax.set_ylabel(payload["y_label"])
    ax.set_title(payload["title"])
    fig.tight_layout()

elif chart_type == "heatmap":
    pivot = df.pivot(index="label", columns="quarter", values="value")
    pivot = pivot.reindex(index=payload["row_order"], columns=payload["col_order"])
    fig, ax = plt.subplots(figsize=(11, max(6, len(pivot) * 0.35)))
    sns.heatmap(pivot, cmap="coolwarm", center=0, ax=ax)
    ax.set_title(payload["title"])
    ax.set_xlabel(payload["x_label"])
    ax.set_ylabel(payload["y_label"])
    fig.tight_layout()

elif chart_type == "lollipop":
    df = df.sort_values("value")
    fig, ax = plt.subplots(figsize=(11, max(4, len(df) * 0.45)))
    y_positions = range(len(df))
    ax.hlines(y=y_positions, xmin=0, xmax=df["value"], color="#9aa5b1")
    ax.scatter(df["value"], y_positions, color="#2b6cb0", s=60)
    ax.set_yticks(list(y_positions))
    ax.set_yticklabels(df["label"].tolist())
    ax.set_xlabel(payload["x_label"])
    ax.set_title(payload["title"])
    fig.tight_layout()

else:
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis("off")
    ax.text(0.5, 0.5, f"Unsupported chart type: {chart_type}", ha="center", va="center")
    ax.set_title(payload.get("title", "Unsupported chart"))
    fig.tight_layout()

fig.savefig(out_path, dpi=150)
