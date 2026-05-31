#!/usr/bin/env python3
"""Structural smoke test for the eval harness — makes NO model API calls.

Checks:
  1. All 724 canonical instances load through the schema.
  2. F1 file loaders work on every d_src format (.md/.csv/.json) and d_der(.json):
     scoring a gold file against itself must give F1 == 1.0.
  3. ER pipeline: a few GOLD stage2 programs execute and render a PNG.
  4. VAS module imports and its rubric prompts load (no API call).
  5. run_generation --dry-run builds prompts for a couple of instances.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EVAL_DIR))

from instances import REPO, load_all  # noqa: E402
from metrics.execution_rate import render_python  # noqa: E402
from metrics.f1 import calculate_f1, extract_values_from_file  # noqa: E402

PASS, FAIL = "PASS", "FAIL"
fails = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global fails
    print(f"  [{PASS if ok else FAIL}] {name}{(' — ' + detail) if detail else ''}")
    if not ok:
        fails += 1


def main() -> int:
    data = load_all()
    print("1. instance loading")
    total = sum(len(v) for v in data.values())
    check("724 instances load", total == 724, f"got {total}")

    print("2. F1 file-loader self-consistency (gold vs itself = 1.0)")
    for dom, insts in data.items():
        inst = insts[0]
        sp = REPO / inst.references.d_src
        sv = extract_values_from_file(sp)
        f1s, _, _ = calculate_f1(sv, list(sv))
        check(f"{dom} d_src ({sp.suffix}) self-F1", abs(f1s - 1.0) < 1e-9 and len(sv) > 0,
              f"{len(sv)} values, f1={f1s:.3f}")
        if inst.references.d_der:
            dp = REPO / inst.references.d_der
            dv = extract_values_from_file(dp)
            f1d, _, _ = calculate_f1(dv, list(dv))
            check(f"{dom} d_der (.json) self-F1", abs(f1d - 1.0) < 1e-9, f"{len(dv)} values")

    print("3. ER pipeline / G_GT availability")
    with tempfile.TemporaryDirectory() as tmp:
        # academic & finance gold stage2 programs are standalone -> render them
        for dom in ("academic", "finance"):
            prog = data[dom][0].references.program.stage2_python
            ok, msg = render_python(REPO / prog, Path(tmp) / f"{dom}.png")
            check(f"{dom} gold stage2 renders (standalone)", ok, msg)
        # research_report gold programs are provenance-only (coupled to the
        # original scripts/ libs); its G_GT is the pre-rendered chart_image.
        rr_imgs = [REPO / i.references.chart_image for i in data["research_report"]]
        present = sum(p.exists() and p.stat().st_size >= 1024 for p in rr_imgs)
        check("research_report G_GT images present (pre-rendered)", present == len(rr_imgs),
              f"{present}/{len(rr_imgs)}")

    print("4. VAS module + rubric prompts")
    try:
        from metrics import vas  # noqa: E402
        sysmsg, _ = vas._load_yaml(vas.PROMPT_DIR / "ic.yaml")
        gp = vas.build_gen_parameter("Bar Chart", "plot X")
        check("vas imports + prompts load", bool(sysmsg) and gp["chart_type"] == "Bar Chart")
    except Exception as exc:  # noqa: BLE001
        check("vas imports + prompts load", False, str(exc))

    print("5. run_generation --dry-run")
    try:
        import run_generation as rg  # noqa: E402
        inst = data["academic"][0]
        with tempfile.TemporaryDirectory() as tmp:
            st = rg.process(inst, "normal", None, Path(tmp), dry_run=True)
            built = (Path(tmp) / "academic__1" / "stage1_prompt.txt").exists()
        check("dry-run builds stage1 prompt", st["status"] == "dry_run" and built)
    except Exception as exc:  # noqa: BLE001
        check("dry-run builds stage1 prompt", False, str(exc))

    print(f"\n{'ALL PASS' if fails == 0 else str(fails) + ' FAILED'}")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
