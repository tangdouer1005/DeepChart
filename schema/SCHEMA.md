# DeepChart Canonical Instance Schema (v1)

DeepChart is an expert-annotated benchmark for **faithful data-science chart
generation**, formulated as **Extract → Reason → Visualize (ERV)**. It spans
three domains (Academic / Finance / Research Report), 724 base queries and 1,482
instances. Every instance pairs a *model-facing* part (context `C`, query `Q`)
with *hidden references* used only for scoring:

| symbol | meaning |
|--------|---------|
| `D_src` | **source data** — the raw values extracted verbatim from the document |
| `D_der` | **derived data** — the chart-ready table after the required reasoning |
| `P_GT`  | **gold program** — executable code that renders the reference chart |
| `G_GT`  | **gold chart** — the rendered reference image |

The three domains were authored independently and use three *different* on-disk
formats. This document defines **one canonical record** that all three normalize
into (Phase 3 ETL produces it). One JSON object per line in
`instances/<domain>.jsonl`.

---

## 1. Canonical record

```jsonc
{
  // ---- identity ----------------------------------------------------------
  "uid":      "academic/0001",      // globally unique = "<domain>/<orig_id>"
  "domain":   "academic",           // enum: academic | finance | research_report
  "orig_id":  "1",                  // original id within the source domain

  // ---- provenance --------------------------------------------------------
  "source": {
    "type":   "nature",             // nature|annual_report|cbinsights|startupblink|startupgenome
    "doc_id": "41586-025-09755-9",  // DOI / company ticker / report slug
    "url":    "https://www.nature.com/articles/s41586-025-09755-9",
    "fig":    "",                   // figure reference inside the document (optional)
    "notes":  "a, Representative images of ..."   // caption / annotator note (optional)
  },

  // ---- chart metadata ----------------------------------------------------
  "info": {
    "level":               "easy",            // easy | medium | hard
    "chart_type":          "Bar Chart",
    "chart_type_subclass": "Bar Chart with Individual Data Points",
    "topic_domain":        ["healthy"],       // subject tags (was info.domain)
    "chart_description":   { /* nested, optional; academic only */ }
  },

  // ---- model-facing query ------------------------------------------------
  "query": {
    "template":   "Generate an {code_type}-rendered Line Chart, showing ...",
    "code_types": ["python"],       // renderable variants: python | html
    "metadata": {                   // domain-specific query params (optional)
      "company":        "abbv",
      "indicator":      "01_IGR",
      "indicator_full": "内部增长率 (Internal Growth Rate, IGR)",
      "start_year":     "2016",
      "end_year":       "2024"
    }
  },

  // ---- model-facing context ----------------------------------------------
  "context": {
    "modality": "text",             // text | multimodal
    "variants": {                   // at least "normal" is always present
      "normal":     ["data/finance/abbv/normal/..."],
      "long":       ["data/finance/abbv/long/..."],      // optional
      "ultra_long": ["data/finance/abbv/ultra_long/..."] // optional (finance only)
    }
  },

  // ---- hidden references (ERV) ------------------------------------------
  "references": {
    "d_src": "references/finance/0001/d_src.csv",        // source data
    "d_der": "references/finance/0001/d_der.json",       // derived data (null if == d_src)
    "program": {
      "stage1_extract": "references/finance/0001/stage1.py",   // extract+reason code
      "stage2_python":  "references/finance/0001/stage2.py",   // python renderer (optional)
      "stage2_html":    "references/finance/0001/stage2.html"  // html renderer (optional)
    },
    "chart_image": "references/finance/0001/chart.png"   // G_GT; "" => render on the fly
  }
}
```

### Field notes

- **`code_types`** drives the `{code_type}` placeholder in `query.template`.
  The runnable query is `template.format(code_type=ct)` for each `ct`. This is
  why the on-disk queries are templates, not finished strings — there is **no
  `query_full`** field anywhere (verified across all 178+290 records).
- **Two orthogonal axes** — do not conflate them:
  - *Context granularity* (`context.variants`: normal / long / ultra_long) is
    the axis that produces the **1,482** headline instance count
    (Academic ×2, Finance ×3, Research Report ×1).
  - *Renderer* (`code_types`: python / html) is a separate axis. Both text
    domains actually ship **both** a python and an html gold program
    (`stage2_python` and `stage2_html`); which renderer is scored is an eval
    choice (Phase 4), not part of the headline count.
