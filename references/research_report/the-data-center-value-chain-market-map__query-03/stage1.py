from __future__ import annotations
import json
import math
import re
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DIRECT_PATH = BASE_DIR / 'direct_data.json'
FINAL_PATH = BASE_DIR / 'final_chart_data.json'


def load_data():
    return json.loads(DIRECT_PATH.read_text(encoding='utf-8'))


def parse_money_to_millions(raw):
    if raw in (None, '', 'N/A'):
        return None
    m = re.match(r'^\$(\d+(?:\.\d+)?)([MB])$', str(raw).strip())
    if not m:
        return None
    value = float(m.group(1))
    unit = m.group(2)
    return value * 1000.0 if unit == 'B' else value


def parse_percentage(raw):
    if raw in (None, '', 'N/A'):
        return None
    m = re.match(r'^(\d+(?:\.\d+)?)%$', str(raw).strip())
    return float(m.group(1)) if m else None


def parse_int(raw):
    if raw in (None, '', 'N/A'):
        return None
    s = str(raw).replace(',', '').strip()
    return int(s) if re.match(r'^\d+$', s) else None


def parse_year(raw):
    if raw in (None, '', 'N/A'):
        return None
    s = str(raw).strip()
    return int(s) if re.match(r'^\d{4}$', s) else None


def parse_maturity(raw):
    if raw in (None, '', 'N/A', 'N/A / 5'):
        return None
    m = re.match(r'^(\d+)\s*/\s*5$', str(raw).strip())
    return int(m.group(1)) if m else None


def parse_mosaic_010(raw):
    if raw in (None, '', 'N/A'):
        return (None, None)
    s = str(raw).strip()
    m_score = re.match(r'^(\d+)\s*/\s*1000', s)
    score = int(m_score.group(1)) if m_score else None
    m_delta = re.search(r'([+-]\d+)\s*\(1-y\)', s)
    delta = int(m_delta.group(1)) if m_delta else None
    return score, delta


def parse_mosaic_014(raw):
    if raw in (None, '', 'N/A', 'N/A / 1000'):
        return None
    m = re.match(r'^(\d+)\s*/\s*1000$', str(raw).strip())
    return int(m.group(1)) if m else None


def assign_segment(row_order, boundaries):
    if row_order is None:
        return None
    for boundary in boundaries:
        if boundary['start_row'] <= row_order <= boundary['end_row']:
            return boundary['segment']
    return None


def stage_family(raw):
    if raw in (None, '', 'N/A'):
        return 'N/A/other'
    s = str(raw).lower()
    if any(token in s for token in ['debt', 'loan', 'line of credit']):
        return 'debt/loan/credit'
    if any(token in s for token in ['grant', 'corporate', 'biz plan competition', 'incubator/accelerator']):
        return 'grant/corporate'
    if any(token in s for token in ['series', 'seed', 'bridge', 'private equity', 'growth equity', 'unattributed vc', 'equity']):
        return 'equity VC'
    return 'N/A/other'


def percentile_from_rank(rank_series):
    n = len(rank_series)
    if n <= 1:
        return pd.Series([100.0] * n, index=rank_series.index)
    return ((n - rank_series) / (n - 1) * 100.0).round(6)


def build_df_010(data):
    rows = []
    boundaries = data.get('segment_boundaries', [])
    for item in data['companies']:
        score, delta = parse_mosaic_010(item.get('mosaic_raw'))
        rows.append({
            'company': item['company'],
            'row_order': item.get('row_order'),
            'founded_year': parse_year(item.get('founded_year_raw')),
            'stage_raw': item.get('stage_raw'),
            'total_raised_raw': item.get('total_raised_raw'),
            'total_raised_m': parse_money_to_millions(item.get('total_raised_raw')),
            'headcount': parse_int(item.get('headcount_raw')),
            'commercial_maturity_raw': item.get('commercial_maturity_raw'),
            'commercial_maturity': parse_maturity(item.get('commercial_maturity_raw')),
            'mosaic_raw': item.get('mosaic_raw'),
            'mosaic_score': score,
            'mosaic_delta': delta,
            'segment': assign_segment(item.get('row_order'), boundaries),
        })
    return pd.DataFrame(rows)


def build_df_014(data):
    rows = []
    for item in data['companies']:
        rows.append({
            'company': item['company'],
            'founded_year': parse_year(item.get('founded_year_raw')),
            'ipo_probability': parse_percentage(item.get('ipo_probability_raw')),
            'total_raised_raw': item.get('total_raised_raw'),
            'total_raised_m': parse_money_to_millions(item.get('total_raised_raw')),
            'total_raised_b': None if parse_money_to_millions(item.get('total_raised_raw')) is None else parse_money_to_millions(item.get('total_raised_raw')) / 1000.0,
            'headcount': parse_int(item.get('headcount_raw')),
            'commercial_maturity_raw': item.get('commercial_maturity_raw'),
            'commercial_maturity': parse_maturity(item.get('commercial_maturity_raw')),
            'mosaic_raw': item.get('mosaic_raw'),
            'mosaic_score': parse_mosaic_014(item.get('mosaic_raw')),
        })
    return pd.DataFrame(rows)


