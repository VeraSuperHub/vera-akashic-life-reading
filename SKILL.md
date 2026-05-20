---
name: vera-akashic-life-reading
description: >-
  Verified birth-chart interpretation workflow for Akashic-record-style and life-lesson readings. Use when the user wants a symbolic soul map, Akashic record, past life reading, life purpose reading, soul blueprint, karmic reading, this-life themes, soul lessons, destiny pattern, BaZi, Zi Wei Dou Shu, Western astrology, Traditional astrology/Gu Zhan, Vedic astrology/Vedic, numerology, or a reflective spiritual narrative from provided birth data or verified charts. Separates deterministic chart calculation from LLM interpretation and refuses to invent unverified charts.
---

# Vera Akashic Life Reading

Create reflective Akashic-record-style life readings from verified birth-chart data. Keep a hard boundary: scripts or trusted external calculators compute charts; the language model interprets confirmed chart facts.

## Operating Rules

- Do not freehand-calculate BaZi, Zi Wei Dou Shu, birth chart, Gu Zhan, or Vedic from memory.
- If the user provides verified BaZi, Zi Wei, birth chart, Gu Zhan, or Vedic data, parse and normalize it before interpreting.
- If the user provides birth data, compute only through a deterministic helper or trusted backend, then ask the user to confirm the chart.
- If chart data is incomplete, label the reading as partial and avoid claims that depend on missing fields.
- Treat Akashic records as symbolic, reflective, and spiritual/creative interpretation, not factual access to hidden records.
- Treat same-named elements across systems as analogical, not equivalent: Western fire/earth/water/air and BaZi wood/fire/earth/metal/water use different technical models.
- Treat exact timestamp-to-category conversions as lossy. Before interpretation, flag boundary-sensitive cases such as a birth time near a Chinese-hour boundary, a planet or angle near a sign cusp, or a planet near a house cusp.
- Avoid fatalistic, medical, financial, legal, or relationship-certainty claims.

## Inputs

Ask only for missing fields needed for the requested mode:

- Name or preferred name.
- Birth date and calendar type: Gregorian/solar or lunar, including leap month when lunar.
- Birth time, as exact as available.
- Birth place and timezone if chart calculation is requested.
- Sex/gender only when Da Yun direction or Zi Wei Dou Shu calculation is requested.
- Latitude/longitude when Western astrology or Vedic ascendant, houses, or lagna are requested.
- Verified BaZi, Zi Wei, birth chart, Gu Zhan, and/or Vedic if the user already has them.
- Source/settings for verified charts, such as app/site, tropical vs sidereal, house system, and true solar time policy.
- Tai Yuan preference when using Tai Yuan: engine-calculated value, user-verified value, or adjusted value for premature/gestational considerations.
- Numerology scope only when requested: date-only numbers, or explicit name method if the user asks for name-based numerology.

## Workflow

1. Choose mode:
   - `verified-chart`: user provides BaZi, Zi Wei, birth chart, Gu Zhan, or Vedic facts.
   - `full-calculator`: for complete multi-system readings, run each requested calculator in sequence, collect one unified chart summary, then ask for confirmation before interpretation.
   - `bazi-calculator`: run `scripts/bazi_profile.py` for BaZi after dependency is available.
   - `ziwei-calculator`: run `scripts/ziwei_profile.mjs` for Zi Wei Dou Shu when gender and birth time are available.
   - `astrology-calculator`: run `scripts/astro_profile.py` for Western astrology, Gu Zhan, and/or Vedic when `swisseph` is available; use the `traditional`/`Gu Zhan` system alias for Gu Zhan rather than a separate mode.
   - `numerology-calculator`: run `scripts/numerology_profile.py` when the user asks for numerology or a full multi-system reading that includes it.
   - `partial`: name/date only, no hidden chart-dependent claims.
