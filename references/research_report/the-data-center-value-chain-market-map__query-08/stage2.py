from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

BASE_DIR = Path(__file__).resolve().parent
FINAL_PATH = BASE_DIR / 'final_chart_data.json'
PNG_PATH = BASE_DIR / 'chart.png'

sns.set_theme(style='whitegrid')


def load_payload():
    return json.loads(FINAL_PATH.read_text(encoding='utf-8'))


def scale_sizes(series, low=120, high=900):
    s = pd.Series(series, dtype='float64')
    if s.empty:
        return s
    if s.nunique(dropna=True) <= 1:
        return pd.Series([0.5 * (low + high)] * len(s), index=s.index)
    scaled = (s - s.min()) / (s.max() - s.min())
    return scaled * (high - low) + low


def annotate_points(ax, df, x_col='x', y_col='y'):
    if 'highlight_label' in df.columns and df['highlight_label'].any():
        to_label = df[df['highlight_label']]
    elif len(df) <= 15:
        to_label = df
    else:
        return
    for row in to_label.itertuples():
        ax.annotate(getattr(row, 'label'), (getattr(row, x_col), getattr(row, y_col)), xytext=(4, 4), textcoords='offset points', fontsize=8)


def draw_ranked_bar(payload):
    df = pd.DataFrame(payload['records'])
    fig_h = max(6, 0.35 * len(df) + 1.5)
    fig, ax = plt.subplots(figsize=(11, fig_h))
    sns.barplot(data=df, x='value', y='label', ax=ax, color=sns.color_palette('deep')[0])
    ax.set_title(payload['plot_config']['title'])
    ax.set_xlabel(payload['plot_config']['x_label'])
    ax.set_ylabel(payload['plot_config']['y_label'])
    fig.tight_layout()
    fig.savefig(PNG_PATH, dpi=200)
    plt.close(fig)


def draw_bubble(payload):
    df = pd.DataFrame(payload['records'])
    fig, ax = plt.subplots(figsize=(11, 7))
    if 'size' in df.columns:
        df['_size'] = scale_sizes(df['size'])
        sns.scatterplot(data=df, x='x', y='y', hue='color' if 'color' in df.columns else None, size='_size', sizes=(120, 900), legend='brief', ax=ax)
        # seaborn scales again; use raw plot for stable sizing
        ax.clear()
        if 'color' in df.columns:
            palette_keys = list(dict.fromkeys(df['color'].tolist()))
            palette = dict(zip(palette_keys, sns.color_palette('tab10', n_colors=len(palette_keys))))
            for key, group in df.groupby('color'):
                ax.scatter(group['x'], group['y'], s=group['_size'], label=key, alpha=0.75, color=palette[key], edgecolors='black', linewidths=0.4)
            ax.legend(title='Group', bbox_to_anchor=(1.02, 1), loc='upper left')
        else:
            ax.scatter(df['x'], df['y'], s=df['_size'], alpha=0.75, color=sns.color_palette('deep')[0], edgecolors='black', linewidths=0.4)
    else:
        sns.scatterplot(data=df, x='x', y='y', hue='color' if 'color' in df.columns else None, ax=ax, s=120)
        if 'color' in df.columns:
            ax.legend(title='Group', bbox_to_anchor=(1.02, 1), loc='upper left')
    annotate_points(ax, df)
    ax.set_title(payload['plot_config']['title'])
    ax.set_xlabel(payload['plot_config']['x_label'])
    ax.set_ylabel(payload['plot_config']['y_label'])
    fig.tight_layout()
    fig.savefig(PNG_PATH, dpi=200)
    plt.close(fig)


def draw_scatter(payload):
    df = pd.DataFrame(payload['records'])
    fig, ax = plt.subplots(figsize=(11, 7))
    sns.scatterplot(data=df, x='x', y='y', hue='color' if 'color' in df.columns else None, ax=ax, s=120)
    annotate_points(ax, df)
    ax.set_title(payload['plot_config']['title'])
    ax.set_xlabel(payload['plot_config']['x_label'])
    ax.set_ylabel(payload['plot_config']['y_label'])
    if 'color' in df.columns:
        ax.legend(title='Group', bbox_to_anchor=(1.02, 1), loc='upper left')
    fig.tight_layout()
    fig.savefig(PNG_PATH, dpi=200)
    plt.close(fig)