def sort_df(df, by, ascending=False):
    if isinstance(by, str):
        by = [by, 'company']
        ascending = [ascending, True]
    return df.sort_values(by=by, ascending=ascending, kind='mergesort').reset_index(drop=True)


def final_payload(data, chart_type, value_unit, sort_rule, selection_rule, records, plot_config, reasoning_summary, stats, open_issues=None):
    return {
        'report_id': data['report_id'],
        'query_id': data['query_id'],
        'query_text': data['query_text'],
        'chart_type': chart_type,
        'value_unit': value_unit,
        'sort_rule': sort_rule,
        'selection_rule': selection_rule,
        'records': records,
        'plot_config': plot_config,
        'reasoning_summary': reasoning_summary,
        'stats': stats,
        'open_issues': open_issues or [],
    }


def build_010_q1(data):
    df = build_df_010(data)
    eligible = df[df['total_raised_m'].notna() & df['mosaic_score'].notna()].copy()
    eligible['value'] = eligible['mosaic_score'] / (eligible['total_raised_m'] / 100.0)
    ranked = sort_df(eligible, 'value', ascending=False).head(15)
    records = [{'label': r.company, 'value': round(float(r.value), 6)} for r in ranked.itertuples()]
    return final_payload(data, 'ranked_bar', 'Mosaic points per $100M raised', 'descending by capital efficiency', 'top 15 companies with numeric funding', records, {'title': 'Top companies by capital efficiency', 'x_label': 'Mosaic points per $100M raised', 'y_label': 'Company'}, ['Filtered to companies with numeric Total raised and Mosaic.', 'Converted Total raised to millions of dollars and then to units of $100M.', 'Computed Mosaic score divided by funding-in-$100M-units.', 'Ranked companies descending and kept the top 15.'], {'eligible_count': int(len(eligible)), 'returned_count': int(len(records))})


def build_010_q2(data):
    df = build_df_010(data)
    eligible = df[df['total_raised_m'].notna() & df['headcount'].notna() & df['mosaic_score'].notna()].copy()
    eligible['funding_rank'] = eligible['total_raised_m'].rank(method='min', ascending=False)
    eligible['mosaic_rank'] = eligible['mosaic_score'].rank(method='min', ascending=False)
    eligible['rank_gap'] = eligible['funding_rank'] - eligible['mosaic_rank']
    top12 = set(sort_df(eligible, ['rank_gap', 'mosaic_score', 'company'], ascending=[False, False, True]).head(12)['company'])
    eligible = sort_df(eligible, ['total_raised_m', 'mosaic_score', 'company'], ascending=[True, False, True])
    def maturity_color(val):
        return 'Unknown' if pd.isna(val) else f'{int(val)} / 5'
    records = []
    for r in eligible.itertuples():
        records.append({
            'label': r.company,
            'x': round(float(r.total_raised_m), 6),
            'y': int(r.mosaic_score),
            'size': int(r.headcount),
            'color': maturity_color(r.commercial_maturity),
            'highlight_label': r.company in top12,
            'rank_gap': round(float(r.rank_gap), 6),
        })
    return final_payload(data, 'bubble', 'mixed', 'all eligible companies plotted; labels restricted to the 12 largest positive funding-rank minus Mosaic-rank gaps', 'numeric funding, headcount, and Mosaic required', records, {'title': 'Quality vs funding with rank-gap highlights', 'x_label': 'Total raised ($M)', 'y_label': 'Mosaic score'}, ['Filtered to companies with numeric funding, headcount, and Mosaic.', 'Ranked companies by funding and Mosaic separately.', 'Computed funding rank minus Mosaic rank and flagged the 12 largest positive gaps for labeling.', 'Rendered all eligible companies as a bubble chart with maturity-based color.'], {'eligible_count': int(len(eligible)), 'returned_count': int(len(records)), 'highlight_count': int(sum(1 for r in records if r['highlight_label']))})


