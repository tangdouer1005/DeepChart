# DeepChart — Data Card

> Draft. Finalized in Phase 6 before any release.

## Overview

DeepChart evaluates **faithful data-science chart generation** under the
Extract → Reason → Visualize (ERV) formulation. Each instance gives a model a
real document + a query and asks it to extract the relevant data, reason it into
chart-ready form, and emit code that renders the requested chart.

## Composition

| domain | source | docs | base queries | context variants | instances |
|---|---|---|---|---|---|
| Academic | Nature research articles | by DOI | 178 | normal, long | 356 |
| Finance | SEC 10-K annual reports | by ticker | 290 | normal, long, ultra_long | 870 |
| Research Report | CB Insights / StartupBlink / Startup Genome PDFs | by report | 256 | (single) | 256 |
| **total** | | | **724** | | **1,482** |

Chart types: Academic spans 15 types (Bar/Scatter/Line/Heatmap/Box/Sankey/…);
Finance is Bar + Line. Levels: present snapshot is uniformly `easy` (field kept
for future medium/hard).

## What ships per instance

- **Model-facing:** context document(s) (`data/`), query template.
- **Hidden references (`references/`):** `D_src` (source data), `D_der` (derived
  data), `P_GT` (gold program, python and/or html), `G_GT` (gold chart image).

## Provenance & licensing

- Academic: figures/data from open-access Nature articles (URLs retained).
- Finance: public SEC filings.
- Research Report: third-party industry reports (source PDFs retained).
- Per-source license review and citation list: **Phase 5–6** (see `CITATION.cff`).

## Known limitations / gaps (Phase 0)

- Finance ids 268, 278, 284, 285, 286, 288 lack a stage1 program.
- Finance `G_GT` images are rendered on the fly (no pre-stored PNGs).
- Some annotator fields are in Chinese (e.g. `indicator_full`), preserved verbatim.

## Secrets / safety

Raw sources contained API keys and credentials; these are scrubbed in Phase 5
(`*key*`, cookies, `google_accounts.json`, RAG configs). See `.gitignore`.
