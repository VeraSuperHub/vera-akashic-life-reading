#!/usr/bin/env python3
"""Emit normalized modern, traditional, and Vedic-style astrology JSON.

This script performs calculation only. It does not generate spiritual
interpretation text.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


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

VEDIC_PLANETS = [
    ("Sun", "太阳", "SUN"),
    ("Moon", "月亮", "MOON"),
    ("Mercury", "水星", "MERCURY"),
    ("Venus", "金星", "VENUS"),
    ("Mars", "火星", "MARS"),
    ("Jupiter", "木星", "JUPITER"),
    ("Saturn", "土星", "SATURN"),
    ("Rahu", "罗睺", "TRUE_NODE"),
]

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

VIMSHOTTARI_SEQUENCE = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIMSHOTTARI_YEARS = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17,
}

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


def _load_swisseph():
    try:
        import swisseph as swe
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Missing dependency: swisseph/pyswisseph. Install scripts/requirements-astro.txt "
            "or provide verified astrology/古占/印占 data manually."
        ) from exc
    return swe


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Calculate normalized astrology JSON.")
    parser.add_argument("--input", help="Path to input JSON. Reads stdin when omitted.")
    parser.add_argument("--self-test", action="store_true", help="Run a synthetic chart calculation.")
    return parser.parse_args()


def _read_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.self_test:
        return {
            "calendar": "solar",
            "birth_date": "2000-08-16",
            "birth_time": "03:30",
            "timezone": "+08:00",
            "latitude": 39.9042,
            "longitude": 116.4074,
            "systems": ["western", "vedic", "traditional"],
            "target_years": [2026],
        }
    text = Path(args.input).read_text(encoding="utf-8") if args.input else sys.stdin.read()
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


def _julian_day_utc(swe: Any, dt_utc: datetime) -> float:
    hour = dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600 + dt_utc.microsecond / 3_600_000_000
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour, swe.GREG_CAL)


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


def _part_of_fortune(asc_lon: float, sun_lon: float, moon_lon: float, sun_house: int | None, cusps: list[float]) -> dict[str, Any]:
    is_day_chart = sun_house in {7, 8, 9, 10, 11, 12}
    if is_day_chart:
        fortune_lon = asc_lon + moon_lon - sun_lon
        formula = "Ascendant + Moon - Sun"
        sect = "day"
    else:
        fortune_lon = asc_lon + sun_lon - moon_lon
        formula = "Ascendant + Sun - Moon"
        sect = "night"
    return {
        "position": _format_degree(fortune_lon),
        "house": _house_of(fortune_lon, cusps),
        "sect": sect,
        "formula": formula,
        "calculation_note": "Sect is approximated from the Sun's calculated house: houses 7-12 are treated as above horizon.",
    }


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


def _planet_constant(swe: Any, name: str) -> int:
    return getattr(swe, name)


def _western_chart(
    swe: Any,
    jd: float,
    lat: float,
    lon: float,
    house_system: str,
    sign_boundary_degrees: float = 1.0,
    house_cusp_degrees: float = 2.0,
) -> dict[str, Any]:
    cusps, ascmc = swe.houses(jd, lat, lon, house_system.encode("ascii"))
    cusp_list = list(cusps)
    planets = []
    positions: dict[str, float] = {}
    for name, label, constant_name in PLANETS:
        xx, _flag = swe.calc_ut(jd, _planet_constant(swe, constant_name))
        ecl_lon, _lat, _dist, speed = xx[:4]
        formatted_position = _format_degree(ecl_lon)
        positions[name] = ecl_lon
        planets.append(
            {
                "name": name,
                "label": label,
                "position": formatted_position,
                "house": _house_of(ecl_lon, cusp_list),
                "retrograde": speed < 0,
                "essential_dignity": _essential_dignity(name, formatted_position["sign"]),
            }
        )

    houses = []
    rules_by_planet: dict[str, list[int]] = {name: [] for name, _label, _constant_name in PLANETS}
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

    aspects = []
    aspect_defs = [("conjunction", "合相", 0, 8), ("sextile", "六合", 60, 4), ("square", "刑相", 90, 6), ("trine", "拱相", 120, 6), ("opposition", "冲相", 180, 8)]
    for a, b in itertools.combinations(positions, 2):
        sep = abs((positions[a] - positions[b] + 180) % 360 - 180)
        hits = [(abs(sep - angle), name, label, angle) for name, label, angle, orb in aspect_defs if abs(sep - angle) <= orb]
        if hits:
            diff, name, label, angle = sorted(hits)[0]
            aspects.append({"from": a, "to": b, "aspect": name, "label": label, "angle": angle, "separation": round(sep, 4), "orb": round(diff, 4)})

    sun_house = _house_of(positions["Sun"], cusp_list)
    angles = {
        "ascendant": _format_degree(ascmc[0]),
        "midheaven": _format_degree(ascmc[1]),
    }
    return {
        "zodiac": "tropical",
        "house_system": house_system,
        "angles": angles,
        "houses": houses,
        "planets": planets,
        "major_aspects": aspects,
        "lots": {
            "part_of_fortune": _part_of_fortune(ascmc[0], positions["Sun"], positions["Moon"], sun_house, cusp_list),
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


def _vimshottari(dt_utc: datetime, moon_lon: float) -> dict[str, Any]:
    nak = _nakshatra(moon_lon)
    lord = nak["lord"]
    segment = 360 / 27
    fraction_used = nak["offset_degrees"] / segment
    remaining_years = (1 - fraction_used) * VIMSHOTTARI_YEARS[lord]
    lord_index = VIMSHOTTARI_SEQUENCE.index(lord)
    start = dt_utc
    end = start + timedelta(days=remaining_years * 365.2425)
    periods = [{"lord": lord, "start": start.date().isoformat(), "end": end.date().isoformat(), "years": round(remaining_years, 4), "balance_at_birth": True}]
    current = end
    for step in range(1, 10):
        next_lord = VIMSHOTTARI_SEQUENCE[(lord_index + step) % len(VIMSHOTTARI_SEQUENCE)]
        years = VIMSHOTTARI_YEARS[next_lord]
        next_end = current + timedelta(days=years * 365.2425)
        periods.append({"lord": next_lord, "start": current.date().isoformat(), "end": next_end.date().isoformat(), "years": years})
        current = next_end
    return {"system": "vimshottari", "moon_nakshatra": nak, "mahadasha_sequence": periods}


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


def _vedic_chart(swe: Any, jd: float, dt_utc: datetime, asc_tropical: float) -> dict[str, Any]:
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd)
    sidereal_asc = (asc_tropical - ayanamsa) % 360
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    planets = []
    moon_lon = None
    for name, label, constant_name in VEDIC_PLANETS:
        xx, _flag = swe.calc_ut(jd, _planet_constant(swe, constant_name), flags)
        ecl_lon, _lat, _dist, speed = xx[:4]
        if name == "Moon":
            moon_lon = ecl_lon
        planets.append(
            {
                "name": name,
                "label": label,
                "position": _format_degree(ecl_lon),
                "nakshatra": _nakshatra(ecl_lon),
                "whole_sign_house": _whole_sign_house(ecl_lon, sidereal_asc),
                "retrograde": speed < 0,
            }
        )
        if name == "Rahu":
            ketu_lon = (ecl_lon + 180) % 360
            planets.append(
                {
                    "name": "Ketu",
                    "label": "计都",
                    "position": _format_degree(ketu_lon),
                    "nakshatra": _nakshatra(ketu_lon),
                    "whole_sign_house": _whole_sign_house(ketu_lon, sidereal_asc),
                    "retrograde": speed < 0,
                }
            )
    if moon_lon is None:
        raise RuntimeError("Moon longitude unavailable; cannot calculate Vimshottari dasha")
    dasha = _vimshottari(dt_utc, moon_lon)
    return {
        "zodiac": "sidereal",
        "ayanamsa": "Lahiri",
        "ayanamsa_degrees": round(ayanamsa, 6),
        "lagna": _format_degree(sidereal_asc),
        "house_model": "whole_sign_from_lagna",
        "planets": planets,
        "dasha": dasha,
    }


def build_profile(payload: dict[str, Any]) -> dict[str, Any]:
    swe = _load_swisseph()
    local_naive = _parse_date_time(payload)
    tz = _parse_timezone(payload.get("timezone"))
    local_dt = local_naive.replace(tzinfo=tz)
    dt_utc = local_dt.astimezone(timezone.utc)
    lat, lon = _coordinates(payload)
    jd = _julian_day_utc(swe, dt_utc)
    systems = {str(item).lower() for item in payload.get("systems", ["western", "vedic"])}
    house_system = str(payload.get("house_system", "P"))
    sign_boundary_degrees = float(payload.get("sign_boundary_degrees", 1.0))
    house_cusp_degrees = float(payload.get("house_cusp_degrees", 2.0))

    result: dict[str, Any] = {
        "ok": True,
        "mode": "astrology-calculator",
        "engine": {
            "name": "pyswisseph",
            "version": getattr(swe, "version", "unknown"),
            "upstream": "https://www.astro.com/swisseph/",
            "license_note": "Swiss Ephemeris is AGPL/commercial; confirm license before product use.",
        },
        "input": {
            "birth_date": payload.get("birth_date"),
            "birth_time": payload.get("birth_time"),
            "timezone": payload.get("timezone"),
            "latitude": lat,
            "longitude": lon,
            "utc": dt_utc.isoformat(),
            "julian_day_ut": jd,
            "sign_boundary_degrees": sign_boundary_degrees,
            "house_cusp_degrees": house_cusp_degrees,
        },
        "calculation_notes": [
            "Western chart uses tropical zodiac and the requested house system.",
            "Western essential dignity and house rulership use the traditional seven-planet ruler scheme; outer planets and nodes are not assigned rulership by this helper.",
            "Part of Fortune is calculated from sect using Ascendant, Sun, and Moon; verify school-specific lot formulas when precision matters.",
            "Sign and house labels are categorical summaries of continuous longitudes; boundary-sensitive placements should be confirmed before interpretation.",
            "Traditional/古占 output uses whole-sign houses, sect, traditional seven-planet rulership, lots, and annual profections when requested.",
            "Vedic-style chart uses Lahiri sidereal zodiac, true node, whole-sign houses from lagna, and approximate Vimshottari mahadasha from Moon nakshatra.",
            "No geocoding is performed; latitude and longitude must be supplied by the caller.",
        ],
    }

    targets = _target_dates(payload)
    western_for_asc = _western_chart(swe, jd, lat, lon, house_system, sign_boundary_degrees, house_cusp_degrees)
    if "western" in systems or "tropical" in systems:
        result["western_tropical"] = western_for_asc
    if "traditional" in systems or "hellenistic" in systems or "ancient" in systems or "古占" in systems:
        result["traditional_western"] = _traditional_western_chart(western_for_asc, local_naive, targets)
    if "vedic" in systems or "jyotish" in systems or "indian" in systems or "印占" in systems:
        vedic = _vedic_chart(swe, jd, dt_utc, western_for_asc["angles"]["ascendant"]["longitude"])
        target_blocks = []
        for target in targets:
            target_blocks.append({"target_date": target.date().isoformat(), "active_mahadasha": _active_dasha(vedic["dasha"]["mahadasha_sequence"], target)})
        if target_blocks:
            vedic["targets"] = target_blocks
        result["vedic_sidereal"] = vedic
    return result


def main() -> int:
    args = _parse_args()
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