def build_010_q3(data):
    df = build_df_010(data)
    eligible = df[df['segment'].notna() & df['commercial_maturity'].notna()].copy()
    def bucket(val):
        if val <= 2:
            return '2 or below'
        if val == 5:
            return '5'
        return '3 to 4'
    eligible['bucket'] = eligible['commercial_maturity'].apply(bucket)
    denom = eligible.groupby('segment')['company'].count().to_dict()
    segments = list(dict.fromkeys(df['segment'].dropna().tolist()))
    buckets = ['2 or below', '3 to 4', '5']
    grouped = eligible.groupby(['segment', 'bucket'])['company'].count().to_dict()
    records = []
    for segment in segments:
        for b in buckets:
            count = grouped.get((segment, b), 0)
            share = 0.0 if denom.get(segment, 0) == 0 else count / denom[segment] * 100.0
            records.append({'group': segment, 'category': b, 'value': round(share, 6), 'count': int(count), 'denominator': int(denom.get(segment, 0))})
    return final_payload(data, 'stacked_bar', 'percent of companies with numeric Commercial Maturity', 'segment order follows report structure', 'within-segment shares across three maturity buckets', records, {'title': 'Maturity mix by value-chain segment', 'x_label': 'Value-chain segment', 'y_label': 'Share of companies (%)'}, ['Assigned segment membership from the section-2 page-block boundaries.', 'Excluded rows with N/A Commercial Maturity because the query defines only three numeric buckets.', 'Bucketed maturity into 2 or below, 3 to 4, and 5.', 'Computed within-segment shares for each bucket.'], {'eligible_count': int(len(eligible)), 'returned_count': int(len(records)), 'segment_count': int(len(segments))}, ['Rows with N/A / 5 Commercial Maturity were excluded from the denominator.'])


def build_010_q4(data):
    df = build_df_010(data)
    segments = df.groupby('segment')['company'].count().reset_index(name='company_count')
    total_companies = segments['company_count'].sum()
    funding = df[df['total_raised_m'].notna()].groupby('segment')['total_raised_m'].sum().reset_index(name='funding_m')
    total_funding = funding['funding_m'].sum()
    merged = segments.merge(funding, on='segment', how='left').fillna({'funding_m': 0.0})
    merged = merged[merged['company_count'] >= 5].copy()
    merged['left_value'] = merged['company_count'] / total_companies * 100.0
    merged['right_value'] = merged['funding_m'] / total_funding * 100.0
    merged['abs_gap'] = (merged['right_value'] - merged['left_value']).abs()
    merged = sort_df(merged.rename(columns={'segment': 'company'}), ['abs_gap', 'company'], ascending=[False, True]).rename(columns={'company': 'segment'})
    records = [{'label': r.segment, 'left_value': round(float(r.left_value), 6), 'right_value': round(float(r.right_value), 6), 'delta': round(float(r.right_value - r.left_value), 6)} for r in merged.itertuples()]
    return final_payload(data, 'dumbbell', 'share (%)', 'descending by absolute gap between company share and funding share', 'segments with at least five companies', records, {'title': 'Segment share of companies vs disclosed funding', 'x_label': 'Share (%)', 'left_label': 'Share of companies', 'right_label': 'Share of disclosed funding'}, ['Assigned segments from section-2 boundaries.', 'Counted each segment’s share of all companies.', 'Summed disclosed funding by segment and converted that to share of disclosed funding.', 'Computed absolute gaps and sorted segments by gap size.'], {'eligible_count': int(len(merged)), 'returned_count': int(len(records))})


def build_010_q5(data):
    df = build_df_010(data)
    eligible = df[(df['founded_year'].notna()) & (df['founded_year'] >= 2020) & df['headcount'].notna() & df['total_raised_m'].notna() & df['mosaic_score'].notna() & df['segment'].notna()].copy()
    eligible['x'] = eligible['headcount'] / (eligible['total_raised_m'] / 100.0)
    eligible = sort_df(eligible, ['founded_year', 'company'], ascending=[False, True]).head(20)
    records = [{'label': r.company, 'x': round(float(r.x), 6), 'y': int(r.mosaic_score), 'color': r.segment, 'founded_year': int(r.founded_year)} for r in eligible.itertuples()]
    return final_payload(data, 'scatter', 'Headcount per $100M raised', 'descending by Founded year, then company name', 'companies founded in 2020 or later with numeric headcount, funding, and Mosaic', records, {'title': 'Youngest companies: headcount intensity vs Mosaic', 'x_label': 'Headcount per $100M raised', 'y_label': 'Mosaic score'}, ['Filtered to companies founded in 2020 or later with numeric headcount, funding, and Mosaic.', 'Converted funding to units of $100M and computed headcount intensity.', 'Assigned segments from section-2 boundaries.', 'Sorted by founded year descending and kept up to 20 companies.'], {'eligible_count': int(len(df[(df['founded_year'].notna()) & (df['founded_year'] >= 2020)])), 'returned_count': int(len(records))}, ['Fewer than 20 companies may qualify when numeric funding/headcount requirements are applied.'])


