# ETL — normalize raw sources → canonical schema (Phase 3)

Each `normalize_<domain>.py` reads one raw source and emits
`instances/<domain>.jsonl` conforming to [`schema/`](../schema/SCHEMA.md), while
copying/renaming context docs into `data/<domain>/` and references into
`references/<domain>/`.

| script | reads | emits |
|---|---|---|
| `normalize_academic.py` | remote `bench/json/` (178) + `nature_*` GT dirs | `instances/academic.jsonl` |
| `normalize_finance.py` | remote `bench/json2/` (290) + `report_*` GT dirs | `instances/finance.jsonl` |
| `normalize_research_report.py` | local `new_domain_eval/new_domain/query-level.jsonl` (256) | `instances/research_report.jsonl` |
| `validate.py` | all three jsonl | pass/fail: schema + path existence + counts |

## Normalization rules (from Phase 0)

- GT dir prefixes `nature_*` / `report_*` → `academic` / `finance`.
- Drop `data.type` (`text_file` vs `text_files`); express as
  `context.modality` + `context.variants`.
- Context variants:
  - Academic: `normal` = paper-md crop, `long` = fuller md. (`ultra_long` absent.)
  - Finance: `normal` = `md_3table_context`, `long` = `pdfs_good_md`,
    `ultra_long` = `pdfs_good` (full 10-K).
  - Research Report: `normal` = `summary` (single multimodal variant).
- Finance ids **268, 278, 284, 285, 286, 288** have no stage1 → set
  `program.stage1_extract = null` (or re-run; decision pending).
- Finance `chart_image` = `""` (rendered on the fly in Phase 6).
- Exclude draft sets entirely: `json2_pre`, `json2_rm`, `json_rm`, `json_back`.
- Preserve Chinese strings verbatim (e.g. `query.metadata.indicator_full`).

## Acceptance (validate.py must pass)

- Every record validates against `schema/instance.schema.json`.
- Counts: academic 178, finance 290, research_report 256 (724 total).
- Every referenced path under `data/` and `references/` exists (allowing the 6
  null finance stage1 and `chart_image == ""`).
