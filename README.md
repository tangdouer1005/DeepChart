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
| **Domains** | Academic (Nature articles) · Finance (10-K filings) · Research Report (industry reports) |
| **Base queries** | 724 (academic 178 · finance 290 · research report 256) |
| **Instances** | 1,482 (with context-granularity variants) |
| **References** | `D_src` (source data) · `D_der` (derived data) · `P_GT` (gold program) · `G_GT` (gold chart) |
| **Metrics** | `F1_src` (extraction) · `F1_der` (reasoning) · `VAS` (VLM-judged visual accuracy) · `ER` (execution rate) |

## Repository layout

```
deepchart/
├── schema/          canonical instance schema (the contract every record obeys)
│   ├── SCHEMA.md            human spec + per-domain mapping
│   ├── instance.schema.json JSON Schema (draft-07)
│   └── instance_model.py    pydantic model
├── instances/       canonical records — one jsonl per domain
├── data/            model-facing context documents (academic / finance / research_report)
├── references/      hidden ground-truth: D_src / D_der / P_GT / G_GT
├── eval/            unified harness: 2-stage generation + F1_src / F1_der / VAS / ER
├── etl/             normalize the raw sources into the canonical schema + validate
└── scripts/         helpers (e.g. fetch Research Report source PDFs)
```

A datasheet for the benchmark is in [`DATA_CARD.md`](DATA_CARD.md).

## The canonical instance

Every record across all three domains normalizes into a single schema — see
[`schema/SCHEMA.md`](schema/SCHEMA.md). In short:

```jsonc
{
  "uid": "finance/1", "domain": "finance",
  "source":  { "type": "annual_report", "doc_id": "abbv", "url": "" },
  "info":    { "level": "easy", "chart_type": "Line Chart", "chart_type_subclass": "Line Chart" },
  "query":   { "template": "Generate an {code_type}-rendered ...", "code_types": ["python"], "metadata": {...} },
  "context": { "modality": "text", "variants": { "normal": [...], "long": [...], "ultra_long": [...] } },
  "references": {
    "d_src": "references/finance/1/d_src.csv",
    "d_der": "references/finance/1/d_der.json",
    "program": { "stage1_extract": "...", "stage2_python": "...", "stage2_html": "..." },
    "chart_image": "references/finance/1/chart.png"
  }
}
```

## Quick start

```bash
pip install -r requirements.txt

# validate the dataset (schema + counts + referenced-file existence)
python etl/validate.py --check-paths        # -> 724/724 valid

# structural check of the eval harness (no model calls, no cost)
python eval/smoke_test.py

# run two-stage generation for a domain (needs an OpenAI-compatible endpoint)
export OPENAI_BASE_URL=... OPENAI_API_KEY=...
python eval/run_generation.py -d finance --variant normal -m <model>
```

See [`eval/README.md`](eval/README.md) for the metrics (`F1_src`, `F1_der`,
`VAS`, `ER`), the judge configuration, and how keys are loaded.

## Data availability

| domain | source documents | included here? |
|---|---|---|
| Academic | Nature-family articles (OCR'd markdown) | **yes** — full text + extracted data + ground-truth |
| Finance | SEC 10-K filings (OCR'd markdown, public record) | **yes** — three text variants + ground-truth |
| Research Report | CB Insights / StartupBlink / Startup Genome reports | **no** — third-party copyright |

Research Report **source PDFs are not redistributed** (they are commercial,
copyrighted reports). The queries, OCR'd `summary` text, and all ground-truth
(`d_src` / `d_der` / programs / chart images) **are** included, so queries and
scoring work without the raw PDFs. To run the multimodal RR input, obtain the
reports from their publishers — see
[`data/research_report/SOURCES.md`](data/research_report/SOURCES.md), then
`python scripts/download_reports.py` reports which PDFs are still missing.

## License

See [`LICENSE`](LICENSE). Source documents retain their original terms (Nature
article text and SEC filings as cited per instance); the queries and
ground-truth artifacts are released under this repository's license. Citation
metadata: [`CITATION.cff`](CITATION.cff).
