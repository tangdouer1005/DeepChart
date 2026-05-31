#!/usr/bin/env python3
"""VAS — VLM-judged Visual Accuracy Score (ported from code/eval/vlm_eval.py).

Two phases, both via a VLM judge (default qwen3-vl-flash):
  1. RUBRIC GENERATION (cached): from the GOLD chart image + a gen_parameter
     descriptor, the judge writes binary yes/no questions in three groups —
     instruction_compliance (ic, >=5), data_mapping_topology (dt, >=2),
     presentation_quality (pq, >=3). Cached per sample so it is generated once.
  2. JUDGING: each rubric question is asked against the GENERATED image; VAS =
     fraction answered "Yes" (with per-group ic/dt/pq sub-scores).

The judge client uses the migrated `eval/api_key_pool.py` (keys from a key file
or OPENAI_API_KEY; never hardcoded). Prompts live in eval/prompts/vlm_eval/.
"""
from __future__ import annotations

import base64
import json
import sys
import time
from pathlib import Path
from typing import Any

import requests
import yaml

EVAL_DIR = Path(__file__).resolve().parent.parent          # .../eval
PROMPT_DIR = EVAL_DIR / "prompts" / "vlm_eval"
sys.path.insert(0, str(EVAL_DIR))
from api_key_pool import ApiKeyPool, load_api_key_pool, resolve_base_url  # noqa: E402

DEFAULT_EVAL_MODEL = "qwen3-vl-flash"
DEFAULT_TIMEOUT = 600

QUESTION_GROUPS = {
    "instruction_compliance": {"prefix": "ic", "min_count": 5, "prompt": "ic.yaml"},
    "data_mapping_topology": {"prefix": "dt", "min_count": 2, "prompt": "dm.yaml"},
    "presentation_quality": {"prefix": "pq", "min_count": 3, "prompt": "pq.yaml"},
}


# --------------------------------------------------------------------------- io
def _load_yaml(path: Path) -> tuple[str, str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data.get("system", ""), data.get("user", "")


def _encode(image_path: Path) -> str:
    return base64.b64encode(Path(image_path).read_bytes()).decode("utf-8")


def _endpoint(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    if base.endswith("/v1") or "/v1/" in base:
        return f"{base}/chat/completions"
    return f"{base}/v1/chat/completions"


def _content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            str(it.get("text", "")) for it in content
            if isinstance(it, dict) and (it.get("type") == "text" or "text" in it)
        )
    return str(content)


# ----------------------------------------------------------------- judge client
class VlmJudge:
    def __init__(self, model: str = DEFAULT_EVAL_MODEL, timeout: int = DEFAULT_TIMEOUT):
        self.model = model
        self.timeout = timeout
        self.pool, self.key_source = load_api_key_pool()
        self.base_url = resolve_base_url()
        self.ask_system, self.ask_user = _load_yaml(PROMPT_DIR / "ask_vlm.yaml")

    def _post(self, system_prompt: str, user_text: str, image_path: Path, max_retries: int = 3,
              temperature: float | None = None) -> str | None:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": user_text},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/png;base64,{_encode(image_path)}"}},
                ]},
            ],
        }
        if temperature is not None:
            payload["temperature"] = temperature
        endpoint = _endpoint(self.base_url)
        for attempt in range(1, max_retries + 1):
            lease = self.pool.next_key()
            try:
                resp = requests.post(
                    endpoint, json=payload, timeout=self.timeout,
                    headers={"Authorization": f"Bearer {lease.api_key}",
                             "Content-Type": "application/json"})
                resp.raise_for_status()
                self.pool.report_success(lease)
                return _content_text(resp.json().get("choices", [{}])[0]
                                     .get("message", {}).get("content", "")).strip()
            except Exception as exc:  # noqa: BLE001
                er = getattr(exc, "response", None) or locals().get("resp")
                code = er.status_code if er is not None else None
                self.pool.report_failure(lease, code, er.text if er is not None else str(exc))
                if attempt < max_retries:
                    time.sleep(1)
        return None

    def gen_questions_json(self, system_prompt: str, user_text: str, gt_image: Path) -> dict | None:
        raw = self._post(system_prompt, user_text, gt_image)
        if raw is None:
            return None
        for candidate in _json_candidates(raw):
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue
        return None

    def ask_yes_no(self, question: str, gen_image: Path) -> str:
        user_text = self.ask_user.format(question=question, image="[Image Provided Below]")
        out = self._post(self.ask_system, user_text, gen_image, temperature=0.0)
        if out is None:
            return "Error"
        low = out.lower()
        return "Yes" if low.startswith("yes") else "No" if low.startswith("no") else "Error"