def build_010_q6(data):
    df = build_df_010(data)
    eligible = df[df['mosaic_score'].notna() & df['segment'].notna()].copy()
    eligible['stage_family'] = eligible['stage_raw'].apply(stage_family)
    agg = eligible.groupby(['segment', 'stage_family']).agg(avg_mosaic=('mosaic_score', 'mean'), company_count=('company', 'count')).reset_index()
    agg = agg[agg['company_count'] >= 2].copy()
    segment_order = list(dict.fromkeys(df['segment'].dropna().tolist()))
    stage_order = ['equity VC', 'debt/loan/credit', 'grant/corporate', 'N/A/other']
    records = []
    for segment in segment_order:
        for stage in stage_order:
            hit = agg[(agg['segment'] == segment) & (agg['stage_family'] == stage)]
            if hit.empty:
                continue
            row = hit.iloc[0]
            records.append({'row': segment, 'col': stage, 'value': round(float(row['avg_mosaic']), 6), 'count': int(row['company_count'])})
    return final_payload(data, 'heatmap', 'average Mosaic score', 'report segment order on rows; normalized stage-family order on columns', 'cells with at least two companies', records, {'title': 'Average Mosaic by segment and normalized stage family', 'x_label': 'Stage family', 'y_label': 'Value-chain segment'}, ['Assigned segment membership from section-2 boundaries.', 'Normalized raw stage labels into equity VC, debt/loan/credit, grant/corporate, and N/A/other.', 'Aggregated average Mosaic by segment-stage cell.', 'Excluded cells with fewer than two companies.'], {'eligible_count': int(len(eligible)), 'returned_count': int(len(records)), 'cell_count': int(len(records))}, ['Stage-family mapping is a documented normalization step rather than a visible source field.'])


def build_010_q7(data):
    df = build_df_010(data)
    eligible = df[df['founded_year'].notna() & df['mosaic_delta'].notna()].copy()
    eligible['age_years'] = 2026 - eligible['founded_year']
    eligible = eligible[eligible['age_years'] > 0].copy()
    eligible['value'] = eligible['mosaic_delta'] / eligible['age_years']
    ranked = sort_df(eligible, 'value', ascending=False).head(10)
    records = [{'label': r.company, 'value': round(float(r.value), 6)} for r in ranked.itertuples()]
    return final_payload(data, 'ranked_bar', 'Mosaic-change points per company-year', 'descending by Mosaic momentum', 'top 10 companies with numeric Founded year and 1-year Mosaic delta', records, {'title': 'Top companies by age-normalized Mosaic momentum', 'x_label': 'Mosaic-change points per company-year', 'y_label': 'Company'}, ['Filtered to companies with numeric founded year and one-year Mosaic change.', 'Computed company age as 2026 minus Founded year.', 'Divided Mosaic delta by age in years and ranked descending.', 'Kept the top 10 companies.'], {'eligible_count': int(len(eligible)), 'returned_count': int(len(records))})


def build_010_q8(data):
    df = build_df_010(data)
    segment_order = list(dict.fromkeys(df['segment'].dropna().tolist()))
    recent = df[df['founded_year'].notna() & (df['founded_year'] >= 2020)]
    high = df[df['mosaic_score'].notna() & (df['mosaic_score'] >= 850)]
    recent_counts = recent.groupby('segment')['company'].count().to_dict()
    high_counts = high.groupby('segment')['company'].count().to_dict()
    recent_total = sum(recent_counts.values())
    high_total = sum(high_counts.values())
    rows = []
    for segment in segment_order:
        left = 0.0 if recent_total == 0 else recent_counts.get(segment, 0) / recent_total * 100.0
        right = 0.0 if high_total == 0 else high_counts.get(segment, 0) / high_total * 100.0
        rows.append({'label': segment, 'left_value': round(left, 6), 'right_value': round(right, 6), 'delta': round(right - left, 6)})
    rows = sorted(rows, key=lambda x: (-x['delta'], x['label']))
    return final_payload(data, 'slope', 'share (%)', 'descending by increase from recent-founder share to high-Mosaic share', 'segment shares within the recent-founder subset and the Mosaic>=850 subset', rows, {'title': 'Segment share shift: recent founders vs high-Mosaic firms', 'left_label': 'Share of companies founded in or after 2020', 'right_label': 'Share of companies with Mosaic >= 850', 'y_label': 'Share (%)'}, ['Assigned segment membership from section-2 boundaries.', 'Built the recent-founder subset using Founded year >= 2020.', 'Built the high-Mosaic subset using Mosaic >= 850.', 'Computed segment shares within each subset and sorted by share increase.'], {'recent_subset_count': int(len(recent)), 'high_mosaic_subset_count': int(len(high)), 'returned_count': int(len(rows))})