def draw_stacked_bar(payload):
    df = pd.DataFrame(payload['records'])
    pivot = df.pivot(index='group', columns='category', values='value').fillna(0.0)
    fig, ax = plt.subplots(figsize=(11, 7))
    colors = sns.color_palette('Set2', n_colors=len(pivot.columns))
    bottom = pd.Series([0.0] * len(pivot), index=pivot.index)
    for color, column in zip(colors, pivot.columns):
        ax.bar(pivot.index, pivot[column], bottom=bottom, label=column, color=color)
        bottom += pivot[column]
    ax.set_title(payload['plot_config']['title'])
    ax.set_xlabel(payload['plot_config']['x_label'])
    ax.set_ylabel(payload['plot_config']['y_label'])
    ax.tick_params(axis='x', rotation=20)
    ax.legend(title='Bucket', bbox_to_anchor=(1.02, 1), loc='upper left')
    fig.tight_layout()
    fig.savefig(PNG_PATH, dpi=200)
    plt.close(fig)


def draw_dumbbell(payload):
    df = pd.DataFrame(payload['records'])
    fig_h = max(6, 0.4 * len(df) + 1.5)
    fig, ax = plt.subplots(figsize=(11, fig_h))
    y_positions = range(len(df))
    for y, row in enumerate(df.itertuples()):
        ax.plot([row.left_value, row.right_value], [y, y], color='gray', linewidth=2)
        ax.scatter(row.left_value, y, color=sns.color_palette('deep')[0], s=80, zorder=3)
        ax.scatter(row.right_value, y, color=sns.color_palette('deep')[1], s=80, zorder=3)
    ax.set_yticks(list(y_positions))
    ax.set_yticklabels(df['label'])
    ax.set_xlabel(payload['plot_config'].get('x_label', payload['plot_config'].get('y_label', 'Value')))
    ax.set_title(payload['plot_config']['title'])
    left_label = payload['plot_config'].get('left_label', 'Left')
    right_label = payload['plot_config'].get('right_label', 'Right')
    ax.scatter([], [], color=sns.color_palette('deep')[0], label=left_label)
    ax.scatter([], [], color=sns.color_palette('deep')[1], label=right_label)
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
    fig.tight_layout()
    fig.savefig(PNG_PATH, dpi=200)
    plt.close(fig)


def draw_heatmap(payload):
    df = pd.DataFrame(payload['records'])
    pivot = df.pivot(index='row', columns='col', values='value')
    fig, ax = plt.subplots(figsize=(11, 7))
    sns.heatmap(pivot, annot=True, fmt='.1f', cmap='YlGnBu', linewidths=0.5, ax=ax)
    ax.set_title(payload['plot_config']['title'])
    ax.set_xlabel(payload['plot_config']['x_label'])
    ax.set_ylabel(payload['plot_config']['y_label'])
    fig.tight_layout()
    fig.savefig(PNG_PATH, dpi=200)
    plt.close(fig)


def draw_slope(payload):
    df = pd.DataFrame(payload['records'])
    fig_h = max(6, 0.4 * len(df) + 1.5)
    fig, ax = plt.subplots(figsize=(11, fig_h))
    for row in df.itertuples():
        ax.plot([0, 1], [row.left_value, row.right_value], marker='o', linewidth=2)
        ax.text(-0.02, row.left_value, row.label, ha='right', va='center', fontsize=9)
        ax.text(1.02, row.right_value, row.label, ha='left', va='center', fontsize=9)
    ax.set_xticks([0, 1])
    ax.set_xticklabels([payload['plot_config'].get('left_label', 'Left'), payload['plot_config'].get('right_label', 'Right')])
    ax.set_ylabel(payload['plot_config'].get('y_label', 'Value'))
    ax.set_title(payload['plot_config']['title'])
    fig.tight_layout()
    fig.savefig(PNG_PATH, dpi=200)
    plt.close(fig)


def main():
    payload = load_payload()
    chart_type = payload['chart_type']
    if chart_type == 'ranked_bar':
        draw_ranked_bar(payload)
    elif chart_type == 'bubble':
        draw_bubble(payload)
    elif chart_type == 'scatter':
        draw_scatter(payload)
    elif chart_type == 'stacked_bar':
        draw_stacked_bar(payload)
    elif chart_type == 'dumbbell':
        draw_dumbbell(payload)
    elif chart_type == 'heatmap':
        draw_heatmap(payload)
    elif chart_type == 'slope':
        draw_slope(payload)
    else:
        raise ValueError(f'Unsupported chart_type: {chart_type}')


if __name__ == '__main__':
    main()
