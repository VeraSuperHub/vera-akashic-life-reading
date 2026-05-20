<div align="center">

# 🔮 vera-akashic-life-reading

**The first open-source multi-model life interpretation engine for Claude Code**

*八字说没有火。星盘说火极旺。谁对？*
*两个都对——这才是问题所在。*

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Node.js](https://img.shields.io/badge/Node.js-18+-339933?logo=node.js&logoColor=white)](https://nodejs.org)
[![Claude Skill](https://img.shields.io/badge/Claude-Skill-orange)](https://claude.ai)

[English](#english) · [中文](#中文)

</div>

---

## English

### The problem with single-system readings

Every divination system is a model. A model compresses reality into its own coordinate space — and **every compression loses information**.

BaZi maps life into stems, branches, and five-phase dynamics.  
A birth chart maps it into planets, houses, and aspects.  
Zi Wei, Vedic, Traditional astrology each apply their own mapping.

When a system says "fire is absent" — it means fire is absent **in its coordinate space**.  
That tells you nothing about what the other four coordinate spaces show.

**Using five models isn't about getting five opinions. It's about recovering what each model loses.**

### What this skill does differently

Most astrology tools pick one system and go deep. This skill treats each system as **one sensor in an ensemble** — and uses the places where sensors disagree to locate what no single sensor can see.

```
BaZi        → energy structure, timing cycles, elemental dynamics
Zi Wei      → life arenas, role archetypes, palace emphasis
Western     → psychological texture, expression, relational patterns
Traditional → planet condition, visibility, symbolic timing (sect, lots, profections)
Vedic       → lunar mind, nakshatra instinct, dasha background
```

When all five point the same direction: **life main thread**.  
When they diverge: **the divergence is the signal**, not noise.

### How it works

```
Birth data (date · time · place)
        │
        ▼
Deterministic calculators — scripts compute, LLM never invents
  bazi_profile.py        → four pillars, structures, 大运/流年
  ziwei_profile.mjs      → 12 palaces, stars, 四化, horoscopes  
  astro_profile.py       → Western / Traditional / Vedic positions
  numerology_profile.py  → Life Path, Birthday Number
        │
        ▼
You confirm the chart
        │
        ▼
Cross-system correction → Akashic reading
```

### Quick start

```bash
# BaZi — no install needed, engine is bundled
python3 scripts/bazi_profile.py --input birth.json

# Zi Wei — no install needed, engine is bundled
node scripts/ziwei_profile.mjs --input birth.json

# Western / Traditional / Vedic
pip install pyswisseph
python3 scripts/astro_profile.py --input birth.json

# Numerology — no dependencies
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

### Install as a Claude Code skill

Copy this folder into your Claude Code skills directory, or install via the skill registry.

Trigger it naturally:

> *"I want a full Akashic life reading combining BaZi, Zi Wei, and my birth chart"*  
> *"I only have a birth date — give me a partial reading"*  
> *"I already have my chart data from another app — interpret it"*

---

## 中文

### 单一系统的根本局限

每一个命理系统都是一个**模型**。模型把现实压缩进自己的坐标系——**每一次压缩都必然有信息损失**。

八字把人生压缩进天干、地支、五行的坐标系。  
西洋星盘把它压缩进天体、宫位、相位的坐标系。  
紫微斗数、印度占星、古典占星各有各的压缩方式。

当一个系统说"命里没有火"——它的意思是**在它的坐标系里**没有火。  
这完全不告诉你其他四个坐标系看到了什么。

**用五个模型，不是为了得到五个意见，而是为了找回每个模型各自丢失的信息。**

### 跨模型校正是核心动作

大多数命理工具选一个系统然后走到底。这个技能把每个系统当作**集成模型里的一个传感器**——用传感器之间分歧的地方，定位任何单一传感器看不到的东西。

```
八字    → 气机结构、五行动力、大运/流年节律
紫微    → 人生宫位、角色原型、宫位强调
西洋    → 心理动力、表达方式、关系模式
古典    → 行星状态、可见性、时间主（sect、福点、小限）
印占    → 月亮心智、星宿本能、大运背景
```

所有系统指向同一方向：**人生主线**。  
系统之间出现分歧：**分歧本身就是信号**，不是噪声。

### 技能架构

```
出生信息（日期 · 时间 · 地点）
        │
        ▼
确定性脚本计算 — 脚本算，LLM 不凭空推算
  bazi_profile.py        → 四柱、结构、大运/流年
  ziwei_profile.mjs      → 十二宫、主星、四化、流年运势
  astro_profile.py       → 西占 / 古占 / 印占星位
  numerology_profile.py  → 生命数字、生日数字
        │
        ▼
你确认命盘
        │
        ▼
跨模型校正 → 阿卡西解读
```

### 快速开始

```bash
# 八字 — 无需安装，引擎已内置
python3 scripts/bazi_profile.py --input birth.json

# 紫微斗数 — 无需安装，引擎已内置
node scripts/ziwei_profile.mjs --input birth.json

# 西占 / 古占 / 印占
pip install pyswisseph
python3 scripts/astro_profile.py --input birth.json

# 数字学 — 无外部依赖
python3 scripts/numerology_profile.py --input birth.json
```

### 五个系统，四个脚本

| 系统 | 脚本 | 引擎 | 依赖 |
|---|---|---|---|
| 八字 | `bazi_profile.py` | `lunar_python` | 已内置 MIT |
| 紫微斗数 | `ziwei_profile.mjs` | `iztro` | 已内置 MIT |
| 西占 + 古占 + 印占 | `astro_profile.py` | `pyswisseph` | 用户自装 |
| 数字学 | `numerology_profile.py` | 无 | 无依赖 |

### 作为 Claude Code 技能使用

将本文件夹复制到你的 Claude Code 技能目录，或通过技能注册表安装。

自然语言触发：

> *"帮我做一个多模型灵魂课题解读，结合八字、星盘和紫微"*  
> *"只有生日和时间，能做今生课题的简版吗？"*  
> *"我已经有四柱和星盘数据，请直接解读"*  
> *"我要完整版前世今生阿卡西记录"*

---

## License

GPL-3.0 © [VeraSuperHub](https://github.com/VeraSuperHub)

This project is licensed under the GNU General Public License v3.0.  
Anyone who distributes or modifies this code must release their changes under the same license.

**Third-party engines:**

- [lunar-python](https://github.com/6tail/lunar-python) by 6tail — MIT
- [iztro](https://github.com/SylarLong/iztro) by SylarLong — MIT
- [Swiss Ephemeris](https://www.astro.com/swisseph/) by Astrodienst — AGPL / commercial  
  *(pyswisseph is not bundled; confirm license before commercial use)*