def build_010_q9(data):
    df = build_df_010(data)
    eligible = df[df['total_raised_m'].notna() & df['headcount'].notna() & df['mosaic_score'].notna() & df['commercial_maturity'].notna()].copy()
    eligible['funding_rank'] = eligible['total_raised_m'].rank(method='min', ascending=False)
    eligible['funding_rank_percentile'] = percentile_from_rank(eligible['funding_rank'])
    eligible['gap_score'] = eligible['mosaic_score'] - eligible['funding_rank_percentile']
    def maturity_bucket(val):
        if val < 4:
            return 'Below 4'
        if val == 4:
            return '4'
        return '5'
    eligible['maturity_bucket'] = eligible['commercial_maturity'].apply(maturity_bucket)
    ranked = sort_df(eligible, ['gap_score', 'company'], ascending=[False, True]).head(12)
    records = [{'label': r.company, 'x': int(r.headcount), 'y': round(float(r.gap_score), 6), 'size': round(float(r.total_raised_m), 6), 'color': r.maturity_bucket} for r in ranked.itertuples()]
    return final_payload(data, 'bubble', 'Mosaic score minus funding-rank percentile', 'descending by derived gap score', 'top 12 companies with numeric funding, headcount, Mosaic, and Commercial Maturity', records, {'title': 'Quality minus funding-rank percentile gap', 'x_label': 'Headcount', 'y_label': 'Mosaic score minus funding-rank percentile'}, ['Filtered to companies with numeric funding, headcount, Mosaic, and Commercial Maturity.', 'Computed funding-rank percentiles from funding ranks.', 'Subtracted funding-rank percentile from Mosaic score.', 'Bucketed maturity into below 4, equal to 4, and equal to 5, then kept the top 12 gap scores.'], {'eligible_count': int(len(eligible)), 'returned_count': int(len(records))}, ['Rows with N/A Commercial Maturity were excluded because the color encoding requires numeric maturity.'])


def build_010_q10(data):
    df = build_df_010(data)
    eligible = df[df['total_raised_m'].notna() & df['segment'].notna()].copy()
    rows = []
    for segment, group in eligible.groupby('segment'):
        ranked = group.sort_values(['total_raised_m', 'company'], ascending=[False, True], kind='mergesort')
        total = ranked['total_raised_m'].sum()
        top3 = ranked.head(3)['total_raised_m'].sum()
        rows.append({'label': segment, 'value': round(float(top3 / total * 100.0), 6), 'eligible_companies': int(len(ranked))})
    rows = sorted(rows, key=lambda x: (-x['value'], x['label']))[:8]
    open_issues = []
    if len(rows) < 8:
        open_issues.append('Only 5 value-chain segments are available after de-duplication, so the chart includes all eligible segments instead of eight.')
    return final_payload(data, 'ranked_bar', 'top-3 funding concentration (%)', 'descending by top-3 funding concentration', 'all eligible segments with numeric funding; capped at the top 8 if available', rows, {'title': 'Top-3 funding concentration by segment', 'x_label': 'Top-3 funding concentration (%)', 'y_label': 'Segment'}, ['Assigned segment membership from section-2 boundaries.', 'Kept only companies with numeric disclosed funding.', 'Ranked companies within each segment by funding and summed the top three values.', 'Divided top-three funding by each segment’s total disclosed funding and sorted descending.'], {'eligible_segment_count': int(df['segment'].nunique()), 'returned_count': int(len(rows))}, open_issues)


def build_014_q1(data):
    df = build_df_014(data)
    eligible = df[df['total_raised_b'].notna()].copy()
    eligible['value'] = eligible['ipo_probability'] / eligible['total_raised_b']
    ranked = sort_df(eligible, 'value', ascending=False).head(15)
    records = [{'label': r.company, 'value': round(float(r.value), 6)} for r in ranked.itertuples()]
    return final_payload(data, 'ranked_bar', 'IPO-probability points per $1B raised', 'descending by IPO readiness efficiency', 'top 15 companies with numeric funding', records, {'title': 'Top companies by IPO readiness efficiency', 'x_label': 'IPO-probability points per $1B raised', 'y_label': 'Company'}, ['Filtered to companies with numeric disclosed funding.', 'Converted Total raised to billions of dollars.', 'Divided IPO probability by funding in $B.', 'Ranked descending and kept the top 15 companies.'], {'eligible_count': int(len(eligible)), 'returned_count': int(len(records))})


def build_014_q2(data):
    df = build_df_014(data)
    eligible = df[df['headcount'].notna() & df['mosaic_score'].notna()].copy()
    eligible['mosaic_rank'] = eligible['mosaic_score'].rank(method='min', ascending=False)
    eligible['mosaic_rank_percentile'] = percentile_from_rank(eligible['mosaic_rank'])
    eligible['gap_score'] = eligible['ipo_probability'] - eligible['mosaic_rank_percentile']
    ranked = sort_df(eligible, ['gap_score', 'company'], ascending=[False, True]).head(20)
    records = [{'label': r.company, 'x': int(r.mosaic_score), 'y': round(float(r.ipo_probability), 6), 'size': int(r.headcount), 'color': 'Selected', 'gap_score': round(float(r.gap_score), 6)} for r in ranked.itertuples()]
    return final_payload(data, 'bubble', 'IPO probability (%)', 'descending by IPO probability minus Mosaic rank percentile', 'top 20 companies with numeric headcount and Mosaic', records, {'title': 'IPO probability vs Mosaic for the largest positive readiness gaps', 'x_label': 'Mosaic score', 'y_label': 'IPO probability (%)'}, ['Filtered to companies with numeric headcount and Mosaic.', 'Ranked companies by Mosaic and converted the ranks to percentiles.', 'Computed IPO probability minus Mosaic-rank percentile.', 'Kept the top 20 positive gaps for the bubble chart.'], {'eligible_count': int(len(eligible)), 'returned_count': int(len(records))})


