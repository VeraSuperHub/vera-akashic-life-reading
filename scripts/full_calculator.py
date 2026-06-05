#!/usr/bin/env python3
"""Orchestrate Akashic calculator helpers into one JSON envelope.

This script performs calculation orchestration only. It does not interpret
chart facts or generate spiritual narrative.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
FIXTURE_PATH = SCRIPT_DIR / "fixtures" / "synthetic_birth.json"

CALCULATORS = {
    "bazi": {
        "mode": "bazi-calculator",
        "cmd": [sys.executable, str(SCRIPT_DIR / "bazi_profile.py")],
        "optional_dependency": False,
    },
    "ziwei": {
        "mode": "ziwei-calculator",
        "cmd": ["node", str(SCRIPT_DIR / "ziwei_profile.mjs")],
        "optional_dependency": False,
    },
    "numerology": {
        "mode": "numerology-calculator",
        "cmd": [sys.executable, str(SCRIPT_DIR / "numerology_profile.py")],
        "optional_dependency": False,
    },
    "astrology": {
        "mode": "astrology-calculator",
        "cmd": [sys.executable, str(SCRIPT_DIR / "astro_profile.py")],
        "optional_dependency": True,
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Akashic calculators and collect JSON outputs.")
    parser.add_argument("--input", help="Path to input JSON. Reads stdin when omitted.")
    parser.add_argument("--self-test", action="store_true", help="Run shared synthetic fixture.")
    parser.add_argument(
        "--systems",
        help="Comma-separated calculator names to run. Defaults to bazi,ziwei,numerology,astrology.",
    )
    parser.add_argument(
        "--require-optional",
        action="store_true",
        help="Treat optional-dependency calculator failures as hard failures.",
    )
    return parser.parse_args()


def load_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.self_test:
        text = FIXTURE_PATH.read_text(encoding="utf-8")
    elif args.input:
        text = Path(args.input).read_text(encoding="utf-8")
    else:
        if sys.stdin.isatty():
            raise ValueError("input JSON is required on stdin or via --input")
        text = sys.stdin.read()
    payload = json.loads(text)
    if not isinstance(payload, dict):
        raise ValueError("input JSON must be an object")
    return payload


def requested_systems(args: argparse.Namespace) -> list[str]:
    if not args.systems:
        return ["bazi", "ziwei", "numerology", "astrology"]
    systems = [item.strip().lower() for item in args.systems.split(",") if item.strip()]
    unknown = [item for item in systems if item not in CALCULATORS]
    if unknown:
        raise ValueError(f"unknown calculator(s): {', '.join(unknown)}")
    return systems


def parse_json_output(text: str) -> dict[str, Any]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid JSON output: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError("calculator output must be a JSON object")
    return data


def run_calculator(name: str, payload: dict[str, Any], require_optional: bool) -> dict[str, Any]:
    config = CALCULATORS[name]
    proc = subprocess.run(
        config["cmd"],
        input=json.dumps(payload, ensure_ascii=False),
        cwd=SCRIPT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    try:
        output = parse_json_output(proc.stdout)
    except RuntimeError as exc:
        return {
            "status": "failed",
            "optional_dependency": config["optional_dependency"],
            "mode": config["mode"],
            "error": str(exc),
            "stderr": proc.stderr.strip(),
        }

    if proc.returncode == 0 and output.get("ok") is True:
        return {
            "status": "ok",
            "optional_dependency": config["optional_dependency"],
            "mode": config["mode"],
            "data": output,
        }

    error = str(output.get("error") or proc.stderr.strip() or f"exit code {proc.returncode}")
    status = "unavailable" if config["optional_dependency"] and not require_optional else "failed"
    return {
        "status": status,
        "optional_dependency": config["optional_dependency"],
        "mode": config["mode"],
        "error": error,
        "data": output,
    }


def build_profile(payload: dict[str, Any], systems: list[str], require_optional: bool) -> dict[str, Any]:
    calculators = {name: run_calculator(name, payload, require_optional) for name in systems}
    verified_outputs = {
        name: item["data"]
        for name, item in calculators.items()
        if item["status"] == "ok" and isinstance(item.get("data"), dict)
    }
    failed = [name for name, item in calculators.items() if item["status"] == "failed"]
    unavailable = [name for name, item in calculators.items() if item["status"] == "unavailable"]

    ok = bool(verified_outputs) and not failed
    return {
        "ok": ok,
        "mode": "full-calculator",
        "input": {
            "name": payload.get("name"),
            "calendar": payload.get("calendar"),
            "birth_date": payload.get("birth_date"),
            "birth_time": payload.get("birth_time"),
            "gender": payload.get("gender"),
            "timezone": payload.get("timezone"),
            "latitude": payload.get("latitude"),
            "longitude": payload.get("longitude"),
            "systems": systems,
        },
        "verified_outputs": verified_outputs,
        "calculators": calculators,
        "failed": failed,
        "unavailable": unavailable,
        "calculation_notes": [
            "This envelope collects deterministic helper outputs only; interpretation must happen in the skill layer after user confirmation.",
            "Use the full-calculator survivor pattern: failed or unavailable systems cannot support claims, while successful systems remain usable after disclosure.",
            "Astrology is optional unless --require-optional is set because it depends on the user-installed Kerykeion/PyJHora/pyswisseph stack and related licensing.",
        ],
    }


def main() -> int:
    args = parse_args()
    try:
        payload = load_payload(args)
        result = build_profile(payload, requested_systems(args), args.require_optional)
    except Exception as exc:
        print(json.dumps({"ok": False, "mode": "full-calculator", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    if args.self_test:
        required = {"bazi", "ziwei", "numerology"}
        if not required <= set(result["verified_outputs"]):
            result["ok"] = False
            result["error"] = "self-test missing required verified outputs"
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
