<div align="center">

# 🔮 vera-akashic-life-reading

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Node.js 18+](https://img.shields.io/badge/Node.js-18+-339933?logo=node.js&logoColor=white)](https://nodejs.org)
[![Claude Skill](https://img.shields.io/badge/Claude-Skill-D97706)](https://claude.ai)

**Five divination systems. One Akashic reading.**  
**五大命理系统，一份阿卡西灵魂记录。**

</div>

---

Who were you before this life? What did you carry into it? What are you here to complete?

你前世是谁？你带着什么来到这一世？你此生的使命是什么？

These are not mystical questions — they are signal-extraction problems.  
Every system captures part of the signal. None captures all of it.  
This skill runs five at once.

这些不是玄学问题，而是信号提取问题。  
每套命理系统只能捕捉到一部分信号，没有任何一套能捕捉全部。  
这个技能同时运行五套，从五个维度共同读取你的阿卡西记录。

---

## The reading single-system readers get wrong  
## 单一系统无法给你的解读

Your BaZi shows no earth in the chart.  
Your Sun sign is Virgo — the most earth sign there is.

你的八字无土。  
你的太阳星座是处女座——最具土元素的星座。

A single-system reader says: *"You lack earth. Ground yourself."*

单一系统解读师会说：*「你缺土，你需要接地气。」*

The five-system reading says something else:  
Earth is not absent. It is locked — expressed through Virgo's intellectual precision, not through material stability. The life lesson is not to find earth. It is to understand which kind of earth you already are, and why it never feels like enough.

五系统解读的答案截然不同：  
土不是缺失的，而是被锁住了——它通过处女座的智识精准性来表达，而非物质层面的稳定。人生课题不是去寻找土，而是理解你已经是哪种土，以及为什么它从来感觉不够。

**That correction — from "missing" to "misread" — is what five systems make possible.**  
**这个修正——从「缺失」到「误读」——正是五套系统才能做到的事。**

---

## What you get · 你会得到什么

```
Who you were before this life          你前世是谁
What you carried into it               你带进这一世的是什么
What you are here to complete          你此生要完成的使命
Which patterns keep repeating — why    哪些模式在反复出现——以及为什么
Where your gifts actually live         你的天赋真正在哪里
What your relationships are practicing 你的关系在练习什么
What your work is really about         你的工作真正关于什么
What to do in the next 90 days        接下来 90 天该做什么
```

Not five readings stacked together.  
One Akashic reading, cross-validated across five coordinate systems.

不是五份解读的叠加，而是一份阿卡西记录——经由五套坐标系交叉验证后得出。

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
LLM 负责解读，脚本负责计算，两者角色严格分离。

---

## Try it · 开始使用

> [!IMPORTANT]
> **Run this skill in a private (incognito) Claude session.**  
> **请在隐私（无痕）模式下运行此技能。**  
> Your birth date, birth time, location, and gender are sensitive personal data.  
> Incognito mode prevents this information from being saved to your conversation history.  
> 出生日期、出生时间、地点与性别均属敏感个人信息，无痕模式可避免其被保存至对话记录。

Install via the Claude Code skill registry or copy this folder into your skills directory.

```
"Give me a full Akashic life reading — BaZi, Zi Wei, birth chart, and Vedic"
"I only have a birthdate. Give me a partial reading."
"I already have my chart from another app. Just interpret it."
"What past-life archetypes does my chart point to?"
```

---

## Run the calculators

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

## Five systems, one reading · 五套系统，一份解读

| System 系统 | Script | Engine | Install |
|---|---|---|---|
| BaZi 八字 | `bazi_profile.py` | lunar_python | bundled — offline |
| Zi Wei Dou Shu 紫微斗数 | `ziwei_profile.mjs` | iztro | bundled — offline |
| Western + Traditional + Vedic 西方 + 古典 + 吠陀 | `astro_profile.py` | pyswisseph | `pip install pyswisseph` |
| Numerology 数字学 | `numerology_profile.py` | none | no dependencies |

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