def build_014_q3(data):
    df = build_df_014(data)
    eligible = df[df['commercial_maturity'].notna()].copy()
    eligible['ipo_rank'] = eligible['ipo_probability'].rank(method='min', ascending=False)
    eligible['maturity_rank'] = eligible['commercial_maturity'].rank(method='min', ascending=False)
    eligible['abs_gap'] = (eligible['ipo_rank'] - eligible['maturity_rank']).abs()
    ranked = sort_df(eligible, ['abs_gap', 'company'], ascending=[False, True]).head(12)
    records = [{'label': r.company, 'left_value': round(float(r.ipo_rank), 6), 'right_value': round(float(r.maturity_rank), 6), 'delta': round(float(r.ipo_rank - r.maturity_rank), 6)} for r in ranked.itertuples()]
    return final_payload(data, 'dumbbell', 'rank position', 'descending by absolute gap between IPO-probability rank and Commercial-Maturity rank', 'top 12 companies with numeric Commercial Maturity', records, {'title': 'IPO rank vs Commercial Maturity rank', 'x_label': 'Rank (lower is better)', 'left_label': 'IPO-probability rank', 'right_label': 'Commercial-Maturity rank'}, ['Filtered to companies with numeric Commercial Maturity.', 'Ranked companies by IPO probability and by Commercial Maturity.', 'Computed absolute rank gaps and selected the 12 largest divergences.', 'Plotted the two rank positions for each selected company.'], {'eligible_count': int(len(eligible)), 'returned_count': int(len(records))}, ['Commercial Maturity is a low-cardinality 1-5 scale, so ties are resolved with the deterministic min-rank convention.'])


def build_014_q4(data):
    df = build_df_014(data)
    eligible = df[df['founded_year'].notna()].copy()
    def cohort(year):
        if 2000 <= year <= 2009:
            return '2000-2009'
        if 2010 <= year <= 2014:
            return '2010-2014'
        if 2015 <= year <= 2019:
            return '2015-2019'
        return '2020+'
    def band(prob):
        if prob < 20.0:
            return 'Below 20%'
        if prob < 40.0:
            return '20%-39.9%'
        return '40%+'
    eligible['cohort'] = eligible['founded_year'].apply(cohort)
    eligible['band'] = eligible['ipo_probability'].apply(band)
    cohort_avg = eligible.groupby('cohort')['ipo_probability'].mean().to_dict()
    cohort_order = [k for k, _ in sorted(cohort_avg.items(), key=lambda item: (-item[1], item[0]))]
    band_order = ['Below 20%', '20%-39.9%', '40%+']
    counts = eligible.groupby(['cohort', 'band'])['company'].count().to_dict()
    denom = eligible.groupby('cohort')['company'].count().to_dict()
    records = []
    for c in cohort_order:
        for b in band_order:
            count = counts.get((c, b), 0)
            share = count / denom[c] * 100.0
            records.append({'group': c, 'category': b, 'value': round(share, 6), 'count': int(count), 'denominator': int(denom[c])})
    return final_payload(data, 'stacked_bar', 'share of cohort companies (%)', 'cohorts sorted by average IPO probability descending', 'all companies with numeric Founded year, bucketed into founded-year cohorts and IPO-probability bands', records, {'title': 'IPO-probability mix by founded-year cohort', 'x_label': 'Founded-year cohort', 'y_label': 'Share of companies (%)'}, ['Assigned companies to founded-year cohorts.', 'Bucketed IPO probability into below 20%, 20%-39.9%, and 40%+ bands.', 'Computed average IPO probability by cohort for bar ordering.', 'Calculated within-cohort shares for the three IPO-probability bands.'], {'eligible_count': int(len(eligible)), 'returned_count': int(len(records)), 'cohort_count': int(len(cohort_order))})


