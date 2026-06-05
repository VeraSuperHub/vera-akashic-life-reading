#!/usr/bin/env python3
"""Run calculator self-tests and validate their JSON envelopes.

This smoke check is intentionally lightweight. It verifies that required local
calculators still emit `{"ok": true}` and that the optional astrology helper
does so when its Kerykeion/PyJHora dependency stack is installed.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent

CHECKS = [
    {
        "name": "bazi",
        "cmd": [sys.executable, str(SCRIPT_DIR / "bazi_profile.py"), "--self-test"],
        "optional": False,
    },
    {
        "name": "numerology",
        "cmd": [sys.executable, str(SCRIPT_DIR / "numerology_profile.py"), "--self-test"],
        "optional": False,
    },
    {
        "name": "ziwei",
        "cmd": ["node", str(SCRIPT_DIR / "ziwei_profile.mjs"), "--self-test"],
        "optional": False,
    },
    {
        "name": "astrology",
        "cmd": [sys.executable, str(SCRIPT_DIR / "astro_profile.py"), "--self-test"],
        "optional": True,
    },
    {
        "name": "full-calculator",
        "cmd": [sys.executable, str(SCRIPT_DIR / "full_calculator.py"), "--self-test"],
        "optional": False,
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Akashic calculator smoke tests.")
    parser.add_argument(
        "--require-optional",
        action="store_true",
        help="Fail when optional calculators such as astrology cannot run.",
    )
    return parser.parse_args()


def load_json(text: str) -> dict[str, Any]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError("self-test output must be a JSON object")
    return data


def _get_astrology_deps() -> dict[str, Any] | None:
    """Run astro_profile.py --check-deps and return parsed JSON, or None.

    --check-deps may exit with code 1 when dependencies are missing, so we
    parse stdout regardless of return code.
    """
    try:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "astro_profile.py"), "--check-deps"],
            cwd=SCRIPT_DIR,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        return json.loads(proc.stdout)
    except Exception:
        pass
    return None


def _astrology_dependency_message(deps: dict[str, Any]) -> str:
    details: list[str] = []
    py_ver = deps.get("python_version", "unknown")
    if not deps.get("python_310_plus", False):
        details.append(f"Python {py_ver} < 3.10 required")
    if not deps.get("kerykeion", False):
        details.append("kerykeion missing")
    if not deps.get("pyjhora", False):
        details.append("PyJHora missing")
    if not deps.get("pyswisseph", False):
        details.append("pyswisseph missing")

    base = str(deps.get("error") or "Optional astrology dependencies are unavailable.")
    if details:
        return f"{base} [dependency check: {'; '.join(details)}]"
    return base


def run_check(check: dict[str, Any], require_optional: bool) -> dict[str, Any]:
    proc = subprocess.run(
        check["cmd"],
        cwd=SCRIPT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    try:
        payload = load_json(proc.stdout)
    except RuntimeError as exc:
        return {
            "name": check["name"],
            "status": "failed",
            "error": str(exc),
            "stderr": proc.stderr.strip(),
        }

    if proc.returncode == 0 and payload.get("ok") is True:
        return {"name": check["name"], "status": "passed"}

    error = str(payload.get("error") or proc.stderr.strip() or f"exit code {proc.returncode}")

    # For astrology failures, surface detailed dependency diagnostics.
    if check["name"] == "astrology":
        deps = _get_astrology_deps()
        if deps is not None:
            dependency_error = _astrology_dependency_message(deps)
            if not deps.get("ok", False):
                error = dependency_error
            else:
                error = f"{error} [dependency check: {dependency_error}]"

    if check["optional"] and not require_optional:
        return {"name": check["name"], "status": "skipped", "reason": error}
    return {"name": check["name"], "status": "failed", "error": error}


def main() -> int:
    args = parse_args()
    results = [run_check(check, args.require_optional) for check in CHECKS]
    failed = [item for item in results if item["status"] == "failed"]
    print(json.dumps({"ok": not failed, "results": results}, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
