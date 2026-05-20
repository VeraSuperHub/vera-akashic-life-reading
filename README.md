<div align="center">

# 🔮 vera-akashic-life-reading

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Node.js 18+](https://img.shields.io/badge/Node.js-18+-339933?logo=node.js&logoColor=white)](https://nodejs.org)
[![Claude Skill](https://img.shields.io/badge/Claude-Skill-D97706)](https://claude.ai)

</div>

---

**Who were you before this life?**  
**What did you carry into it?**  
**What are you here to complete?**

These are not mystical questions. They are signal-extraction problems.  
Every divination system captures part of the signal. None captures all of it.

This skill runs five systems at once — and reads the Akashic from all five together.

---

## The example that explains everything

Your BaZi shows no earth in the chart.  
Your Sun sign is Virgo — the most earth sign there is.

A single-system reader says: *"You lack earth. Ground yourself."*  
That is the wrong reading.

The five-system reading says something else:  
Earth is not absent. It is locked — expressed through Virgo's intellectual precision, not through material stability. The life lesson is not to find earth. It is to understand which kind of earth you already are, and why it never feels like enough.

**That correction — from "missing" to "misread" — is what five systems make possible.**

---

## What this skill generates

```
Who you are at the soul level
Who you were in past lives
What contracts you came here to fulfill
What patterns keep repeating — and why
Where your gifts actually live
What your relationships are practicing
What your work is really about
What to do in the next 90 days
```

Not five separate readings stacked together.  
One Akashic reading, cross-validated across five coordinate systems.

---

## How it works

```
Your birth data
       |
       v
Five deterministic calculators
  BaZi         -> energy structure, elemental dynamics, Da Yun / Liu Nian
  Zi Wei       -> life palaces, major stars, Si Hua, horoscopes
  Western      -> planets, houses, aspects, psychological texture
  Traditional  -> sect, angularity, lots, annual profections
  Vedic        -> nakshatra, lagna, Vimshottari dasha
       |
       v
You confirm the chart
       |
       v
Cross-system correction
Where models disagree is where the real reading lives
       |
       v
Your Akashic reading
```

The LLM interprets. The scripts calculate. These two roles never swap.

---

## Quick start

```bash
git clone https://github.com/VeraSuperHub/vera-akashic-life-reading.git

# BaZi — offline, no install needed
python3 scripts/bazi_profile.py --input birth.json

# Zi Wei Dou Shu — offline, no install needed
node scripts/ziwei_profile.mjs --input birth.json

# Western + Traditional + Vedic
pip install pyswisseph
python3 scripts/astro_profile.py --input birth.json

# Numerology
python3 scripts/numerology_profile.py --input birth.json
```

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

---

## Using as a Claude Code skill

> [!IMPORTANT]
> **Run this skill in a private (incognito) Claude session.**
> Your birth date, birth time, location, and gender are sensitive personal data.
> Incognito mode prevents this information from being saved to your conversation history.

Install via the Claude Code skill registry or copy this folder into your skills directory.

```
"Give me a full Akashic life reading — BaZi, Zi Wei, birth chart, and Vedic"
"I only have a birthdate. Give me a partial reading."
"I already have my chart from another app. Just interpret it."
"What past-life archetypes does my chart point to?"
```

---

## Five systems, one reading

| System | Script | Engine | Install |
|---|---|---|---|
| BaZi | `bazi_profile.py` | lunar_python | bundled — offline |
| Zi Wei Dou Shu | `ziwei_profile.mjs` | iztro | bundled — offline |
| Western + Traditional + Vedic | `astro_profile.py` | pyswisseph | `pip install pyswisseph` |
| Numerology | `numerology_profile.py` | none | no dependencies |

---

## License

GPL-3.0 © [VeraSuperHub](https://github.com/VeraSuperHub)

Anyone who modifies or distributes this code must release it under GPL-3.0.  
Bundled engines `lunar_python` and `iztro` retain their original MIT licenses.  
`pyswisseph` is not bundled — confirm Swiss Ephemeris AGPL / commercial license before product use.

---

<div align="center">

**[VeraSuperHub](https://github.com/VeraSuperHub)**  
Open-source divination skill ecosystem for domain experts

</div>
