# Calculation Contract

Use this contract to keep deterministic calculation separate from interpretation.

## Reliability Modes

| Mode | Allowed Interpretation |
| --- | --- |
| `verified-chart` | Full reading from user-provided chart facts. |
| `bazi-calculator` | Full BaZi-based reading after script output is confirmed. |
| `ziwei-calculator` | Full Zi Wei-based reading after `ziwei_profile.mjs` output is confirmed. |
| `astrology-calculator` | Full birth chart-based reading after ephemeris output is confirmed. |
| `numerology-calculator` | Supplemental date-based numerology after `numerology_profile.py` output is confirmed. |
| `partial` | Reflective themes only; no Hour Pillar, ascendant, houses, or precise timing claims. |

## Birth Input JSON

```json
{
  "name": "optional display name",
  "calendar": "solar",
  "birth_date": "2005-12-23",
  "birth_time": "08:37:00",
  "is_lunar_leap_month": false,
  "gender": "male",
  "target_years": [2026],
  "verified_tai_yuan": "optional verified pillar from the user's trusted chart",
  "tai_yuan_policy": "engine-calculated, user-verified, or adjusted",
  "premature_birth_note": "optional note if the user wants Tai Yuan adjusted for gestational context",
  "timezone": "+08:00",
  "birth_place": "optional city",
  "latitude": 39.9,
  "longitude": 116.4,
  "systems": ["western", "traditional", "vedic"],
  "interpretation_mode": "reflective or akashic-full"
}
```

`calendar` may be `solar`, `gregorian`, `lunar`, or `chinese_lunar`.

## Normalized Output

```json
{
  "ok": true,
  "mode": "bazi-calculator",
  "engine": {
    "name": "lunar_python",
    "version": "..."
  },
  "input": {},
  "bazi": {
    "pillars": {
      "year": "Yi You",
      "month": "Wu Zi",
      "day": "Xin Si",
      "hour": "Ren Chen"
    },
    "structure": {
      "branches": [],
      "counts": {},
      "branch_interactions": [
        {
          "type": "San Hui",
          "name": "Hai-Zi-ChouSan HuiWater",
          "branches": ["Hai", "Zi", "Chou"],
          "element": "Water",
          "basis": "four_pillars_only",
          "involves_auxiliary": false,
          "auxiliary_sources": [],
          "positions": []
        }
      ]
    },
    "verified_auxiliary_pillars": [
      {
        "position": "verified_tai_yuan",
        "label": "verifiedTai Yuan",
        "pillar": "<verified_ganzhi_pillar>",
        "source": "user_verified"
      }
    ],
    "day_master": "Xin",
    "five_elements": {},
    "ten_gods": {},
    "hidden_stems": {},
    "nayin": {},
    "tai_yuan": "",
    "tai_xi": "",
    "ming_gong": "",
    "shen_gong": "",
    "boundary_sensitivity": {}
  },
  "yun": {
    "available": true,
    "direction": "forward",
    "start": {},
    "decades": [],
    "target_years": [2026],
    "annual_fortunes": []
  },
  "ziwei": {
    "solar_date": "",
    "lunar_date": "",
    "chinese_date": "",
    "soul": "",
    "body": "",
    "five_elements_class": "",
    "palaces": [],
    "horoscopes": []
  },
  "western_tropical": {
    "zodiac": "tropical",
    "house_system": "P",
    "angles": {},
    "houses": [
      {
        "house": 1,
        "cusp": {},
        "ruler": "Mars",
        "ruler_scheme": "traditional"
      }
    ],
    "planets": [
      {
        "name": "Sun",
        "position": {},
        "house": 5,
        "essential_dignity": {},
        "rules_houses": []
      }
    ],
    "major_aspects": [],
    "lots": {
      "part_of_fortune": {}
    },
    "analysis": {
      "house_ruler_concentrations": [],
      "boundary_sensitivity": {}
    }
  },
  "vedic_sidereal": {
    "zodiac": "sidereal",
    "ayanamsa": "Lahiri",
    "lagna": {},
    "house_model": "whole_sign_from_lagna",
    "planets": [],
    "dasha": {}
  },
  "traditional_western": {
    "tradition": "traditional_western_hellenistic_style",
    "zodiac": "tropical",
    "house_model": "whole_sign_from_ascendant",
    "ruler_scheme": "traditional_seven_planet",
    "sect": "day or night",
    "houses": [],
    "planets": [],
    "lots": {},
    "annual_profections": []
  },
  "numerology": {
    "life_path": {},
    "birthday_number": {},
    "attitude_number": {}
  },
  "calculation_notes": []
}
```

## Verification Policy

- Always show the four pillars and any chart settings before generating the reading.
- If a user says the chart differs from their trusted app, pause interpretation and ask for the verified chart.
- Treat exact timestamp-to-category conversion as information loss. If a calculated field is close to a category boundary, ask whether the user wants to keep the current categorization, test adjacent categories, apply true-solar-time/location correction, or use a verified chart.
- For BaZi, record whether late Zi hour is treated as same-day or next-day when the engine exposes that choice.
- For BaZi hour pillars, flag birth times close to Chinese-hour boundaries. Use this especially around 23:00/01:00/03:00/.../21:00, where a small time correction can change the Hour Pillar.
- For BaZi structure, show deterministic combinations first, then interpret only after confirming they make sense under the user's preferred school.
- For Tai Yuan, Ming Gong, Shen Gong or other auxiliary pillars, distinguish engine-calculated values from user-verified values. If they conflict, show both and ask which school/source to use.
- For Tai Yuan, explicitly ask whether the user wants an adjustment when premature birth, induced delivery, uncertain gestational timing, or school-specific Tai Yuan policy matters. Do not invent adjusted Tai Yuan; request a verified adjusted value or state that the engine value is unadjusted.
- If a branch interaction includes auxiliary pillars, preserve `involves_auxiliary` and `auxiliary_sources` in the summary so the reading can weight it differently from four-pillar-only interactions.
- For Da Yun/Liu Nian, sex/gender is required only because the traditional forward/reverse direction rule uses it; do not overstate gender identity beyond this calculation convention.
- For Zi Wei, record gender convention, time-index convention, language, leap-month handling, and whether target horoscopes use a specific date or a year anchor.
- For birth chart, record zodiac, house system, birth timezone, coordinates, ephemeris source, essential dignity scheme, house-ruler scheme, and Part of Fortune formula. Flag planets or angles near sign cusps, and planets near house cusps, because categorical sign/house labels may change under small time/location/house-system corrections.
- For Gu Zhan, record tradition, zodiac, whole-sign house model, traditional ruler scheme, sect, lots, annual profection target dates, and omitted techniques. Treat profections and time lords as symbolic timing context, not event prediction.
- For Vedic, record ayanamsa, node choice, lagna/house model, dasha system, and ephemeris source. Treat dasha as symbolic timing context, not deterministic prediction.
- For numerology, show the arithmetic, master-number convention, full-date versus component-first reduction convention, and whether the reading is date-only or name-based.
- For cross-system element language, state that BaZi five phases and Western/Vedic elemental vocabularies are separate technical systems. Compare them symbolically; do not convert one into the other.
- Do not combine chart data from mismatched settings without warning.
