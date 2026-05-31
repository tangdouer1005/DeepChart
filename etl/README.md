# ETL — normalize raw sources → canonical schema

Each `normalize_<domain>.py` reads one raw source and emits
`instances/<domain>.jsonl` conforming to [`schema/`](../schema/SCHEMA.md), while
materializing context docs into `data/<domain>/` and references into
`references/<domain>/`.

| script | reads | emits |
|---|---|---|
| `normalize_academic.py` | Nature `json/` (178) + GT dirs | `instances/academic.jsonl` |
| `normalize_finance.py` | 10-K `json2/` (290) + GT dirs | `instances/finance.jsonl` |
| `normalize_research_report.py` | `query-level.jsonl` (256) | `instances/research_report.jsonl` |
| `validate.py` | all three jsonl | pass/fail: schema + path existence + counts |

## Normalization rules

- Unify GT directory prefixes into `academic` / `finance` / `research_report`.
- Express context as `context.modality` + `context.variants` (drop the raw
  `data.type` flag).
- Context variants:
  - Academic: `normal` / `long` are scopes of the single full-paper markdown.
  - Finance: all OCR text — `normal` = the 3 statement tables, `long` =
    tables + context, `ultra_long` = the full 10-K markdown. The raw 10-K PDFs
    are source provenance, not input, and are not shipped.
  - Research Report: `normal` = `summary` + the source PDF (multimodal).
- Finance ids **268, 278, 284, 285, 286, 288** have no stage-1 program →
  `program.stage1_extract = null`.
- The gold chart image (`chart_image`) is the python-rendered reference for all
  three domains.
- Preserve Chinese strings verbatim (e.g. `query.metadata.indicator_full`).

## Acceptance (`validate.py` must pass)

- Every record validates against `schema/instance.schema.json`.
- Counts: academic 178, finance 290, research_report 256 (724 total).
- With `--check-paths`, every referenced file under `data/` and `references/`
  exists (allowing the 6 null finance stage-1 programs).
