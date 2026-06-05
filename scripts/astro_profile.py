#!/usr/bin/env python3
"""Emit normalized modern, traditional, and Vedic-style astrology JSON.

This script performs calculation only. It does not generate spiritual
interpretation text.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from importlib import metadata
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "synthetic_birth.json"

SIGNS = [
    ("Aries", "白羊"),
    ("Taurus", "金牛"),
    ("Gemini", "双子"),
    ("Cancer", "巨蟹"),
    ("Leo", "狮子"),
    ("Virgo", "处女"),
    ("Libra", "天秤"),
    ("Scorpio", "天蝎"),
    ("Sagittarius", "射手"),
    ("Capricorn", "摩羯"),
    ("Aquarius", "水瓶"),
    ("Pisces", "双鱼"),
]

PLANETS = [
    ("Sun", "太阳", "SUN"),
    ("Moon", "月亮", "MOON"),
    ("Mercury", "水星", "MERCURY"),
    ("Venus", "金星", "VENUS"),
    ("Mars", "火星", "MARS"),
    ("Jupiter", "木星", "JUPITER"),
    ("Saturn", "土星", "SATURN"),
    ("Uranus", "天王星", "URANUS"),
    ("Neptune", "海王星", "NEPTUNE"),
    ("Pluto", "冥王星", "PLUTO"),
    ("True Node", "北交点", "TRUE_NODE"),
]

TRADITIONAL_PLANETS = {"Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"}

NAKSHATRAS = [
    ("Ashwini", "Ketu"),
    ("Bharani", "Venus"),
    ("Krittika", "Sun"),
    ("Rohini", "Moon"),
    ("Mrigashira", "Mars"),
    ("Ardra", "Rahu"),
    ("Punarvasu", "Jupiter"),
    ("Pushya", "Saturn"),
    ("Ashlesha", "Mercury"),
    ("Magha", "Ketu"),
    ("Purva Phalguni", "Venus"),
    ("Uttara Phalguni", "Sun"),
    ("Hasta", "Moon"),
    ("Chitra", "Mars"),
    ("Swati", "Rahu"),
    ("Vishakha", "Jupiter"),
    ("Anuradha", "Saturn"),
    ("Jyeshtha", "Mercury"),
    ("Mula", "Ketu"),
    ("Purva Ashadha", "Venus"),
    ("Uttara Ashadha", "Sun"),
    ("Shravana", "Moon"),
    ("Dhanishta", "Mars"),
    ("Shatabhisha", "Rahu"),
    ("Purva Bhadrapada", "Jupiter"),
    ("Uttara Bhadrapada", "Saturn"),
    ("Revati", "Mercury"),
]

SIGN_INDEX = {name: index for index, (name, _label) in enumerate(SIGNS)}
PLANET_LABELS = {name: label for name, label, _constant_name in PLANETS}

TRADITIONAL_RULERS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

DOMICILE_SIGNS = {
    "Sun": {"Leo"},
    "Moon": {"Cancer"},
    "Mercury": {"Gemini", "Virgo"},
    "Venus": {"Taurus", "Libra"},
    "Mars": {"Aries", "Scorpio"},
    "Jupiter": {"Sagittarius", "Pisces"},
    "Saturn": {"Capricorn", "Aquarius"},
}

EXALTATION_SIGNS = {
    "Sun": "Aries",
    "Moon": "Taurus",
    "Mercury": "Virgo",
    "Venus": "Pisces",
    "Mars": "Capricorn",
    "Jupiter": "Cancer",
    "Saturn": "Libra",
}

DIGNITY_LABELS = {
    "domicile": "入庙",
    "detriment": "失势",
    "exaltation": "入旺",
    "fall": "落陷",
    "neutral": "平",
    "not_evaluated": "未评估",
}

HOUSE_ANGULARITY = {
    1: "angular",
    2: "succedent",
    3: "cadent",
    4: "angular",
    5: "succedent",
    6: "cadent",
    7: "angular",
    8: "succedent",
    9: "cadent",
    10: "angular",
    11: "succedent",
    12: "cadent",
}

PLANET_SECT = {
    "Sun": "day",
    "Jupiter": "day",
    "Saturn": "day",
    "Moon": "night",
    "Venus": "night",
    "Mars": "night",
    "Mercury": "variable",
}

HOUSE_NAME_TO_NUMBER = {
    "First_House": 1,
    "Second_House": 2,
    "Third_House": 3,
    "Fourth_House": 4,
    "Fifth_House": 5,
    "Sixth_House": 6,
    "Seventh_House": 7,
    "Eighth_House": 8,
    "Ninth_House": 9,
    "Tenth_House": 10,
    "Eleventh_House": 11,
    "Twelfth_House": 12,
}

HOUSE_ATTRS = [
    "first_house",
    "second_house",
    "third_house",
    "fourth_house",
    "fifth_house",
    "sixth_house",
    "seventh_house",
    "eighth_house",
    "ninth_house",
    "tenth_house",
    "eleventh_house",
    "twelfth_house",
]

KERYKEION_PLANETS = [
    ("Sun", "太阳", "sun"),
    ("Moon", "月亮", "moon"),
    ("Mercury", "水星", "mercury"),
    ("Venus", "金星", "venus"),
    ("Mars", "火星", "mars"),
    ("Jupiter", "木星", "jupiter"),
    ("Saturn", "土星", "saturn"),
    ("Uranus", "天王星", "uranus"),
    ("Neptune", "海王星", "neptune"),
    ("Pluto", "冥王星", "pluto"),
    ("True Node", "北交点", "true_north_lunar_node"),
]

KERYKEION_ACTIVE_POINTS = [
    "Sun",
    "Moon",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
    "True_North_Lunar_Node",
    "Ascendant",
    "Medium_Coeli",
    "Pars_Fortunae",
    "Pars_Spiritus",
]

KERYKEION_NAME_ALIASES = {
    "True_North_Lunar_Node": "True Node",
    "Mean_North_Lunar_Node": "Mean Node",
    "Pars_Fortunae": "Part of Fortune",
    "Pars_Spiritus": "Part of Spirit",
}

ASPECT_LABELS = {
    "conjunction": "合相",
    "sextile": "六合",
    "square": "刑相",
    "trine": "拱相",
    "opposition": "冲相",
}

VEDIC_PLANET_LABELS = {
    "L": ("Lagna", "上升"),
    0: ("Sun", "太阳"),
    1: ("Moon", "月亮"),
    2: ("Mars", "火星"),
    3: ("Mercury", "水星"),
    4: ("Jupiter", "木星"),
    5: ("Venus", "金星"),
    6: ("Saturn", "土星"),
    7: ("Rahu", "罗睺"),
    8: ("Ketu", "计都"),
    9: ("Uranus", "天王星"),
    10: ("Neptune", "海王星"),
    11: ("Pluto", "冥王星"),
}


def _load_kerykeion():
    try:
        from kerykeion import AspectsFactory, AstrologicalSubjectFactory
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Missing dependency: kerykeion. Install scripts/requirements-astro.txt "
            "or provide verified Western/古占 chart data manually."
        ) from exc
    try:
        version = metadata.version("kerykeion")
    except metadata.PackageNotFoundError:
        version = "unknown"
    return AstrologicalSubjectFactory, AspectsFactory, version


def _load_pyjhora():
    try:
        with redirect_stdout(io.StringIO()):
            from jhora import const, utils
            from jhora.horoscope.chart import charts
            from jhora.horoscope.dhasa.graha import vimsottari
            from jhora.panchanga import drik
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Missing dependency for PyJHora: "
            f"{exc.name}. Install scripts/requirements-astro.txt or provide verified 印占/Jyotish data manually."
        ) from exc
    except TypeError as exc:
        if sys.version_info < (3, 10):
            raise RuntimeError(
                "PyJHora requires Python 3.10 or newer. Run this helper with a newer Python "
                "or provide verified 印占/Jyotish data manually."
            ) from exc
        raise RuntimeError(f"Could not import PyJHora: {exc}") from exc
    try:
        version = metadata.version("PyJHora")
    except metadata.PackageNotFoundError:
        version = "unknown"
    return const, utils, charts, vimsottari, drik, version


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Calculate normalized astrology JSON.")
    parser.add_argument("--input", help="Path to input JSON. Reads stdin when omitted.")
    parser.add_argument("--self-test", action="store_true", help="Run a synthetic chart calculation.")
    parser.add_argument("--check-deps", action="store_true", help="Check if astrology dependencies are available without calculating.")
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


def _parse_date_time(payload: dict[str, Any]) -> datetime:
    date_text = str(payload.get("birth_date", ""))
    time_text = str(payload.get("birth_time", ""))
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(f"{date_text} {time_text}", fmt)
        except ValueError:
            pass
    raise ValueError("birth_date must use YYYY-MM-DD and birth_time must use HH:MM or HH:MM:SS")


def _parse_timezone(value: Any) -> timezone | ZoneInfo:
    if value is None:
        raise ValueError("timezone is required for astrology calculation")
    text = str(value).strip()
    if text.upper().startswith("UTC"):
        text = text[3:]
    if text in {"Z", "+00:00", "-00:00", ""}:
        return timezone.utc
    if text[0] in {"+", "-"}:
        sign = 1 if text[0] == "+" else -1
        rest = text[1:]
        if ":" in rest:
            hour_text, minute_text = rest.split(":", 1)
        else:
            hour_text, minute_text = rest, "0"
        return timezone(sign * timedelta(hours=int(hour_text), minutes=int(minute_text)))
    try:
        return ZoneInfo(text)
    except Exception as exc:
        raise ValueError("timezone must be an IANA name such as Asia/Shanghai or an offset such as +08:00") from exc


def _coordinates(payload: dict[str, Any]) -> tuple[float, float]:
    lat = payload.get("latitude")
    lon = payload.get("longitude")
    coords = payload.get("coordinates")
    if isinstance(coords, dict):
        lat = coords.get("latitude", lat)
        lon = coords.get("longitude", lon)
    if lat is None or lon is None:
        raise ValueError("latitude and longitude are required for ascendant, houses, and Vedic lagna")
    return float(lat), float(lon)


def _timezone_is_fixed_offset(value: Any) -> bool:
    if value is None:
        return False
    text = str(value).strip()
    if not text:
        return False
    return text.upper().startswith("UTC") or text in {"Z", "+00:00", "-00:00"} or text[0] in {"+", "-"}


def _kerykeion_birth_args(local_dt: datetime, timezone_value: Any) -> tuple[datetime, str]:
    if _timezone_is_fixed_offset(timezone_value):
        return local_dt.astimezone(timezone.utc).replace(tzinfo=None), "UTC"
    return local_dt.replace(tzinfo=None), str(timezone_value).strip()


def _timezone_offset_hours(local_dt: datetime) -> float:
    offset = local_dt.utcoffset()
    if offset is None:
        raise ValueError("timezone offset could not be resolved for Vedic calculation")
    return offset.total_seconds() / 3600


def _format_degree(lon: float) -> dict[str, Any]:
    value = lon % 360
    sign_index = int(value // 30)
    within = value - sign_index * 30
    deg = int(within)
    minute_float = (within - deg) * 60
    minute = int(minute_float)
    second = round((minute_float - minute) * 60)
    if second == 60:
        second = 0
        minute += 1
    if minute == 60:
        minute = 0
        deg += 1
    sign_en, sign_cn = SIGNS[sign_index]
    return {
        "longitude": round(value, 6),
        "sign": sign_en,
        "sign_cn": sign_cn,
        "degree": deg,
        "minute": minute,
        "second": second,
        "display": f"{sign_cn} {deg:02d}°{minute:02d}'{second:02d}\"",
    }


def _house_number(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    return HOUSE_NAME_TO_NUMBER.get(str(value))


def _kerykeion_point_position(point: Any) -> dict[str, Any]:
    return _format_degree(float(point.abs_pos))


def _kerykeion_planet_record(point: Any, name: str, label: str, cusps: list[float]) -> dict[str, Any]:
    position = _kerykeion_point_position(point)
    return {
        "name": name,
        "label": label,
        "position": position,
        "house": _house_number(getattr(point, "house", None)) or _house_of(position["longitude"], cusps),
        "retrograde": bool(getattr(point, "retrograde", False)),
        "essential_dignity": _essential_dignity(name, position["sign"]),
    }


def _kerykeion_lot_record(point: Any, name: str) -> dict[str, Any]:
    position = _kerykeion_point_position(point)
    return {
        "name": name,
        "position": position,
        "house": _house_number(getattr(point, "house", None)),
        "calculation_note": "Calculated by Kerykeion from the configured tropical chart settings.",
    }


def _aspect_name(value: str) -> str:
    return KERYKEION_NAME_ALIASES.get(value, value.replace("_", " "))


def _interval_contains(x: float, a: float, b: float) -> bool:
    x %= 360
    a %= 360
    b %= 360
    return a <= x < b if a <= b else x >= a or x < b


def _house_of(lon: float, cusps: list[float]) -> int | None:
    for index in range(12):
        if _interval_contains(lon, cusps[index], cusps[(index + 1) % 12]):
            return index + 1
    return None


def _angular_distance(a: float, b: float) -> float:
    return abs((a - b + 180) % 360 - 180)


def _sign_boundary_distance(lon: float) -> float:
    within = lon % 30
    return min(within, 30 - within)


def _nearest_house_cusp(lon: float, cusps: list[float]) -> dict[str, Any]:
    distances = [
        {
            "house_cusp": index + 1,
            "cusp_longitude": round(cusp % 360, 6),
            "distance_degrees": round(_angular_distance(lon, cusp), 6),
        }
        for index, cusp in enumerate(cusps)
    ]
    return min(distances, key=lambda item: item["distance_degrees"])


def _western_boundary_sensitivity(
    planets: list[dict[str, Any]],
    cusps: list[float],
    angles: dict[str, dict[str, Any]],
    sign_threshold_degrees: float,
    house_threshold_degrees: float,
) -> dict[str, Any]:
    sign_items = []
    house_items = []
    angle_items = []

    for planet in planets:
        lon = planet["position"]["longitude"]
        sign_distance = _sign_boundary_distance(lon)
        if sign_distance <= sign_threshold_degrees:
            sign_items.append(
                {
                    "body": planet["name"],
                    "label": planet["label"],
                    "position": planet["position"],
                    "distance_to_sign_boundary_degrees": round(sign_distance, 6),
                }
            )

        cusp = _nearest_house_cusp(lon, cusps)
        if cusp["distance_degrees"] <= house_threshold_degrees:
            house_items.append(
                {
                    "body": planet["name"],
                    "label": planet["label"],
                    "position": planet["position"],
                    "current_house": planet.get("house"),
                    "nearest_cusp": cusp,
                }
            )

    for name, angle in angles.items():
        sign_distance = _sign_boundary_distance(angle["longitude"])
        if sign_distance <= sign_threshold_degrees:
            angle_items.append(
                {
                    "angle": name,
                    "position": angle,
                    "distance_to_sign_boundary_degrees": round(sign_distance, 6),
                }
            )

    return {
        "sign_boundary_threshold_degrees": sign_threshold_degrees,
        "house_cusp_threshold_degrees": house_threshold_degrees,
        "has_boundary_warnings": bool(sign_items or house_items or angle_items),
        "planets_near_sign_boundary": sign_items,
        "angles_near_sign_boundary": angle_items,
        "planets_near_house_cusp": house_items,
        "adjustment_prompt": "If any item is near a sign or house boundary, confirm birth time, coordinates, timezone, and house system before interpreting categorical sign or house labels.",
    }


def _opposite_sign(sign: str) -> str:
    return SIGNS[(SIGN_INDEX[sign] + 6) % 12][0]


def _essential_dignity(planet: str, sign: str) -> dict[str, Any]:
    if planet not in DOMICILE_SIGNS:
        return {
            "scheme": "traditional_seven_planet",
            "primary": "not_evaluated",
            "statuses": [],
            "label": DIGNITY_LABELS["not_evaluated"],
        }

    statuses = []
    if sign in DOMICILE_SIGNS[planet]:
        statuses.append("domicile")
    if sign in {_opposite_sign(item) for item in DOMICILE_SIGNS[planet]}:
        statuses.append("detriment")

    exaltation = EXALTATION_SIGNS.get(planet)
    if exaltation and sign == exaltation:
        statuses.append("exaltation")
    if exaltation and sign == _opposite_sign(exaltation):
        statuses.append("fall")

    priority = ["exaltation", "domicile", "fall", "detriment"]
    primary = next((status for status in priority if status in statuses), "neutral")
    return {
        "scheme": "traditional_seven_planet",
        "primary": primary,
        "statuses": statuses,
        "label": DIGNITY_LABELS[primary],
        "labels": [DIGNITY_LABELS[status] for status in statuses] or [DIGNITY_LABELS["neutral"]],
    }


def _house_ruler_concentrations(planets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_house: dict[int, dict[str, Any]] = {}
    for planet in planets:
        ruled_houses = planet.get("rules_houses") or []
        placement_house = planet.get("house")
        if not ruled_houses or placement_house is None:
            continue
        entry = by_house.setdefault(
            placement_house,
            {
                "house": placement_house,
                "ruling_planets": [],
                "ruled_houses": [],
                "count": 0,
                "interpretation_hint": "multiple house rulers concentrate in this house",
            },
        )
        entry["ruling_planets"].append(planet["name"])
        entry["ruled_houses"].extend(ruled_houses)

    concentrations = []
    for entry in by_house.values():
        entry["ruling_planets"] = sorted(set(entry["ruling_planets"]))
        entry["ruled_houses"] = sorted(set(entry["ruled_houses"]))
        entry["count"] = len(entry["ruled_houses"])
        if entry["count"] >= 3:
            concentrations.append(entry)
    return sorted(concentrations, key=lambda item: (-item["count"], item["house"]))


def _lot_position(name: str, asc_lon: float, sun_lon: float, moon_lon: float, sect: str, lagna_lon: float) -> dict[str, Any]:
    if name == "fortune":
        if sect == "day":
            lot_lon = asc_lon + moon_lon - sun_lon
            formula = "Ascendant + Moon - Sun"
        else:
            lot_lon = asc_lon + sun_lon - moon_lon
            formula = "Ascendant + Sun - Moon"
        label = "福点"
    elif name == "spirit":
        if sect == "day":
            lot_lon = asc_lon + sun_lon - moon_lon
            formula = "Ascendant + Sun - Moon"
        else:
            lot_lon = asc_lon + moon_lon - sun_lon
            formula = "Ascendant + Moon - Sun"
        label = "灵点"
    else:
        raise ValueError(f"unsupported lot: {name}")
    return {
        "name": name,
        "label": label,
        "position": _format_degree(lot_lon),
        "whole_sign_house": _whole_sign_house(lot_lon, lagna_lon),
        "formula": formula,
        "sect": sect,
    }


def _age_on_date(birth: datetime, target: datetime) -> int:
    birthday_passed = (target.month, target.day) >= (birth.month, birth.day)
    return target.year - birth.year - (0 if birthday_passed else 1)


def _annual_profections(birth_local: datetime, targets: list[datetime], houses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for target in targets:
        age = max(0, _age_on_date(birth_local, target.replace(tzinfo=None)))
        house_number = age % 12 + 1
        house = houses[house_number - 1]
        rows.append(
            {
                "target_date": target.date().isoformat(),
                "age_at_target": age,
                "profected_house": house_number,
                "profected_sign": house["sign"],
                "profected_sign_cn": house["sign_cn"],
                "time_lord": house["ruler"],
                "time_lord_label": PLANET_LABELS.get(house["ruler"]),
                "calculation_note": "Annual profection is counted from birthday to birthday; year-only targets use Jan 1 as the target date.",
            }
        )
    return rows


def _kerykeion_aspects(subject: Any, aspects_factory: Any) -> list[dict[str, Any]]:
    aspects = aspects_factory.single_chart_aspects(
        subject,
        active_points=[
            "Sun",
            "Moon",
            "Mercury",
            "Venus",
            "Mars",
            "Jupiter",
            "Saturn",
            "Uranus",
            "Neptune",
            "Pluto",
            "True_North_Lunar_Node",
        ],
    )
    records = []
    for aspect in aspects.aspects:
        data = aspect.model_dump()
        angle = int(data.get("aspect_degrees") or 0)
        if angle not in {0, 60, 90, 120, 180}:
            continue
        aspect_name = str(data.get("aspect") or "").lower()
        raw_diff = abs(float(data.get("diff") or 0)) % 360
        separation = min(raw_diff, 360 - raw_diff)
        records.append(
            {
                "from": _aspect_name(str(data.get("p1_name"))),
                "to": _aspect_name(str(data.get("p2_name"))),
                "aspect": aspect_name,
                "label": ASPECT_LABELS.get(aspect_name),
                "angle": angle,
                "separation": round(separation, 4),
                "orb": round(abs(float(data.get("orbit") or 0)), 4),
                "movement": data.get("aspect_movement"),
            }
        )
    return records


def _kerykeion_western_chart(
    subject: Any,
    aspects_factory: Any,
    house_system: str,
    sign_boundary_degrees: float,
    house_cusp_degrees: float,
) -> dict[str, Any]:
    cusp_list = [float(getattr(subject, attr).abs_pos) for attr in HOUSE_ATTRS]
    planets = [
        _kerykeion_planet_record(getattr(subject, attr), name, label, cusp_list)
        for name, label, attr in KERYKEION_PLANETS
    ]

    houses = []
    rules_by_planet: dict[str, list[int]] = {name: [] for name, _label, _attr in KERYKEION_PLANETS}
    for index, cusp in enumerate(cusp_list):
        cusp_position = _format_degree(cusp)
        ruler = TRADITIONAL_RULERS.get(cusp_position["sign"])
        house_number = index + 1
        houses.append(
            {
                "house": house_number,
                "cusp": cusp_position,
                "ruler": ruler,
                "ruler_label": PLANET_LABELS.get(ruler),
                "ruler_scheme": "traditional",
            }
        )
        if ruler in rules_by_planet:
            rules_by_planet[ruler].append(house_number)

    for planet in planets:
        planet["rules_houses"] = rules_by_planet.get(planet["name"], [])

    angles = {
        "ascendant": _kerykeion_point_position(subject.ascendant),
        "midheaven": _kerykeion_point_position(subject.medium_coeli),
    }
    return {
        "zodiac": "tropical",
        "house_system": house_system,
        "engine": "kerykeion",
        "angles": angles,
        "houses": houses,
        "planets": planets,
        "major_aspects": _kerykeion_aspects(subject, aspects_factory),
        "lots": {
            "part_of_fortune": _kerykeion_lot_record(subject.pars_fortunae, "part_of_fortune"),
            "part_of_spirit": _kerykeion_lot_record(subject.pars_spiritus, "part_of_spirit"),
        },
        "analysis": {
            "house_ruler_concentrations": _house_ruler_concentrations(planets),
            "boundary_sensitivity": _western_boundary_sensitivity(
                planets,
                cusp_list,
                angles,
                sign_boundary_degrees,
                house_cusp_degrees,
            ),
        },
    }


def _traditional_western_chart(
    western: dict[str, Any],
    birth_local: datetime,
    targets: list[datetime],
) -> dict[str, Any]:
    asc_lon = western["angles"]["ascendant"]["longitude"]
    asc_sign_index = int((asc_lon % 360) // 30)
    planets_by_name = {planet["name"]: planet for planet in western["planets"]}
    sun = planets_by_name["Sun"]
    moon = planets_by_name["Moon"]
    sun_whole_house = _whole_sign_house(sun["position"]["longitude"], asc_lon)
    sect = "day" if sun_whole_house in {7, 8, 9, 10, 11, 12} else "night"

    houses = []
    rules_by_planet = {name: [] for name in TRADITIONAL_PLANETS}
    for index in range(12):
        sign_index = (asc_sign_index + index) % 12
        sign_en, sign_cn = SIGNS[sign_index]
        ruler = TRADITIONAL_RULERS[sign_en]
        house_number = index + 1
        houses.append(
            {
                "house": house_number,
                "sign": sign_en,
                "sign_cn": sign_cn,
                "ruler": ruler,
                "ruler_label": PLANET_LABELS.get(ruler),
                "angularity": HOUSE_ANGULARITY[house_number],
                "house_model": "whole_sign",
            }
        )
        rules_by_planet[ruler].append(house_number)

    traditional_planets = []
    for name in ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
        planet = planets_by_name[name]
        whole_house = _whole_sign_house(planet["position"]["longitude"], asc_lon)
        sect_affiliation = PLANET_SECT[name]
        traditional_planets.append(
            {
                "name": name,
                "label": planet["label"],
                "position": planet["position"],
                "whole_sign_house": whole_house,
                "house_angularity": HOUSE_ANGULARITY[whole_house],
                "retrograde": planet["retrograde"],
                "essential_dignity": planet["essential_dignity"],
                "sect_affiliation": sect_affiliation,
                "in_sect": None if sect_affiliation == "variable" else sect_affiliation == sect,
                "rules_houses": rules_by_planet.get(name, []),
            }
        )

    lots = {
        "part_of_fortune": _lot_position(
            "fortune",
            asc_lon,
            sun["position"]["longitude"],
            moon["position"]["longitude"],
            sect,
            asc_lon,
        ),
        "part_of_spirit": _lot_position(
            "spirit",
            asc_lon,
            sun["position"]["longitude"],
            moon["position"]["longitude"],
            sect,
            asc_lon,
        ),
    }

    return {
        "tradition": "traditional_western_hellenistic_style",
        "zodiac": "tropical",
        "house_model": "whole_sign_from_ascendant",
        "ruler_scheme": "traditional_seven_planet",
        "sect": sect,
        "angles": western["angles"],
        "houses": houses,
        "planets": traditional_planets,
        "lots": lots,
        "annual_profections": _annual_profections(birth_local, targets, houses),
        "calculation_notes": [
            "古占 layer uses tropical zodiac, whole-sign houses from Ascendant, traditional seven-planet rulers, sect, Fortune/Spirit lots, and annual profections.",
            "This helper does not calculate bounds/terms, decans, fixed stars, primary directions, or zodiacal releasing.",
            "Treat 古占 as a traditional symbolic timing and condition layer, not deterministic event prediction.",
        ],
    }


def _nakshatra(lon: float) -> dict[str, Any]:
    segment = 360 / 27
    pada_segment = segment / 4
    index = int((lon % 360) // segment)
    start = index * segment
    offset = (lon % 360) - start
    pada = int(offset // pada_segment) + 1
    name, lord = NAKSHATRAS[index]
    return {
        "index": index + 1,
        "name": name,
        "lord": lord,
        "pada": pada,
        "offset_degrees": round(offset, 6),
    }


def _whole_sign_house(lon: float, lagna_lon: float) -> int:
    lagna_sign = int((lagna_lon % 360) // 30)
    body_sign = int((lon % 360) // 30)
    return ((body_sign - lagna_sign) % 12) + 1


def _target_dates(payload: dict[str, Any]) -> list[datetime]:
    dates = []
    for value in payload.get("target_dates") or []:
        dates.append(datetime.strptime(str(value), "%Y-%m-%d").replace(tzinfo=timezone.utc))
    years = payload.get("target_years")
    if isinstance(years, int):
        years = [years]
    for year in years or []:
        dates.append(datetime(int(year), 1, 1, tzinfo=timezone.utc))
    return dates


def _active_dasha(periods: list[dict[str, Any]], target: datetime) -> dict[str, Any] | None:
    target_date = target.date().isoformat()
    for period in periods:
        if period["start"] <= target_date < period["end"]:
            return period
    return None


def _pyjhora_jd_from_tuple(utils: Any, drik: Any, value: tuple[int, int, int, float]) -> float:
    year, month, day, fractional_hour = value
    return utils.julian_day_number(drik.Date(year, month, day), (fractional_hour, 0, 0))


def _pyjhora_date_tuple_to_iso(value: tuple[int, int, int, float]) -> str:
    year, month, day, _fractional_hour = value
    return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"


def _pyjhora_lord_name(lord: Any) -> str:
    return VEDIC_PLANET_LABELS.get(lord, (str(lord), str(lord)))[0]


def _pyjhora_dasha(utils: Any, const: Any, drik: Any, vimsottari: Any, jd: float, place: Any, moon_nakshatra: dict[str, Any]) -> dict[str, Any]:
    balance, rows = vimsottari.get_vimsottari_dhasa_bhukthi(
        jd,
        place,
        dhasa_level_index=const.MAHA_DHASA_DEPTH.MAHA_DHASA_ONLY,
    )
    periods = []
    for index, row in enumerate(rows):
        lords, start_tuple, duration_years = row
        start_tuple = tuple(start_tuple)
        if index + 1 < len(rows):
            end_tuple = tuple(rows[index + 1][1])
        else:
            start_jd = _pyjhora_jd_from_tuple(utils, drik, start_tuple)
            end_tuple = tuple(utils.jd_to_gregorian(start_jd + float(duration_years) * const.sidereal_year))
        lord_ids = list(lords if isinstance(lords, tuple) else (lords,))
        periods.append(
            {
                "lord": _pyjhora_lord_name(lord_ids[-1]),
                "lord_ids": lord_ids,
                "start": _pyjhora_date_tuple_to_iso(start_tuple),
                "end": _pyjhora_date_tuple_to_iso(end_tuple),
                "years": round(float(duration_years), 4),
            }
        )
    return {
        "system": "vimshottari",
        "source": "PyJHora",
        "balance_at_birth": {
            "years": balance[0],
            "months": balance[1],
            "days": balance[2],
        },
        "moon_nakshatra": moon_nakshatra,
        "mahadasha_sequence": periods,
    }


def _pyjhora_vedic_chart(
    local_naive: datetime,
    timezone_offset_hours: float,
    lat: float,
    lon: float,
    payload: dict[str, Any],
) -> dict[str, Any]:
    const, utils, charts, vimsottari, drik, _version = _load_pyjhora()
    ayanamsa_mode = str(payload.get("ayanamsa") or payload.get("vedic_ayanamsa") or "LAHIRI").upper()
    place_name = str(payload.get("birth_place") or payload.get("place") or "birthplace")
    place = drik.Place(place_name, lat, lon, timezone_offset_hours)

    with redirect_stdout(io.StringIO()):
        utils.set_language("en")
        drik.set_ayanamsa_mode(ayanamsa_mode)
        drik.set_planet_list(set_rahu_ketu_as_true_nodes=True, include_western_planets=False)
        jd = utils.julian_day_number(
            drik.Date(local_naive.year, local_naive.month, local_naive.day),
            (local_naive.hour, local_naive.minute, local_naive.second),
        )
        planet_positions = charts.rasi_chart(jd, place)
        retrograde_planets = set(drik.planets_in_retrograde(jd, place))
        ayanamsa_degrees = drik.get_ayanamsa_value(jd)

    lagna_record = next((item for item in planet_positions if item[0] == "L"), None)
    if lagna_record is None:
        raise RuntimeError("PyJHora did not return a lagna record")
    lagna_lon = lagna_record[1][0] * 30 + lagna_record[1][1]
    moon_lon = None
    planets = []
    for planet_id, (sign_index, sign_degree) in planet_positions:
        absolute_lon = sign_index * 30 + sign_degree
        if planet_id == "L":
            continue
        name, label = VEDIC_PLANET_LABELS.get(planet_id, (str(planet_id), str(planet_id)))
        if name == "Moon":
            moon_lon = absolute_lon
        planets.append(
            {
                "name": name,
                "label": label,
                "position": _format_degree(absolute_lon),
                "nakshatra": _nakshatra(absolute_lon),
                "whole_sign_house": _whole_sign_house(absolute_lon, lagna_lon),
                "retrograde": planet_id in retrograde_planets,
            }
        )

    if moon_lon is None:
        raise RuntimeError("Moon longitude unavailable; cannot calculate Vimshottari dasha")

    moon_nakshatra = _nakshatra(moon_lon)
    with redirect_stdout(io.StringIO()):
        dasha = _pyjhora_dasha(utils, const, drik, vimsottari, jd, place, moon_nakshatra)

    return {
        "zodiac": "sidereal",
        "engine": "PyJHora",
        "ayanamsa": ayanamsa_mode.title() if ayanamsa_mode == "LAHIRI" else ayanamsa_mode,
        "ayanamsa_degrees": round(ayanamsa_degrees, 6),
        "lagna": _format_degree(lagna_lon),
        "house_model": "whole_sign_from_lagna",
        "planets": planets,
        "dasha": dasha,
    }


def build_profile(payload: dict[str, Any]) -> dict[str, Any]:
    local_naive = _parse_date_time(payload)
    tz = _parse_timezone(payload.get("timezone"))
    local_dt = local_naive.replace(tzinfo=tz)
    dt_utc = local_dt.astimezone(timezone.utc)
    lat, lon = _coordinates(payload)
    systems = {str(item).lower() for item in payload.get("systems", ["western", "vedic"])}
    house_system = str(payload.get("house_system", "P"))
    sign_boundary_degrees = float(payload.get("sign_boundary_degrees", 1.0))
    house_cusp_degrees = float(payload.get("house_cusp_degrees", 2.0))
    wants_western = bool({"western", "tropical"} & systems)
    wants_traditional = bool({"traditional", "hellenistic", "ancient", "古占"} & systems)
    wants_vedic = bool({"vedic", "jyotish", "indian", "印占"} & systems)

    result: dict[str, Any] = {
        "ok": True,
        "mode": "astrology-calculator",
        "engine": {
            "name": "split_astrology",
            "western": None,
            "vedic": None,
        },
        "input": {
            "birth_date": payload.get("birth_date"),
            "birth_time": payload.get("birth_time"),
            "timezone": payload.get("timezone"),
            "latitude": lat,
            "longitude": lon,
            "utc": dt_utc.isoformat(),
            "sign_boundary_degrees": sign_boundary_degrees,
            "house_cusp_degrees": house_cusp_degrees,
        },
        "unavailable_systems": [],
        "calculation_notes": [
            "Western/西占 chart uses Kerykeion with tropical zodiac and the requested house system.",
            "Western essential dignity and house rulership use the traditional seven-planet ruler scheme; outer planets and nodes are not assigned rulership by this helper.",
            "Western lots are returned by Kerykeion; verify school-specific lot formulas when precision matters.",
            "Sign and house labels are categorical summaries of continuous longitudes; boundary-sensitive placements should be confirmed before interpretation.",
            "Traditional/古占 output uses whole-sign houses, sect, traditional seven-planet rulership, lots, and annual profections when requested.",
            "Vedic/印占 chart uses PyJHora with the configured sidereal ayanamsa, true node, whole-sign houses from lagna, and PyJHora Vimshottari mahadasha.",
            "Kerykeion, PyJHora, and Swiss Ephemeris/pyswisseph have copyleft/commercial licensing considerations; confirm the license path before product or hosted use.",
            "No geocoding is performed; latitude and longitude must be supplied by the caller.",
        ],
    }

    targets = _target_dates(payload)
    western_for_traditional = None
    if wants_western or wants_traditional:
        try:
            subject_factory, aspects_factory, kerykeion_version = _load_kerykeion()
            kerykeion_dt, kerykeion_tz = _kerykeion_birth_args(local_dt, payload.get("timezone"))
            subject = subject_factory.from_birth_data(
                str(payload.get("name") or "Native"),
                kerykeion_dt.year,
                kerykeion_dt.month,
                kerykeion_dt.day,
                kerykeion_dt.hour,
                kerykeion_dt.minute,
                lng=lon,
                lat=lat,
                tz_str=kerykeion_tz,
                online=False,
                zodiac_type="Tropical",
                houses_system_identifier=house_system,
                active_points=KERYKEION_ACTIVE_POINTS,
                seconds=kerykeion_dt.second,
                suppress_geonames_warning=True,
            )
            result["engine"]["western"] = {
                "name": "kerykeion",
                "version": kerykeion_version,
                "upstream": "https://github.com/g-battaglia/kerykeion",
                "license": "AGPL-3.0",
                "ephemeris_dependency": "pyswisseph / Swiss Ephemeris",
            }
            result["input"]["kerykeion_timezone"] = kerykeion_tz
            western_for_traditional = _kerykeion_western_chart(
                subject,
                aspects_factory,
                house_system,
                sign_boundary_degrees,
                house_cusp_degrees,
            )
            if wants_western:
                result["western_tropical"] = western_for_traditional
            if wants_traditional:
                result["traditional_western"] = _traditional_western_chart(western_for_traditional, local_naive, targets)
        except Exception as exc:
            affected = []
            if wants_western:
                affected.append("western")
            if wants_traditional:
                affected.append("traditional")
            result["unavailable_systems"].append({"systems": affected, "engine": "kerykeion", "error": str(exc)})

    if wants_vedic:
        try:
            _const, _utils, _charts, _vimsottari, _drik, pyjhora_version = _load_pyjhora()
            result["engine"]["vedic"] = {
                "name": "PyJHora",
                "version": pyjhora_version,
                "upstream": "https://github.com/naturalstupid/PyJHora",
                "license": "AGPL-3.0",
                "ephemeris_dependency": "pyswisseph / Swiss Ephemeris",
            }
            vedic = _pyjhora_vedic_chart(local_naive, _timezone_offset_hours(local_dt), lat, lon, payload)
            target_blocks = []
            for target in targets:
                target_blocks.append({"target_date": target.date().isoformat(), "active_mahadasha": _active_dasha(vedic["dasha"]["mahadasha_sequence"], target)})
            if target_blocks:
                vedic["targets"] = target_blocks
            result["vedic_sidereal"] = vedic
        except Exception as exc:
            result["unavailable_systems"].append({"systems": ["vedic"], "engine": "PyJHora", "error": str(exc)})

    produced = any(key in result for key in ("western_tropical", "traditional_western", "vedic_sidereal"))
    if not produced:
        errors = "; ".join(
            f"{','.join(item['systems'])}: {item['error']}" for item in result["unavailable_systems"]
        )
        raise RuntimeError(f"No requested astrology systems are available. {errors}".strip())
    return result


def _check_deps() -> dict[str, Any]:
    """Quick dependency probe — import-check only, no calculation."""
    result: dict[str, Any] = {
        "ok": True,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "python_310_plus": sys.version_info >= (3, 10),
        "kerykeion": False,
        "kerykeion_version": None,
        "pyjhora": False,
        "pyjhora_version": None,
        "pyswisseph": False,
    }
    try:
        import kerykeion  # noqa: F401
        result["kerykeion"] = True
        try:
            result["kerykeion_version"] = metadata.version("kerykeion")
        except metadata.PackageNotFoundError:
            result["kerykeion_version"] = "unknown"
    except ImportError:
        result["ok"] = False

    try:
        import swisseph  # noqa: F401
        result["pyswisseph"] = True
    except ImportError:
        result["ok"] = False

    if sys.version_info >= (3, 10):
        try:
            from jhora.horoscope.chart import charts  # noqa: F401
            result["pyjhora"] = True
            try:
                result["pyjhora_version"] = metadata.version("PyJHora")
            except metadata.PackageNotFoundError:
                result["pyjhora_version"] = "unknown"
        except (ImportError, TypeError):
            result["ok"] = False
    else:
        result["ok"] = False

    if not result["ok"]:
        missing = []
        if not result["kerykeion"]:
            missing.append("kerykeion")
        if not result["pyswisseph"]:
            missing.append("pyswisseph")
        if not result["pyjhora"]:
            missing.append("PyJHora")
        if not result["python_310_plus"]:
            missing.append("Python>=3.10")
        result["error"] = f"Missing: {', '.join(missing)}. Install scripts/requirements-astro.txt or provide verified chart data manually."
    return result


def main() -> int:
    args = _parse_args()
    if args.check_deps:
        deps = _check_deps()
        print(json.dumps(deps, ensure_ascii=False, indent=2))
        return 0 if deps["ok"] else 1
    try:
        result = build_profile(_read_payload(args))
        if args.self_test:
            if "western_tropical" not in result or "vedic_sidereal" not in result or "traditional_western" not in result:
                raise RuntimeError("self-test missing chart sections")
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
