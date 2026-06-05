<div align="center">

# vera-akashic-life-reading

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.10+ for astrology](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Node.js 18+](https://img.shields.io/badge/Node.js-18%2B-339933?logo=node.js&logoColor=white)](https://nodejs.org)
[![Skill](https://img.shields.io/badge/AI-Skill-7C3AED)](https://github.com/VeraSuperHub)

**Five deterministic chart engines. One symbolic Akashic reading workflow.**<br>
**五套确定性计算引擎，一份跨系统阿卡西灵魂解读流程。**

</div>

---

This repository contains the public skill folder and calculation engine for
Akashic-style life readings across BaZi, Zi Wei Dou Shu, Western astrology,
traditional Western astrology, Vedic/Jyotish astrology, and numerology.

The boundary is strict:

```text
scripts calculate chart facts -> user confirms chart facts -> LLM interprets
```

The language model should never freehand-calculate charts from memory.

---

## Download

Use one of these options.

### Option 1: Download ZIP

[Download the latest main branch as a ZIP](https://github.com/VeraSuperHub/vera-akashic-life-reading/archive/refs/heads/main.zip)

If the GitHub download button is not working, use the direct codeload URL:

```bash
curl -L -o vera-akashic-life-reading-main.zip \
  https://codeload.github.com/VeraSuperHub/vera-akashic-life-reading/zip/refs/heads/main
```

### Option 2: Clone With Git

```bash
git clone https://github.com/VeraSuperHub/vera-akashic-life-reading.git
cd vera-akashic-life-reading
```

---

## What This Skill Produces

It supports symbolic, reflective readings such as:

- past-life and this-life archetype readings
- life-purpose and karmic-pattern readings
- BaZi, Zi Wei, Western, traditional Western, Vedic, and numerology synthesis
- cross-system correction, where one chart system prevents a simplistic reading of another

It does not provide factual proof of hidden records, deterministic fate claims,
medical advice, legal advice, financial advice, or guaranteed relationship outcomes.

---

## Calculation Engine

| Layer | Script | Engine | Dependency status |
|---|---|---|---|
| BaZi | `scripts/bazi_profile.py` | `lunar_python` | vendored, offline |
| Zi Wei Dou Shu | `scripts/ziwei_profile.mjs` | `iztro` | vendored, offline |
| Western astrology | `scripts/astro_profile.py` | `Kerykeion` + Swiss Ephemeris | optional install |
| Traditional Western | `scripts/astro_profile.py` | Kerykeion tropical positions + local traditional layer | optional install |
| Vedic/Jyotish | `scripts/astro_profile.py` | `PyJHora` + Swiss Ephemeris | optional install, Python 3.10+ recommended |
| Numerology | `scripts/numerology_profile.py` | local arithmetic | no external dependency |
| Full orchestration | `scripts/full_calculator.py` | wraps the requested helpers | uses available engines |

Install optional astrology dependencies only when Western/traditional/Vedic
calculation is needed:

```bash
python3 -m pip install -r scripts/requirements-astro.txt
python3 scripts/astro_profile.py --check-deps
```

If optional astrology dependencies are unavailable, provide verified chart facts
manually or run the non-astrology calculators only.

---

## Quick Smoke Test

After downloading:

```bash
python3 scripts/smoke_all.py
```

Expected behavior:

- BaZi, numerology, Zi Wei, and full-calculator checks should pass.
- Astrology may be reported as skipped if Python 3.10+, Kerykeion, PyJHora, or
  pyswisseph are not available in the current environment.

Run the unified calculator envelope:

```bash
python3 scripts/full_calculator.py --self-test
```

---

## Run Individual Calculators

Create `birth.json`:

```json
{
  "calendar": "solar",
  "birth_date": "1990-06-15",
  "birth_time": "08:30",
  "timezone": "+08:00",
  "latitude": 39.9,
  "longitude": 116.4,
  "gender": "female",
  "systems": ["western", "traditional", "vedic"],
  "target_years": [2025, 2026]
}
```

Then run:

```bash
# BaZi
python3 scripts/bazi_profile.py --input birth.json

# Zi Wei Dou Shu
node scripts/ziwei_profile.mjs --input birth.json

# Western + traditional Western + Vedic/Jyotish
python3 scripts/astro_profile.py --input birth.json

# Numerology
python3 scripts/numerology_profile.py --input birth.json

# Unified envelope
python3 scripts/full_calculator.py --input birth.json
```

---

## How The Reading Works

```text
Birth data
   |
   v
Deterministic calculators
   |-- BaZi: pillars, branch structures, luck cycles
   |-- Zi Wei: palaces, stars, transformations
   |-- Western: planets, houses, aspects
   |-- Traditional Western: sect, lots, annual profections
   |-- Vedic/Jyotish: lagna, nakshatra, Vimshottari dasha
   |-- Numerology: date-based numbers
   |
   v
Chart confirmation
   |
   v
Symbolic Akashic interpretation
```

Where systems disagree, the reading should use that tension carefully. For
example, a BaZi "missing" phase should not be flattened into a generic
deficiency if another verified system shows a strong analogous expression
pattern. The systems are compared; they are not treated as identical.

---

## Privacy

Birth date, birth time, location, gender, and chart outputs are sensitive
personal data. Use private sessions when possible, ask only for fields needed
for the requested calculator, and do not store user birth data unless the user
explicitly asks for an artifact.

---

## License

GPL-3.0 (C) [VeraSuperHub](https://github.com/VeraSuperHub)

Anyone who modifies or distributes this code must release it under GPL-3.0.
Bundled engines `lunar_python` and `iztro` retain their original MIT licenses.
Kerykeion, PyJHora, Swiss Ephemeris, and `pyswisseph` have their own licensing
terms; confirm the license path before product or hosted use.

---

<div align="center">

**[VeraSuperHub](https://github.com/VeraSuperHub)**  
Open-source skill ecosystem for domain experts

</div>
