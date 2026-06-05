#!/usr/bin/env python3
"""Emit normalized numerology JSON from date fields.

This script performs simple arithmetic only. It does not generate spiritual
interpretation text and does not infer identity from a name.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "synthetic_birth.json"

MASTER_NUMBERS = {11, 22, 33}

CORE_MEANINGS = {
    1: "initiative, self-definition, and beginning",
    2: "sensitivity, relationship, and cooperation",
    3: "expression, language, and creative play",
    4: "structure, discipline, and embodiment",
    5: "freedom, change, and lived experience",
    6: "care, responsibility, beauty, and repair",
    7: "inquiry, solitude, depth, and truth-seeking",
    8: "power, resources, authority, and building",
    9: "completion, compassion, service, and release",
    11: "heightened intuition, transmission, and spiritual sensitivity",
    22: "large-scale building, stewardship, and practical vision",
    33: "service, teaching, healing, and collective care",
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Calculate normalized numerology JSON.")
    parser.add_argument("--input", help="Path to input JSON. Reads stdin when omitted.")
    parser.add_argument("--self-test", action="store_true", help="Run a synthetic date calculation.")
    return parser.parse_args()


def _read_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.self_test:
        return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    if args.input:
        text = Path(args.input).read_text(encoding="utf-8")
    else:
        if sys.stdin.isatty():
            raise ValueError("input JSON is required on stdin or via --input")
        text = sys.stdin.read()
    payload = json.loads(text)
    if not isinstance(payload, dict):
        raise ValueError("input JSON must be an object")
    return payload


def _parse_birth_date(value: Any) -> datetime:
    try:
        return datetime.strptime(str(value), "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("birth_date must use YYYY-MM-DD") from exc


def _reduce(value: int, preserve_master: bool = True) -> dict[str, Any]:
    steps = [value]
    current = value
    while current > 9 and not (preserve_master and current in MASTER_NUMBERS):
        current = sum(int(char) for char in str(current))
        steps.append(current)
    return {
        "compound": value,
        "reduced": current,
        "display": f"{value}/{current}" if value != current else str(current),
        "reduction_steps": steps,
        "is_master_number": current in MASTER_NUMBERS,
        "meaning": CORE_MEANINGS.get(current, ""),
    }


def _digits(text: str) -> list[int]:
    return [int(char) for char in text if char.isdigit()]


def build_profile(payload: dict[str, Any]) -> dict[str, Any]:
    birth_date = _parse_birth_date(payload.get("birth_date"))
    date_digits = _digits(birth_date.strftime("%Y%m%d"))
    birthday = birth_date.day
    attitude_seed = birth_date.month + birth_date.day

    result = {
        "ok": True,
        "mode": "numerology-calculator",
        "engine": {
            "name": "vera-numerology-arithmetic",
            "version": "1.0.0",
        },
        "input": {
            "name": payload.get("name"),
            "birth_date": payload.get("birth_date"),
        },
        "numerology": {
            "life_path": _reduce(sum(date_digits)),
            "birthday_number": _reduce(birthday),
            "attitude_number": _reduce(attitude_seed),
        },
        "calculation_notes": [
            "Life Path uses the full-date digit-sum convention: sum all YYYYMMDD digits, then reduce while preserving master numbers 11, 22, and 33.",
            "Some numerology schools reduce year, month, and day separately before final summing; this helper does not use that component-first convention.",
            "Birthday Number is the day-of-month reduced with the same master-number convention.",
            "Attitude Number is month plus day, included as an optional secondary lens.",
            "Expression/Destiny Number is not calculated unless a user explicitly supplies a Latin-script full birth name and asks for that school.",
            "Use numerology as a symbolic supplemental layer, not as proof or deterministic diagnosis.",
        ],
    }
    return result


def main() -> int:
    args = _parse_args()
    try:
        result = build_profile(_read_payload(args))
        if args.self_test:
            if result["numerology"]["life_path"]["reduced"] != 8:
                raise RuntimeError("self-test mismatch")
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
