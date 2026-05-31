# DeepChart

An expert-annotated benchmark for **faithful data-science chart generation**,
formulated as **Extract → Reason → Visualize (ERV)**.

A model is given a real-world document (a *context* `C`) and a *query* `Q`, and
must (1) **extract** the relevant source data from the document, (2) **reason**
over it to derive the chart-ready values, and (3) **visualize** it by emitting
executable code that renders the requested chart. Each instance ships hidden
references for scoring each stage.

| | |
|---|---|
| **Domains** | Academic (Nature papers) · Finance (10-K annual reports) · Research Report (industry PDFs) |
| **Base queries** | 724 |
| **Instances** | 1,482 (with context-granularity variants) |
| **References** | `D_src` (source data) · `D_der` (derived data) · `P_GT` (gold program) · `G_GT` (gold chart) |
| **Metrics** | `F1_src` (extraction) · `F1_der` (reasoning) · `VAS` (VLM-judged visual accuracy) · `ER` (execution rate) |

> Status: **internal consolidation — not yet published.** This repo is being
> assembled from three independently-authored sources into one canonical layout.
> See [`docs/PHASE0_INVENTORY.md`](docs/PHASE0_INVENTORY.md) for the source audit.

## Repository layout

```
deepchart/
├── schema/              canonical instance schema (the contract every record obeys)
│   ├── SCHEMA.md            human spec + per-domain mapping
│   ├── instance.schema.json JSON Schema (draft-07)
│   └── instance_model.py    pydantic model
├── instances/           canonical records, one jsonl per domain  (Phase 3 output)
├── data/                model-facing context documents            (Phase 2/3)
│   ├── academic/  finance/  research_report/
├── references/          hidden ground-truth: D_src / D_der / P_GT / G_GT  (Phase 3)
│   ├── academic/  finance/  research_report/
├── etl/                 normalize the 3 raw sources → canonical schema   (Phase 3)
├── eval/                unified harness: 2-stage generation + metrics     (Phase 4)
├── scripts/             helpers (chart rendering, data prep)
└── docs/                inventory, data card, design notes
```

## The canonical instance

Every record across all three domains normalizes into a single schema — see
[`schema/SCHEMA.md`](schema/SCHEMA.md). In short:

```jsonc
{
  "uid": "finance/1", "domain": "finance",
  "source":  { "type": "annual_report", "doc_id": "abbv", ... },
  "info":    { "level": "easy", "chart_type": "Line Chart", ... },
  "query":   { "template": "Generate an {code_type}-rendered ...", "code_types": ["html"], "metadata": {...} },
  "context": { "modality": "text", "variants": { "normal": [...], "long": [...], "ultra_long": [...] } },
  "references": {
    "d_src": "...", "d_der": "...",
    "program": { "stage1_extract": "...", "stage2_python": "...", "stage2_html": "..." },
    "chart_image": "..."        // "" => render on the fly
  }
}
```

## Build status (phased consolidation)

- [x] **Phase 0** — read-only inventory of the three sources (`docs/PHASE0_INVENTORY.md`)
- [x] **Phase 1** — canonical schema + repo skeleton
- [x] **Phase 2** — assemble locally: text-domain data mirrored down (RR already local)
- [x] **Phase 3** — ETL: 724 canonical records in `instances/`, `data/` + `references/` materialized & validated
- [x] **Phase 4** — unified eval harness (2-stage generation + `F1_src`/`F1_der`/`VAS`/`ER`); `eval/smoke_test.py` passes without model calls
- [ ] **Phase 5** — scrub secrets, pin deps, add LICENSE ← *next*
- [ ] **Phase 6** — README/data card finalization + end-to-end smoke test

## Data availability

| domain | source documents | shipped here? |
|---|---|---|
| Academic | Nature-family articles (OCR'd markdown) | **yes** (full text + extracted data + GT) |
| Finance | SEC 10-K filings (OCR'd markdown, public record) | **yes** (3 text variants + GT) |
| Research Report | CB Insights / StartupBlink / Startup Genome PDFs | **no — third-party copyright** |

Research Report **source PDFs are not redistributed** (they are commercial,
copyrighted reports). The queries, OCR'd `summary` text, and all ground-truth
(`d_src` / `d_der` / programs / chart images) **are** included, so queries and
scoring work without the raw PDFs. To run the multimodal RR input, obtain the
reports from their publishers — see
[`data/research_report/SOURCES.md`](data/research_report/SOURCES.md) and
`python scripts/download_reports.py` (reports which PDFs are missing).

## License

TBD (set before public release). See [`LICENSE`](LICENSE). Note the per-domain
provenance above: Nature article text and SEC filings retain their original
terms; ground-truth artifacts are released under this repo's license.