- **`chart_image == ""`** is legal: it means no pre-rendered `G_GT` is stored and
  the reference chart must be produced by executing `program.stage2_*`. (In
  practice all three domains DO ship a pre-rendered python `G_GT`, so this is
  currently unused but kept for robustness.)
- **`d_der == null`** means the derived table equals the source table (no
  reasoning step beyond extraction) — true for some Academic instances.
- Chinese strings (e.g. `indicator_full`) are preserved verbatim; an optional
  English gloss may be added in a later phase but is **not** required by v1.

---

## 2. Per-domain → canonical mapping

| canonical field | Academic (`json/`) | Finance (`json2/`) | Research Report (`query-level.jsonl`) |
|---|---|---|---|
| `uid` | `academic/{id}` | `finance/{id}` | `research_report/{query_id}` |
| `source.type` | `info.source.type` = `nature` | `info.source.type` = `annual_report` | `source` (cbinsights/…) |
| `source.doc_id` | DOI from `data.paper` path | `info.company` | `report` |
| `source.url` | `info.source.url` | `info.source.url` (often "") | — |
| `info.chart_description` | `info.source.description` | — | — |
| `query.template` | `query` | `query` | `query` |
| `query.code_types` | `["python"]` | `["python"]` | `["python"]` |
| `query.metadata` | — | `info.{company,indicator,indicator_full,start_year,end_year}` | — |
| `context.modality` | `text` | `text` | `multimodal` |
| `context.variants.normal` | `data.paper` | `data.table` (3 statement tables) | `summary` + `src_pdf` |
| `context.variants.long` | (md crop) | `data.table_context` (tables + 10-K context.md) | — |
| `context.variants.ultra_long` | — | `data.complete_report` (full 10-K OCR md) | — |
| `references.d_src` | `ground_truth_table` (.md) | `ground_truth_table` (alpha `.csv`) | `ground_truth.direct_data` (.json) |
| `references.d_der` | stage1 output (json) | `report_py_1_output` (json) | `ground_truth.final_chart_data` (.json) |
| `references.program.stage1_extract` | `nature_1/{id}.py` | `report_py_1/{id}.py` | `ground_truth.reasoning` (.py) |
| `references.program.stage2_python` | `nature/{id}.py` (json `ground_truth_code.py`) | `report_py_2/{id}.py` | `ground_truth.chart_code` (.py) |
| `references.program.stage2_html` (secondary) | `nature_2_html/{id}.html` | `report/{id}.html` | — |
| `references.chart_image` (python-rendered) | `ground_truth_image` (`id-N.png`) | `image/report_py/{id}.png` | `ground_truth.chart_image` (.png) |

### Domain quirks the ETL must absorb (from Phase 0)

- GT directory prefixes `nature_*` / `report_*` → normalize to
  `academic` / `finance`.
- `data.type` is `text_file` (academic) vs `text_files` (finance) → drop; use
  `context.modality` + `variants`.
- Finance is missing stage1 for ids **268, 278, 284, 285, 286, 288** (stage2
  present). Either re-run those 6 or set `program.stage1_extract = null`.
- Exclude draft sets: `json2_pre` (155), `json2_rm`, `json_rm`, `json_back`.

---

## 3. Counts (must hold after ETL)

| domain | base queries | context variants | instances |
|---|---|---|---|
| Academic | 178 | ×2 (normal, long) | 356 |
| Finance | 290 | ×3 (normal, long, ultra_long — all OCR text) | 870 |
| Research Report | 256 | ×1 | 256 |
| **total** | **724** | | **1,482** |

Matches the paper (Table 7). Finance's three variants are **all OCR'd text** at
growing scope (3 tables → tables+context → full 10-K markdown); the raw 10-K PDFs
are source provenance, **not** input, and are not shipped. The canonical jsonl
stores the **724 base records** (`etl/validate.py` checks 178/290/256); the 1,482
is the base × context-variant expansion at eval time.
