#!/usr/bin/env python3
"""Emit normalized BaZi JSON using lunar_python.

This script performs calculation only. It does not generate spiritual
interpretation text.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from importlib import metadata
from pathlib import Path
from typing import Any


VENDOR_DIR = Path(__file__).resolve().parent / "vendor"
if (VENDOR_DIR / "lunar_python").is_dir():
    sys.path.insert(0, str(VENDOR_DIR))

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "synthetic_birth.json"


STEM_ELEMENTS = {
    "甲": "木",
    "乙": "木",
    "丙": "火",
    "丁": "火",
    "戊": "土",
    "己": "土",
    "庚": "金",
    "辛": "金",
    "壬": "水",
    "癸": "水",
}

BRANCH_ELEMENTS = {
    "子": "水",
    "丑": "土",
    "寅": "木",
    "卯": "木",
    "辰": "土",
    "巳": "火",
    "午": "火",
    "未": "土",
    "申": "金",
    "酉": "金",
    "戌": "土",
    "亥": "水",
}

POSITION_LABELS = {
    "year": "年支",
    "month": "月支",
    "day": "日支",
    "hour": "时支",
}

VERIFIED_AUXILIARY_KEYS = {
    "verified_tai_yuan": "验证胎元",
    "verified_ming_gong": "验证命宫",
    "verified_shen_gong": "验证身宫",
}

THREE_MEETINGS = [
    (("亥", "子", "丑"), "水"),
    (("寅", "卯", "辰"), "木"),
    (("巳", "午", "未"), "火"),
    (("申", "酉", "戌"), "金"),
]

THREE_HARMONIES = [
    (("申", "子", "辰"), "水"),
    (("亥", "卯", "未"), "木"),
    (("寅", "午", "戌"), "火"),
    (("巳", "酉", "丑"), "金"),
]

SIX_HARMONIES = {
    ("子", "丑"): "土",
    ("寅", "亥"): "木",
    ("卯", "戌"): "火",
    ("辰", "酉"): "金",
    ("巳", "申"): "水",
    ("午", "未"): "土",
}

CLASHES = [("子", "午"), ("丑", "未"), ("寅", "申"), ("卯", "酉"), ("辰", "戌"), ("巳", "亥")]
HARMS = [("子", "未"), ("丑", "午"), ("寅", "巳"), ("卯", "辰"), ("申", "亥"), ("酉", "戌")]
BREAKS = [("子", "酉"), ("丑", "辰"), ("寅", "亥"), ("卯", "午"), ("巳", "申"), ("未", "戌")]
PUNISHMENT_PAIRS = [("子", "卯")]
PUNISHMENT_TRIPLES = [("寅", "巳", "申"), ("丑", "未", "戌")]
SELF_PUNISH_BRANCHES = {"辰", "午", "酉", "亥"}

CHINESE_HOUR_BOUNDARIES = [
    (23 * 60, "亥", "子"),
    (1 * 60, "子", "丑"),
    (3 * 60, "丑", "寅"),
    (5 * 60, "寅", "卯"),
    (7 * 60, "卯", "辰"),
    (9 * 60, "辰", "巳"),
    (11 * 60, "巳", "午"),
    (13 * 60, "午", "未"),
    (15 * 60, "未", "申"),
    (17 * 60, "申", "酉"),
    (19 * 60, "酉", "戌"),
    (21 * 60, "戌", "亥"),
]


def _load_lunar_python():
    try:
        from lunar_python import Lunar, Solar
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Missing dependency: lunar_python. Install scripts/requirements.txt "
            "or provide verified BaZi data manually."
        ) from exc
    return Lunar, Solar


def _parse_date(value: str) -> tuple[int, int, int]:
    try:
        date = datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("birth_date must use YYYY-MM-DD") from exc
    return date.year, date.month, date.day


def _parse_time(value: str | None) -> tuple[int, int, int]:
    if not value:
        raise ValueError("birth_time is required for a reliable hour pillar")
    formats = ["%H:%M:%S", "%H:%M"]
    for fmt in formats:
        try:
            time = datetime.strptime(value, fmt)
            return time.hour, time.minute, time.second
        except ValueError:
            pass
    raise ValueError("birth_time must use HH:MM or HH:MM:SS")


def _time_boundary_sensitivity(hour: int, minute: int, second: int, threshold_minutes: int = 15) -> dict[str, Any]:
    total_minutes = hour * 60 + minute + second / 60
    closest = None
    for boundary_minutes, from_branch, to_branch in CHINESE_HOUR_BOUNDARIES:
        diff = abs(total_minutes - boundary_minutes)
        circular_diff = min(diff, 1440 - diff)
        if closest is None or circular_diff < closest["minutes_from_boundary"]:
            closest = {
                "boundary_time": f"{boundary_minutes // 60:02d}:{boundary_minutes % 60:02d}",
                "from_branch": from_branch,
                "to_branch": to_branch,
                "minutes_from_boundary": round(circular_diff, 2),
            }
    if closest is None:
        return {"near_chinese_hour_boundary": False, "threshold_minutes": threshold_minutes}
    return {
        "near_chinese_hour_boundary": closest["minutes_from_boundary"] <= threshold_minutes,
        "threshold_minutes": threshold_minutes,
        "closest_boundary": closest,
        "adjustment_prompt": "If birth time is close to this boundary, confirm civil time, true solar time, timezone, and trusted chart source before interpreting the hour pillar.",
    }


def _read_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.self_test:
        return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    if args.input:
        text = Path(args.input).read_text(encoding="utf-8")
    else:
        if sys.stdin.isatty():
            raise ValueError("input JSON is required on stdin or via --input")
        text = sys.stdin.read()
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"input must be JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("input JSON must be an object")
    return payload


def _gender_code(value: Any) -> int | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"1", "m", "male", "man", "男"}:
        return 1
    if text in {"0", "f", "female", "woman", "女"}:
        return 0
    raise ValueError("gender must be male/female, man/woman, 男/女, 1/0, or omitted")


def _maybe_call(obj: Any, method: str) -> Any:
    fn = getattr(obj, method, None)
    if fn is None:
        return None
    try:
        return fn()
    except Exception:
        return None


def _normalize_pillar(value: Any, field: str) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if len(text) != 2 or text[0] not in STEM_ELEMENTS or text[1] not in BRANCH_ELEMENTS:
        raise ValueError(f"{field} must be a two-character stem-branch pillar, such as 甲子")
    return text


def _verified_auxiliary_pillars(payload: dict[str, Any]) -> list[dict[str, Any]]:
    auxiliary = []
    for key, label in VERIFIED_AUXILIARY_KEYS.items():
        pillar = _normalize_pillar(payload.get(key), key)
        if pillar:
            auxiliary.append(
                {
                    "position": key,
                    "label": label,
                    "pillar": pillar,
                    "source": "user_verified",
                }
            )

    for index, item in enumerate(payload.get("auxiliary_pillars") or []):
        if not isinstance(item, dict):
            raise ValueError("auxiliary_pillars entries must be objects")
        pillar = _normalize_pillar(item.get("pillar"), f"auxiliary_pillars[{index}].pillar")
        if not pillar:
            continue
        auxiliary.append(
            {
                "position": str(item.get("position") or f"auxiliary_{index + 1}"),
                "label": str(item.get("label") or "验证辅助柱"),
                "pillar": pillar,
                "source": str(item.get("source") or "user_verified"),
            }
        )
    return auxiliary


def _branch_records(pillars: dict[str, str], auxiliary_pillars: list[dict[str, Any]] | None = None) -> list[dict[str, str]]:
    records = []
    for position in ("year", "month", "day", "hour"):
        pillar = pillars[position]
        records.append(
            {
                "position": position,
                "label": POSITION_LABELS[position],
                "pillar": pillar,
                "stem": pillar[0],
                "branch": pillar[1],
            }
        )
    for item in auxiliary_pillars or []:
        pillar = item["pillar"]
        records.append(
            {
                "position": item["position"],
                "label": item["label"],
                "pillar": pillar,
                "stem": pillar[0],
                "branch": pillar[1],
                "source": item.get("source", "user_verified"),
                "auxiliary": True,
            }
        )
    return records


def _positions_for(records: list[dict[str, str]], branches: tuple[str, ...] | list[str]) -> list[dict[str, str]]:
    wanted = set(branches)
    positions = []
    for item in records:
        if item["branch"] not in wanted:
            continue
        position = {
            "position": item["position"],
            "label": item["label"],
            "pillar": item["pillar"],
            "branch": item["branch"],
        }
        if item.get("source"):
            position["source"] = item["source"]
        if item.get("auxiliary"):
            position["auxiliary"] = True
        positions.append(position)
    return positions


def _pair_present(present: set[str], pair: tuple[str, str]) -> bool:
    return pair[0] in present and pair[1] in present


def _interaction(
    interaction_type: str,
    branches: tuple[str, ...] | list[str],
    records: list[dict[str, str]],
    element: str | None = None,
    strength: str | None = None,
    missing: list[str] | None = None,
) -> dict[str, Any]:
    text = "".join(branches)
    positions = _positions_for(records, branches)
    auxiliary_positions = [position for position in positions if position.get("auxiliary")]
    item: dict[str, Any] = {
        "type": interaction_type,
        "name": text + interaction_type + (element or ""),
        "branches": list(branches),
        "positions": positions,
        "basis": "four_pillars_plus_auxiliary" if auxiliary_positions else "four_pillars_only",
        "involves_auxiliary": bool(auxiliary_positions),
    }
    if auxiliary_positions:
        item["auxiliary_sources"] = sorted(
            {
                str(position.get("position") or position.get("source") or "auxiliary")
                for position in auxiliary_positions
            }
        )
    if element:
        item["element"] = element
    if strength:
        item["strength"] = strength
    if missing:
        item["missing"] = missing
    return item


def _stem_label(item: dict[str, str]) -> str:
    label = item["label"]
    if label.endswith("支"):
        return label[:-1] + "干"
    return label + "天干"


def _detect_bazi_structure(
    simple_pillars: dict[str, str],
    auxiliary_pillars: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    records = _branch_records(simple_pillars, auxiliary_pillars)
    branches = [item["branch"] for item in records]
    present = set(branches)
    branch_counts = {branch: branches.count(branch) for branch in sorted(present)}
    stem_counts: dict[str, int] = {}
    branch_element_counts: dict[str, int] = {}
    stem_element_counts: dict[str, int] = {}
    for item in records:
        stem = item["stem"]
        branch = item["branch"]
        stem_counts[stem] = stem_counts.get(stem, 0) + 1
        stem_element = STEM_ELEMENTS.get(stem)
        branch_element = BRANCH_ELEMENTS.get(branch)
        if stem_element:
            stem_element_counts[stem_element] = stem_element_counts.get(stem_element, 0) + 1
        if branch_element:
            branch_element_counts[branch_element] = branch_element_counts.get(branch_element, 0) + 1

    interactions = []
    for combo, element in THREE_MEETINGS:
        if all(branch in present for branch in combo):
            interactions.append(_interaction("三会", combo, records, element, "full"))

    for combo, element in THREE_HARMONIES:
        if all(branch in present for branch in combo):
            interactions.append(_interaction("三合", combo, records, element, "full"))
            continue
        found = [branch for branch in combo if branch in present]
        if len(found) == 2:
            missing = [branch for branch in combo if branch not in present]
            interactions.append(_interaction("半合", tuple(found), records, element, "partial", missing))

    for pair, element in SIX_HARMONIES.items():
        if _pair_present(present, pair):
            interactions.append(_interaction("六合", pair, records, element, "pair"))

    for pair in CLASHES:
        if _pair_present(present, pair):
            interactions.append(_interaction("冲", pair, records, strength="pair"))

    for pair in HARMS:
        if _pair_present(present, pair):
            interactions.append(_interaction("害", pair, records, strength="pair"))

    for pair in BREAKS:
        if _pair_present(present, pair):
            interactions.append(_interaction("破", pair, records, strength="pair"))

    for pair in PUNISHMENT_PAIRS:
        if _pair_present(present, pair):
            interactions.append(_interaction("刑", pair, records, strength="pair"))

    for combo in PUNISHMENT_TRIPLES:
        if all(branch in present for branch in combo):
            interactions.append(_interaction("三刑", combo, records, strength="full"))

    for branch in SELF_PUNISH_BRANCHES:
        if branch_counts.get(branch, 0) > 1:
            interactions.append(_interaction("自刑", (branch,), records, strength="duplicate"))

    return {
        "basis": "four_pillars_plus_verified_auxiliary" if auxiliary_pillars else "four_pillars",
        "branches": records,
        "stems": [{"position": item["position"], "label": _stem_label(item), "stem": item["stem"]} for item in records],
        "counts": {
            "stems": stem_counts,
            "branches": branch_counts,
            "stem_elements": stem_element_counts,
            "branch_main_elements": branch_element_counts,
        },
        "branch_interactions": interactions,
    }


def _parse_year_list(value: Any) -> list[int]:
    if value is None:
        return []
    if isinstance(value, int):
        return [value]
    if isinstance(value, str):
        values = [part.strip() for part in value.replace("，", ",").split(",") if part.strip()]
    elif isinstance(value, list):
        values = value
    else:
        raise ValueError("target_years must be an integer, string, list, or omitted")
    years = []
    for item in values:
        try:
            years.append(int(item))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"target_years contains a non-year value: {item}") from exc
    return sorted(set(years))


def _liu_nian_rows(da_yun: Any, n: int) -> list[dict[str, Any]]:
    rows = []
    for item in da_yun.getLiuNian(n):
        rows.append(
            {
                "year": item.getYear(),
                "age": item.getAge(),
                "pillar": item.getGanZhi(),
                "xun": item.getXun(),
                "xun_kong": item.getXunKong(),
            }
        )
    return rows


def _pillar_block(eight_char: Any, prefix: str) -> dict[str, Any]:
    return {
        "pillar": _maybe_call(eight_char, f"get{prefix}"),
        "heaven_stem": _maybe_call(eight_char, f"get{prefix}Gan"),
        "earth_branch": _maybe_call(eight_char, f"get{prefix}Zhi"),
        "hidden_stems": _maybe_call(eight_char, f"get{prefix}HideGan"),
        "five_elements": _maybe_call(eight_char, f"get{prefix}WuXing"),
        "nayin": _maybe_call(eight_char, f"get{prefix}NaYin"),
        "ten_god_stem": _maybe_call(eight_char, f"get{prefix}ShiShenGan"),
        "ten_god_branch": _maybe_call(eight_char, f"get{prefix}ShiShenZhi"),
        "terrain": _maybe_call(eight_char, f"get{prefix}DiShi"),
    }


def _yun_block(
    eight_char: Any,
    gender: int | None,
    sect: int,
    target_years: list[int],
    include_all_liu_nian: bool,
) -> dict[str, Any]:
    if gender is None:
        return {
            "available": False,
            "reason": "gender omitted; 大运顺逆 and 起运 not computed",
        }
    yun = eight_char.getYun(gender, sect)
    decades = []
    da_yun_items = yun.getDaYun(10)
    annual_fortunes = []
    for item in da_yun_items:
        decade = {
            "index": item.getIndex(),
            "pillar": item.getGanZhi(),
            "start_year": item.getStartYear(),
            "end_year": item.getEndYear(),
            "start_age": item.getStartAge(),
            "end_age": item.getEndAge(),
        }
        year_count = item.getEndYear() - item.getStartYear() + 1
        if include_all_liu_nian:
            decade["liu_nian"] = _liu_nian_rows(item, year_count)
        for row in _liu_nian_rows(item, year_count):
            if row["year"] in target_years:
                annual_fortunes.append(
                    {
                        **row,
                        "active_decade": {
                            "index": decade["index"],
                            "pillar": decade["pillar"],
                            "start_year": decade["start_year"],
                            "end_year": decade["end_year"],
                            "start_age": decade["start_age"],
                            "end_age": decade["end_age"],
                        },
                    }
                )
        decades.append(decade)

    block = {
        "available": True,
        "gender_code": gender,
        "sect": sect,
        "direction": "forward" if yun.isForward() else "reverse",
        "start": {
            "years": yun.getStartYear(),
            "months": yun.getStartMonth(),
            "days": yun.getStartDay(),
            "hours": yun.getStartHour(),
            "solar": yun.getStartSolar().toYmdHms(),
        },
        "decades": decades,
    }
    if target_years:
        block["target_years"] = target_years
        block["annual_fortunes"] = annual_fortunes
    return block


def build_profile(payload: dict[str, Any]) -> dict[str, Any]:
    Lunar, Solar = _load_lunar_python()
    y, m, d = _parse_date(str(payload.get("birth_date", "")))
    h, mi, s = _parse_time(payload.get("birth_time"))
    calendar = str(payload.get("calendar", "solar")).strip().lower()
    leap = bool(payload.get("is_lunar_leap_month", False))

    if calendar in {"solar", "gregorian", "公历", "阳历"}:
        solar = Solar.fromYmdHms(y, m, d, h, mi, s)
        lunar = solar.getLunar()
    elif calendar in {"lunar", "chinese_lunar", "农历", "阴历"}:
        lunar_month = -m if leap else m
        lunar = Lunar.fromYmdHms(y, lunar_month, d, h, mi, s)
        solar = lunar.getSolar()
    else:
        raise ValueError("calendar must be solar/gregorian or lunar/chinese_lunar")

    eight_char = lunar.getEightChar()
    bazi_sect = int(payload.get("bazi_sect", 2))
    eight_char.setSect(bazi_sect)
    gender = _gender_code(payload.get("gender"))
    yun_sect = int(payload.get("yun_sect", 2))
    target_years = _parse_year_list(payload.get("target_years") or payload.get("liu_nian_years"))
    include_all_liu_nian = bool(payload.get("include_all_liu_nian", False))
    boundary_minutes = int(payload.get("category_boundary_minutes", 15))

    pillars = {
        "year": _pillar_block(eight_char, "Year"),
        "month": _pillar_block(eight_char, "Month"),
        "day": _pillar_block(eight_char, "Day"),
        "hour": _pillar_block(eight_char, "Time"),
    }
    simple_pillars = {key: value["pillar"] for key, value in pillars.items()}
    verified_auxiliary = _verified_auxiliary_pillars(payload)

    try:
        engine_version = metadata.version("lunar_python")
    except metadata.PackageNotFoundError:
        engine_version = getattr(sys.modules.get("lunar_python"), "__version__", "unknown")

    result = {
        "ok": True,
        "mode": "bazi-calculator",
        "engine": {
            "name": "lunar_python",
            "version": engine_version,
            "upstream": "https://github.com/6tail/lunar-python",
        },
        "input": {
            "name": payload.get("name"),
            "calendar": calendar,
            "birth_date": payload.get("birth_date"),
            "birth_time": payload.get("birth_time"),
            "is_lunar_leap_month": leap,
            "gender": payload.get("gender"),
            "timezone": payload.get("timezone"),
            "birth_place": payload.get("birth_place"),
            "verified_auxiliary_pillars": verified_auxiliary,
            "tai_yuan_policy": payload.get("tai_yuan_policy"),
            "premature_birth_note": payload.get("premature_birth_note"),
            "category_boundary_minutes": boundary_minutes,
        },
        "calendar": {
            "solar": solar.toYmdHms(),
            "lunar": lunar.toFullString(),
        },
        "bazi": {
            "pillars": simple_pillars,
            "pillar_details": pillars,
            "structure": _detect_bazi_structure(simple_pillars, verified_auxiliary),
            "verified_auxiliary_pillars": verified_auxiliary,
            "day_master": eight_char.getDayGan(),
            "tai_yuan": eight_char.getTaiYuan(),
            "tai_xi": eight_char.getTaiXi(),
            "ming_gong": eight_char.getMingGong(),
            "shen_gong": eight_char.getShenGong(),
            "boundary_sensitivity": _time_boundary_sensitivity(h, mi, s, boundary_minutes),
        },
        "yun": _yun_block(eight_char, gender, yun_sect, target_years, include_all_liu_nian),
        "calculation_notes": [
            "Birth time is interpreted as the already-correct local civil time supplied by the user.",
            "This helper does not apply timezone conversion, geocoding, or true-solar-time correction.",
            "Confirm edge cases near solar terms, midnight/late Zi hour, or timezone boundaries against a trusted chart source.",
            "BaZi structure detection is symbolic rule extraction only; weigh strength, season, and school-specific rules before interpretation.",
            "User-verified auxiliary pillars such as 胎元 are kept separate from engine-calculated values; do not silently merge conflicting schools.",
            "Engine-calculated 胎元 is unadjusted; ask whether the user wants to provide an adjusted/verified 胎元 when premature birth or gestational school policy matters.",
            "Hour-pillar categorization is lossy near Chinese-hour boundaries; confirm civil time, true solar time, timezone, and trusted chart source before interpreting boundary-sensitive cases.",
        ],
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate normalized BaZi JSON.")
    parser.add_argument("--input", help="Path to input JSON. Reads stdin when omitted.")
    parser.add_argument("--self-test", action="store_true", help="Run a known upstream test case.")
    args = parser.parse_args()
    try:
        result = build_profile(_read_payload(args))
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    if args.self_test:
        expected = {"year": "庚辰", "month": "甲申", "day": "丙午", "hour": "庚寅"}
        if result["bazi"]["pillars"] != expected:
            print(json.dumps({"ok": False, "error": "self-test mismatch", "result": result}, ensure_ascii=False, indent=2))
            return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