def build_014_q5(data):
    df = build_df_014(data)
    eligible = df[df['headcount'].notna() & df['total_raised_b'].notna() & df['commercial_maturity'].notna()].copy()
    eligible = eligible[eligible['headcount'] > 1].copy()
    eligible['value'] = eligible['ipo_probability'] / eligible['headcount'].apply(lambda x: math.log10(x))
    ranked = sort_df(eligible, ['value', 'company'], ascending=[False, True]).head(25)
    records = [{'label': r.company, 'x': round(float(r.total_raised_b), 6), 'y': round(float(r.value), 6), 'color': f'{int(r.commercial_maturity)} / 5'} for r in ranked.itertuples()]
    return final_payload(data, 'scatter', 'IPO probability divided by log10(headcount)', 'descending by scale-adjusted IPO readiness', 'top 25 companies with numeric funding, headcount, and Commercial Maturity', records, {'title': 'Scale-adjusted IPO readiness', 'x_label': 'Total raised ($B)', 'y_label': 'IPO probability / log10(headcount)'}, ['Filtered to companies with numeric funding, headcount, and Commercial Maturity.', 'Computed log10(headcount) and divided IPO probability by that scale term.', 'Ranked descending by the derived readiness metric.', 'Kept the top 25 companies for plotting.'], {'eligible_count': int(len(eligible)), 'returned_count': int(len(records))}, ['The log10(headcount) normalization is a documented modeling choice from the query recommendation.'])


def build_014_q6(data):
    df = build_df_014(data)
    eligible = df[df['mosaic_score'].notna()].copy()
    eligible['mosaic_rank'] = eligible['mosaic_score'].rank(method='min', ascending=False)
    eligible['ipo_rank'] = eligible['ipo_probability'].rank(method='min', ascending=False)
    eligible['mosaic_percentile'] = percentile_from_rank(eligible['mosaic_rank'])
    eligible['ipo_percentile'] = percentile_from_rank(eligible['ipo_rank'])
    eligible['value'] = (eligible['mosaic_percentile'] - eligible['ipo_percentile']).abs()
    ranked = sort_df(eligible, ['value', 'company'], ascending=[False, True]).head(10)
    records = [{'label': r.company, 'value': round(float(r.value), 6)} for r in ranked.itertuples()]
    return final_payload(data, 'ranked_bar', 'percentile-point mismatch', 'descending by absolute mismatch between Mosaic percentile and IPO-probability percentile', 'top 10 companies with numeric Mosaic', records, {'title': 'Largest Mosaic-to-IPO mismatches', 'x_label': 'Absolute percentile-point mismatch', 'y_label': 'Company'}, ['Filtered to companies with numeric Mosaic.', 'Ranked companies by Mosaic and IPO probability separately.', 'Converted both rank series to percentile scales.', 'Computed the absolute mismatch and kept the top 10 companies.'], {'eligible_count': int(len(eligible)), 'returned_count': int(len(records))})


def build_014_q7(data):
    df = build_df_014(data)
    eligible = df[(df['founded_year'].notna()) & (df['founded_year'] >= 2015) & df['headcount'].notna() & df['total_raised_m'].notna() & df['mosaic_score'].notna() & df['commercial_maturity'].notna()].copy()
    eligible['x'] = eligible['headcount'] / (eligible['total_raised_m'] / 100.0)
    eligible['color'] = eligible['commercial_maturity'].apply(lambda v: 'Below 5' if v < 5 else '5 / 5')
    ranked = sort_df(eligible, ['ipo_probability', 'company'], ascending=[False, True]).head(15)
    records = [{'label': r.company, 'x': round(float(r.x), 6), 'y': round(float(r.ipo_probability), 6), 'size': int(r.mosaic_score), 'color': r.color} for r in ranked.itertuples()]
    return final_payload(data, 'bubble', 'Headcount per $100M raised vs IPO probability', 'descending by IPO probability within the founded-2015-or-later subset', 'top 15 companies founded in 2015 or later with numeric funding, headcount, Mosaic, and Commercial Maturity', records, {'title': 'IPO probability vs headcount intensity for recent companies', 'x_label': 'Headcount per $100M raised', 'y_label': 'IPO probability (%)'}, ['Filtered to companies founded in 2015 or later with numeric funding, headcount, Mosaic, and Commercial Maturity.', 'Converted funding to units of $100M and computed headcount intensity.', 'Bucketed Commercial Maturity into below 5 versus exactly 5.', 'Ranked by IPO probability and kept the top 15 companies.'], {'eligible_count': int(len(eligible)), 'returned_count': int(len(records))})