2. Normalize chart facts into the schema in `references/calculation-contract.md`.
3. If Tai Yuan will be used and the user did not supply a verified value, ask whether to keep the engine-calculated Tai Yuan or provide/confirm an adjusted Tai Yuan before surfacing it in the chart summary. This is especially important for premature birth or any school that adjusts Tai Yuan by gestational assumptions.
4. For BaZi, surface deterministic structure facts such as Earthly BranchSan Hui, San He/Ban He, Liu He, Chong, Xing, Hai, Po, verified or confirmed auxiliary facts such as Tai Yuan, and Da Yun/Liu Nian when sex/gender and target years are supplied.
5. For Zi Wei, Gu Zhan, and Vedic, surface chart facts only from the helper output or user-verified data; record settings such as leap monthhandling, house model, sect, ayanamsa, node choice, and timing model.
6. If any helper script exits non-zero or returns invalid JSON, show the error briefly, do not interpret partial failed output as chart fact, and ask whether to retry with corrected input or switch to `verified-chart` mode.
7. Show the computed or parsed chart summary and ask for confirmation before interpretation. If any category boundary warning appears, ask whether to use the current categorization, an alternate calculation, or the user's verified chart.
8. Read `references/interpretation-framework.md` and `references/akashic-style-patterns.md` before generating the final reading.
9. Use cross-system correction as the primary synthesis move: if one system appears to show absence and another shows analogous strength, reframe the life lesson around access, containment, release, or domain of expression rather than simplistic deficiency. Do not claim the systems are measuring the same element.
10. Apply `references/safety-privacy-boundary.md` to the final wording, especially when using examples or prior readings as style references.
11. If using bundled scripts, include calculation notes and limitations in the final response.
12. After the initial reading, invite focused feedback. If the user corrects or nuances a pattern, load `references/refinement-patterns.md` and re-synthesize with the correction integrated.

## Reference Routing

| Need | Load |
| --- | --- |
| Input/output schema, chart settings, and confirmation rules | `references/calculation-contract.md` |
| Mapping verified chart mechanics to a reading | `references/interpretation-framework.md` |
| Long-form Akashic reading structure and tone | `references/akashic-style-patterns.md` |
| Gu Zhan / traditional Western astrology layer | `references/traditional-astrology-module.md` |
| Feedback-based second-pass synthesis | `references/refinement-patterns.md` |
| Numerology calculation and cross-mapping | `references/numerology-module.md` |
| Synthetic example of correction-first reading | `references/worked-example-anonymous.md` |
| Privacy, partial-data, and high-stakes boundaries | `references/safety-privacy-boundary.md` |
| Engine provenance, license, and upgrade notes | `references/upstream-attribution.md` |

## Runtime Dependencies

| Calculator | Script | Runtime | Dependency Status |
| --- | --- | --- | --- |
| BaZi | `scripts/bazi_profile.py` | Python 3 | `lunar_python` is vendored under `scripts/vendor/`; `scripts/requirements.txt` is only for upgrades or external installs. |
| Zi Wei Dou Shu | `scripts/ziwei_profile.mjs` | Node.js | `iztro` is vendored under `scripts/vendor/iztro/`; no npm install is needed for normal use. |
| Western astrology/Gu Zhan/Vedic | `scripts/astro_profile.py` | Python 3 | Requires user-installed `pyswisseph` from `scripts/requirements-astro.txt`; check Swiss Ephemeris licensing before product use. |
| Numerology | `scripts/numerology_profile.py` | Python 3 | No external dependency; date arithmetic only. |

## Script Use

For BaZi calculation with Gregorian or lunar date/time:

```bash
python3 scripts/bazi_profile.py --input birth.json
```

The skill vendors a MIT copy of `lunar_python` under `scripts/vendor/` so the helper can run offline in normal use. `scripts/requirements.txt` documents the upstream package constraint for upgrades or external environments.

To request Da Yun and specific Liu Nian, include `gender` and `target_years`, for example:

```json
{"calendar":"solar","birth_date":"YYYY-MM-DD","birth_time":"HH:MM","birth_place":"City, Region","gender":"female","target_years":[2026]}
```

If the user provides a verified Tai Yuan, keep it separate from the engine-computed value:

```json
{"verified_tai_yuan":"<verified_ganzhi_pillar>"}
```

For Zi Wei Dou Shu:

```bash
node scripts/ziwei_profile.mjs --input birth.json
```

For Western astrology, Gu Zhan, or Vedic, install the optional ephemeris dependency and supply coordinates:

```bash
python3 scripts/astro_profile.py --input birth.json
```

`scripts/astro_profile.py` requires `pyswisseph`; check the Swiss Ephemeris AGPL/commercial license before product use. Do not substitute sun-sign astrology or generic Vedic summaries for calculated chart facts.

To request Gu Zhan output, include a traditional system alias:

```json
{"systems":["western","traditional","vedic"],"target_years":[2026]}
```

The Gu Zhan layer is a traditional Western/Hellenistic-style sublayer: tropical zodiac, whole-sign houses from Ascendant, traditional seven-planet rulers, sect, Fortune/Spirit lots, and annual profections. It does not calculate bounds/terms, decans, fixed stars, primary directions, or zodiacal releasing.

For date-based numerology:

```bash
python3 scripts/numerology_profile.py --input birth.json
```

Use numerology as a supplemental lens. Do not calculate name-based Expression/Destiny numbers unless the user explicitly provides the name form and asks for that school.
