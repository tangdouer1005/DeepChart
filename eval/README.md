# Eval — unified harness (Phase 4)

Two-stage generation, then four metrics, over all three domains. All metrics read
the **canonical** `instances/<domain>.jsonl` + `references/`, so one harness
covers academic / finance / research_report uniformly.

## Pipeline

1. **Stage 1 — Extract+Reason** (`run_generation.py`): the model reads a context
   variant + the query and emits a python program that prints/writes a JSON of
   `{src_data, der_data}`. We execute it → `D_src_hat`, `D_der_hat`.
2. **Stage 2 — Visualize**: the model emits a python program; we execute/render it
   to a PNG → `G_hat`.

Outputs land at `outputs/<model>/<domain>/<variant>/<uid_safe>/`
(`stage1.py`, `stage1.json`, `stage2.py`, `chart.png`).

## Metrics (`metrics/`)

| metric | what | module |
|---|---|---|
| **F1_src** | numbers in `D_src_hat` vs gold `references.d_src` | `f1_src.py` (+ `f1.py`) |
| **F1_der** | numbers in `D_der_hat` vs gold `references.d_der` | `f1_der.py` |
| **VAS** | VLM-judged visual accuracy of `G_hat` vs `G_GT`, cached binary rubrics (ic≥5 / dt≥2 / pq≥3), default judge `qwen3-vl-flash` | `vas.py` |
| **ER** | execution rate: does a generated program run & render a valid PNG | `execution_rate.py` |

F1 uses a **bag-of-numbers** match (greedy, `rel_tol=1e-4`), robust to key
renaming/ordering. `f1.py` handles every gold format: JSON keeps structure;
CSV/markdown (academic `d_src` / finance `d_src`) are numeric-tokenized.

## Running

```bash
# structural check — NO model calls, NO cost
python eval/smoke_test.py

# generation (needs an OpenAI-compatible endpoint; see Keys below)
python eval/run_generation.py -d finance --variant normal -m gpt-4o
python eval/run_generation.py -d academic --variant normal -m gpt-4o --dry-run   # prompts only
```

## Keys / endpoint

No keys are hardcoded. `api_key_pool.py` reads, in order: `$OPENAI_API_KEYS_FILE`
/ `$OPENAI_API_KEY_FILE` → a `key` file at repo root (one key per line) →
`$OPENAI_API_KEY`. Base URL from `$OPENAI_BASE_URL`. The pool round-robins keys
and cools one down on 401/403/429. **Never commit the `key` file** (gitignored).

## Notes / known specifics

- **Reference charts (`G_GT`) are pre-rendered** for all three domains
  (academic `id-N.png`, finance `image/report_py`, research_report `chart.png`),
  so VAS does not need to re-run gold programs.
- **research_report gold programs are provenance-only**: they are coupled to the
  original repo's `scripts/*_groundtruth_lib.py` + per-report `_shared.py` and do
  not run standalone. Use the pre-rendered `chart_image` as `G_GT`. (academic &
  finance gold stage2 programs *are* standalone and runnable.)
- The `{code_type}` placeholder in `query.template` is python for all domains
  (see schema/SCHEMA.md). html gold programs are kept as secondary `stage2_html`.
- Multimodal (research_report) stage-1 currently feeds the text summary; feeding
  the source PDF pages as images is a TODO hook in `run_generation.read_context`.
