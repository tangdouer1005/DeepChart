# DeepChart — Data Card

## Overview

DeepChart evaluates **faithful data-science chart generation** under the
Extract → Reason → Visualize (ERV) formulation. Each instance gives a model a
real document + a query and asks it to extract the relevant data, reason it into
chart-ready form, and emit code that renders the requested chart.

## Composition

| domain | source | docs | base queries | context variants | instances |
|---|---|---|---|---|---|
| Academic | Nature research articles | by DOI | 178 | normal, long | 356 |
| Finance | SEC 10-K filings | by ticker | 290 | normal, long, ultra_long | 870 |
| Research Report | CB Insights / StartupBlink / Startup Genome reports | by report | 256 | (single) | 256 |
| **total** | | | **724** | | **1,482** |

Chart types: Academic spans 15 types (Bar/Scatter/Line/Heatmap/Box/Sankey/…);
Finance is Bar + Line. Finance's three context variants are all OCR'd text at
growing scope (3 statement tables → tables+context → full 10-K markdown).

## What ships per instance

- **Model-facing:** context document(s) (`data/`) and the query template.
- **Hidden references (`references/`):** `D_src` (source data), `D_der` (derived
  data), `P_GT` (gold program, python; html kept as a secondary variant for the
  text domains), `G_GT` (gold chart image).

## Provenance & licensing

- **Academic** — Nature-family articles (URLs/DOIs retained per instance);
  ~60% open access.
- **Finance** — public SEC 10-K filings, used as OCR'd text.
- **Research Report** — third-party industry reports; **source PDFs are not
  redistributed** (see `data/research_report/SOURCES.md`).

Source documents retain their original terms; queries and ground-truth artifacts
are the authors' own work. See `LICENSE` and `CITATION.cff`.

## Known limitations

- Finance ids 268, 278, 284, 285, 286, 288 have no stage-1 program
  (`references.program.stage1_extract` is `null`).
- Research Report gold programs are provenance-only (the pre-rendered
  `chart_image` is the usable `G_GT`); see `eval/README.md`.
- Some annotator fields are in Chinese (e.g. `indicator_full`), preserved verbatim.
- The `level` field is uniformly `easy` in this release (kept for future use).
