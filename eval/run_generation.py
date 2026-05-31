#!/usr/bin/env python3
"""Two-stage generation driver (Phase 4), unified across all three domains.

For each canonical instance and a chosen context `variant`:

  Stage 1 (Extract+Reason): prompt the model with the context + query; it emits a
    python program that writes a JSON of {src_data, der_data}. We execute it.
  Stage 2 (Visualize): prompt the model with the derived data + query; it emits a
    python program; we execute/render it to a PNG (see metrics.execution_rate).

Outputs land under:
  <output>/<model>/<domain>/<variant>/<uid_safe>/{stage1.py, stage1.json,
                                                   stage2.py, chart.png}
which the metrics in eval/metrics/ then read.

`--dry-run` builds and saves the prompts but makes NO model calls and runs NO
code — used by the structural smoke test (eval/smoke_test.py).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import requests
import yaml
from jinja2 import Template

EVAL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EVAL_DIR))
from api_key_pool import load_api_key_pool, resolve_base_url  # noqa: E402
from instances import load_instances, read_context, uid_safe, REPO  # noqa: E402
from metrics.execution_rate import render_python  # noqa: E402

PROMPTS = EVAL_DIR / "prompts"


def _load_prompt(name: str) -> tuple[str, str]:
    data = yaml.safe_load((PROMPTS / name).read_text(encoding="utf-8"))
    return data.get("system", ""), data.get("user", "")


def clean_code(content: str) -> str:
    content = content.strip()
    m = re.search(r"```python\s*(.*?)\s*```", content, re.DOTALL) or \
        re.search(r"```\s*(.*?)\s*```", content, re.DOTALL)
    if m:
        return m.group(1)
    for fence in ("```python", "```"):
        if content.startswith(fence):
            content = content[len(fence):].strip()
    return content[:-3].strip() if content.endswith("```") else content


class TextLLM:
    def __init__(self, model: str, timeout: int = 600):
        self.model, self.timeout = model, timeout
        self.pool, _ = load_api_key_pool()
        base = resolve_base_url().rstrip("/")
        self.endpoint = base if base.endswith("/chat/completions") else f"{base}/chat/completions"

    def chat(self, system_prompt: str, user_text: str, retries: int = 3) -> str | None:
        payload = {"model": self.model, "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}]}
        for attempt in range(1, retries + 1):
            lease = self.pool.next_key()
            try:
                r = requests.post(self.endpoint, json=payload, timeout=self.timeout,
                                  headers={"Authorization": f"Bearer {lease.api_key}",
                                           "Content-Type": "application/json"})
                r.raise_for_status()
                self.pool.report_success(lease)
                return r.json()["choices"][0]["message"]["content"]
            except Exception as exc:  # noqa: BLE001
                er = getattr(exc, "response", None) or locals().get("r")
                self.pool.report_failure(lease, er.status_code if er is not None else None,
                                         er.text if er is not None else str(exc))
                if attempt < retries:
                    time.sleep(1)
        return None


def build_stage1_prompt(inst, context: str) -> tuple[str, str]:
    system_prompt, user_tpl = _load_prompt("stage1_extract.yaml")
    info = inst.info
    user = Template(user_tpl).render(
        chart_type=info.chart_type or "", chart_purpose=inst.query.template,
        chart_layout=info.chart_type_subclass or "", data=context)
    return system_prompt, user


def build_stage2_prompt(inst, stage1_data: str) -> tuple[str, str]:
    system_prompt, user_tpl = _load_prompt("stage2_visualize.yaml")
    info = inst.info
    user = Template(user_tpl).render(
        chart_type=info.chart_type or "", chart_purpose=inst.query.template,
        chart_layout=info.chart_type_subclass or "", data=stage1_data)
    return system_prompt, user


def process(inst, variant: str, llm: TextLLM | None, out_root: Path, dry_run: bool) -> dict:
    st = {"uid": inst.uid, "stage1_exec": False, "stage2_render": False, "status": "ok"}
    outdir = out_root / uid_safe(inst.uid)
    outdir.mkdir(parents=True, exist_ok=True)
    context = read_context(inst, variant)

    s1_sys, s1_user = build_stage1_prompt(inst, context)
    (outdir / "stage1_prompt.txt").write_text(s1_sys + "\n\n" + s1_user, encoding="utf-8")
    if dry_run:
        st["status"] = "dry_run"
        return st
    if llm is None:
        st["status"] = "no_llm"
        return st

    # ---- Stage 1
    raw1 = llm.chat(s1_sys, s1_user)
    if not raw1:
        st["status"] = "stage1_llm_failed"
        return st
    (outdir / "stage1.py").write_text(clean_code(raw1), encoding="utf-8")
    ok1, _ = render_python(outdir / "stage1.py", outdir / "stage1.out.json")  # script writes json to argv1
    st["stage1_exec"] = (outdir / "stage1.json").exists() or ok1
    stage1_data = ""
    p = outdir / "stage1.json"
    if p.exists():
        stage1_data = p.read_text(encoding="utf-8")

    # ---- Stage 2
    s2_sys, s2_user = build_stage2_prompt(inst, stage1_data or context)
    raw2 = llm.chat(s2_sys, s2_user)
    if not raw2:
        st["status"] = "stage2_llm_failed"
        return st
    (outdir / "stage2.py").write_text(clean_code(raw2), encoding="utf-8")
    ok2, msg = render_python(outdir / "stage2.py", outdir / "chart.png")
    st["stage2_render"] = ok2
    st["render_msg"] = msg
    return st


def main() -> None:
    ap = argparse.ArgumentParser(description="DeepChart two-stage generation driver.")
    ap.add_argument("-d", "--domain", required=True, choices=["academic", "finance", "research_report"])
    ap.add_argument("--variant", default="normal", choices=["normal", "long", "ultra_long"])
    ap.add_argument("-m", "--model", default="gpt-4o")
    ap.add_argument("--output-dir", default=str(REPO / "outputs"))
    ap.add_argument("--limit", type=int, help="Only process the first N instances.")
    ap.add_argument("--dry-run", action="store_true", help="Build prompts only; no model calls, no execution.")
    args = ap.parse_args()

    insts = load_instances(args.domain)
    if args.limit:
        insts = insts[:args.limit]
    out_root = Path(args.output_dir) / args.model / args.domain / args.variant
    llm = None if args.dry_run else TextLLM(args.model)

    results = [process(i, args.variant, llm, out_root, args.dry_run) for i in insts]
    n = len(results)
    print(f"[{args.domain}/{args.variant}] processed {n}")
    if not args.dry_run:
        print(f"  stage1 exec ok: {sum(r['stage1_exec'] for r in results)}/{n}")
        print(f"  stage2 render ok: {sum(r['stage2_render'] for r in results)}/{n}")
    (out_root / "run_summary.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