def build_014_q8(data):
    df = build_df_014(data)
    eligible = df[df['founded_year'].notna()].copy()
    def cohort(year):
        if year < 2010:
            return 'pre-2010'
        if year <= 2014:
            return '2010-2014'
        if year <= 2019:
            return '2015-2019'
        return '2020+'
    eligible['cohort'] = eligible['founded_year'].apply(cohort)
    company_counts = eligible.groupby('cohort')['company'].count().to_dict()
    total_companies = sum(company_counts.values())
    funding = eligible[eligible['total_raised_b'].notna()].groupby('cohort')['total_raised_b'].sum().to_dict()
    total_funding = sum(funding.values())
    cohorts = ['pre-2010', '2010-2014', '2015-2019', '2020+']
    rows = []
    for c in cohorts:
        left = company_counts.get(c, 0) / total_companies * 100.0
        right = 0.0 if total_funding == 0 else funding.get(c, 0.0) / total_funding * 100.0
        rows.append({'label': c, 'left_value': round(left, 6), 'right_value': round(right, 6), 'delta': round(right - left, 6)})
    rows = sorted(rows, key=lambda x: (-x['delta'], x['label']))
    return final_payload(data, 'slope', 'share (%)', 'descending by increase from company share to funding share', 'all companies with numeric Founded year; funding shares use disclosed funding only', rows, {'title': 'Cohort share of companies vs disclosed funding', 'left_label': 'Share of pipeline companies', 'right_label': 'Share of disclosed funding', 'y_label': 'Share (%)'}, ['Assigned companies to the pre-2010, 2010-2014, 2015-2019, and 2020+ cohorts.', 'Computed each cohort’s share of all pipeline companies.', 'Summed disclosed funding by cohort and converted those sums to funding shares.', 'Sorted cohorts by the increase from company share to funding share.'], {'cohort_count': int(len(rows)), 'returned_count': int(len(rows))}, ['Funding-share denominators exclude rows with N/A Total raised.'])


def build_014_q9(data):
    df = build_df_014(data)
    eligible = df[(df['commercial_maturity'] == 5) & df['total_raised_b'].notna() & df['headcount'].notna() & df['mosaic_score'].notna()].copy()
    median_mosaic = eligible['mosaic_score'].median()
    eligible['color'] = eligible['mosaic_score'].apply(lambda v: 'At or above median Mosaic' if v >= median_mosaic else 'Below median Mosaic')
    ranked = sort_df(eligible, ['ipo_probability', 'company'], ascending=[False, True]).head(20)
    records = [{'label': r.company, 'x': round(float(r.total_raised_b), 6), 'y': round(float(r.ipo_probability), 6), 'size': int(r.headcount), 'color': r.color} for r in ranked.itertuples()]
    return final_payload(data, 'bubble', 'IPO probability (%)', 'descending by IPO probability inside the Commercial Maturity = 5 subset', 'top 20 companies with Commercial Maturity = 5 and numeric funding, headcount, and Mosaic', records, {'title': 'Maturity-5 companies: funding vs IPO probability', 'x_label': 'Total raised ($B)', 'y_label': 'IPO probability (%)'}, ['Filtered to companies with Commercial Maturity = 5 plus numeric funding, headcount, and Mosaic.', 'Computed the median Mosaic within the filtered set.', 'Flagged companies as at/above versus below the filtered-set median.', 'Ranked by IPO probability and kept the top 20 companies.'], {'eligible_count': int(len(eligible)), 'returned_count': int(len(records)), 'median_mosaic': float(median_mosaic) if not pd.isna(median_mosaic) else None}, ['Rows with N/A Mosaic were excluded because the color split depends on the filtered-set median Mosaic.'])


def build_014_q10(data):
    df = build_df_014(data)
    eligible = df[df['headcount'].notna()].copy()
    eligible['value'] = eligible['ipo_probability'] / (eligible['headcount'] / 1000.0)
    ranked = sort_df(eligible, ['value', 'company'], ascending=[False, True]).head(12)
    records = [{'label': r.company, 'value': round(float(r.value), 6)} for r in ranked.itertuples()]
    return final_payload(data, 'ranked_bar', 'percentage points of IPO probability per 1,000 employees', 'descending by IPO probability per 1,000 employees', 'top 12 companies with numeric headcount', records, {'title': 'Top companies by IPO probability per 1,000 employees', 'x_label': 'IPO-probability points per 1,000 employees', 'y_label': 'Company'}, ['Filtered to companies with numeric headcount.', 'Scaled headcount to units of 1,000 employees.', 'Divided IPO probability by scaled headcount and ranked descending.', 'Kept the top 12 companies.'], {'eligible_count': int(len(eligible)), 'returned_count': int(len(records))})


BUILDERS = {
    ('010', 1): build_010_q1,
    ('010', 2): build_010_q2,
    ('010', 3): build_010_q3,
    ('010', 4): build_010_q4,
    ('010', 5): build_010_q5,
    ('010', 6): build_010_q6,
    ('010', 7): build_010_q7,
    ('010', 8): build_010_q8,
    ('010', 9): build_010_q9,
    ('010', 10): build_010_q10,
    ('014', 1): build_014_q1,
    ('014', 2): build_014_q2,
    ('014', 3): build_014_q3,
    ('014', 4): build_014_q4,
    ('014', 5): build_014_q5,
    ('014', 6): build_014_q6,
    ('014', 7): build_014_q7,
    ('014', 8): build_014_q8,
    ('014', 9): build_014_q9,
    ('014', 10): build_014_q10,
}


def main():
    data = load_data()
    builder = BUILDERS[(data['report_id'], data['query_id'])]
    payload = builder(data)
    FINAL_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
