#!/usr/bin/env python3
"""ER — execution rate: does a generated (or gold) program run and emit a chart?

Two renderers, mirroring the original two-step pipeline:
  - python : run the script (matplotlib forced to the Agg backend); the script
             is expected to write its figure to argv[1], but we also detect any
             PNG it drops in the working dir as a fallback.
  - html   : render the file in headless Chromium via Playwright and screenshot.

`render()` returns (ok, message). A min-size check rejects blank/empty images.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

MIN_IMAGE_BYTES = 1024
DEFAULT_TIMEOUT = 60


def render_python(py_path: str | Path, out_png: str | Path, timeout: int = DEFAULT_TIMEOUT) -> tuple[bool, str]:
    py_path, out_png = Path(py_path).resolve(), Path(out_png)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, MPLBACKEND="Agg")
    with tempfile.TemporaryDirectory() as work:
        try:
            proc = subprocess.run(
                [sys.executable, str(py_path), str(out_png.resolve())],
                capture_output=True, text=True, timeout=timeout, cwd=work, env=env,
            )
        except subprocess.TimeoutExpired:
            return False, "timeout"
        except Exception as exc:  # noqa: BLE001
            return False, f"error: {exc}"
        if _valid(out_png):
            return True, "ok"
        # fallback: the script may have saved a PNG in its cwd
        for cand in Path(work).rglob("*.png"):
            if _valid(cand):
                cand.replace(out_png)
                return True, "ok (cwd png)"
        if proc.returncode != 0:
            return False, f"exit {proc.returncode}: {proc.stderr.strip()[:200]}"
        return False, "no image produced"


def render_html(html_path: str | Path, out_png: str | Path, timeout: int = DEFAULT_TIMEOUT) -> tuple[bool, str]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False, "playwright not installed"
    html_path, out_png = Path(html_path), Path(out_png)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1200, "height": 900})
            page.goto(html_path.resolve().as_uri(), timeout=timeout * 1000)
            page.wait_for_timeout(1500)
            page.screenshot(path=str(out_png), full_page=True)
            browser.close()
    except Exception as exc:  # noqa: BLE001
        return False, f"error: {exc}"
    return (_valid(out_png), "ok" if _valid(out_png) else "blank image")


def render(program_path: str | Path, code_type: str, out_png: str | Path, timeout: int = DEFAULT_TIMEOUT) -> tuple[bool, str]:
    if code_type == "python":
        return render_python(program_path, out_png, timeout)
    if code_type == "html":
        return render_html(program_path, out_png, timeout)
    return False, f"unknown code_type: {code_type}"


def _valid(png: str | Path) -> bool:
    png = Path(png)
    return png.exists() and png.stat().st_size >= MIN_IMAGE_BYTES