def _json_candidates(text: str):
    yield text
    t = text.strip()
    if t.startswith("```"):
        body = t.split("```")
        if len(body) > 1:
            seg = body[1]
            yield seg[4:].strip() if seg.startswith("json") else seg.strip()
    s, e = t.find("{"), t.rfind("}")
    if s != -1 and e > s:
        yield t[s:e + 1]


# ------------------------------------------------------------------- rubric mgmt
def _normalize(qs: Any) -> dict[str, str]:
    if not isinstance(qs, dict):
        return {}
    return {str(k).strip(): str(v).strip() for k, v in qs.items() if str(k).strip() and str(v).strip()}


def _missing_groups(questions: dict[str, str]) -> list[str]:
    counts: dict[str, int] = {}
    for key in questions:
        counts[key.split("_", 1)[0]] = counts.get(key.split("_", 1)[0], 0) + 1
    return [cat for cat, cfg in QUESTION_GROUPS.items()
            if counts.get(cfg["prefix"], 0) < cfg["min_count"]]


def ensure_rubric(judge: VlmJudge, gt_image: Path, gen_parameter: dict, cache_path: Path) -> dict[str, str]:
    """Generate (or load cached) rubric questions for a sample."""
    combined: dict[str, str] = {}
    if cache_path.exists():
        try:
            combined = _normalize(json.loads(cache_path.read_text(encoding="utf-8")).get("evaluation_questions"))
            if not _missing_groups(combined):
                return combined
        except Exception:  # noqa: BLE001
            combined = {}

    gp_str = json.dumps(gen_parameter, indent=2, ensure_ascii=False)
    for cat in _missing_groups(combined):
        cfg = QUESTION_GROUPS[cat]
        system_prompt, user_prompt = _load_yaml(PROMPT_DIR / cfg["prompt"])
        user_text = user_prompt.format(gen_parameter=gp_str, image="[Image provided separately]")
        qs = judge.gen_questions_json(system_prompt, user_text, gt_image)
        if isinstance(qs, dict):
            prefix = cfg["prefix"]
            combined = {k: v for k, v in combined.items() if not k.startswith(f"{prefix}_")}
            for k, v in _normalize(qs).items():
                combined[k if k.startswith(f"{prefix}_") else f"{prefix}_{k}"] = v

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(
        {"gen_parameter": gen_parameter, "evaluation_questions": combined},
        ensure_ascii=False, indent=2), encoding="utf-8")
    return combined if not _missing_groups(combined) else {}


# --------------------------------------------------------------------- scoring
def score(gt_image: str | Path, gen_image: str | Path, gen_parameter: dict,
          cache_path: str | Path, judge: VlmJudge | None = None) -> dict[str, Any]:
    """VAS for one sample. Returns accuracy + ic/dt/pq sub-scores + status."""
    judge = judge or VlmJudge()
    gt_image, gen_image, cache_path = Path(gt_image), Path(gen_image), Path(cache_path)
    res = {"status": "ok", "accuracy": 0.0, "ic_score": 0.0, "dt_score": 0.0, "pq_score": 0.0}

    if not gt_image.exists():
        res["status"] = "gt_image_missing"
        return res
    rubric = ensure_rubric(judge, gt_image, gen_parameter, cache_path)
    if not rubric:
        res["status"] = "questions_missing"
        return res
    if not gen_image.exists() or gen_image.stat().st_size < 1024:
        res["status"] = "image_missing"
        return res

    counts = {"ic": [0, 0], "dt": [0, 0], "pq": [0, 0]}
    yes = total = 0
    for qid, question in rubric.items():
        prefix = qid.split("_")[0]
        ans = judge.ask_yes_no(question, gen_image)
        if ans == "Error":
            continue
        counts.setdefault(prefix, [0, 0])
        counts[prefix][1] += 1
        total += 1
        if ans == "Yes":
            counts[prefix][0] += 1
            yes += 1
    for prefix in ("ic", "dt", "pq"):
        y, t = counts[prefix]
        res[f"{prefix}_score"] = y / t if t else 0.0
    res["accuracy"] = yes / total if total else 0.0
    return res


def build_gen_parameter(chart_type: str, query: str) -> dict[str, str]:
    """Minimal descriptor the rubric prompts expect (chart_type/purpose/layout)."""
    ct = (chart_type or "").lower()
    layout = ("xy" if ("scatter" in ct or "bubble" in ct)
              else "matrix" if "heatmap" in ct
              else "cartesian" if ("line" in ct or "area" in ct)
              else "horizontal")
    return {"chart_type": chart_type or "bar", "chart_purpose": query, "chart_layout": layout}
