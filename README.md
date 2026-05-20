<div align="center">

# 🔮 vera-akashic-life-reading

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Node.js 18+](https://img.shields.io/badge/Node.js-18+-339933?logo=node.js&logoColor=white)](https://nodejs.org)
[![Claude Skill](https://img.shields.io/badge/Claude-Skill-D97706)](https://claude.ai)

</div>

---

**八字说没有火。星盘说火旺至极。**

这不是矛盾。这是你一直在做单一模型解读时，被系统性遗漏的信息。

**Your BaZi says no fire. Your birth chart says fire is dominant.**

This isn't a contradiction. This is the information that gets lost every time you trust only one system.

---

## 为什么五个系统，不是一个

每个命理系统都是模型。模型把人生压缩进自己的坐标系——压缩必然有损失。

八字能看到的，紫微看不完整。紫微能定位的，星盘解释不了原因。星盘里的心理动力，印占用 dasha 给出时间答案。古典占星告诉你这个力量当下的条件和可见度。

**没有哪个系统是错的。每个系统都只是不完整的。**

跨模型校正的价值不在于堆叠答案，在于找到任何单一模型无法单独回答的问题——然后用其他模型来回答它。

---

## Why five models, not one

Every divination system is a lossy compression of life. What BaZi sees, Zi Wei misses. What Zi Wei locates, Western astrology explains differently. What Western astrology frames psychologically, Vedic dasha answers temporally. What all of them describe in potential, Traditional astrology qualifies by condition.

**No system is wrong. Every system is incomplete.**

The point isn't to get five readings. It's to use the gaps between them.

---

## 这个技能做什么

- 用**确定性脚本**计算五个命理系统的命盘数据，LLM 只做解读，不推算
- 运行 Claude Code 后，自然语言触发，无需记命令
- 八字和紫微**无需安装依赖**，引擎已内置，离线可用
- 识别跨系统分歧，以校正而非堆叠为主要解读动作
- 支持"我已有命盘数据"模式——不想重新算就直接解读

## What this skill does

- Runs **deterministic calculators** for all five systems — the LLM interprets, never invents chart facts
- Natural language triggers inside Claude Code — no commands to memorize
- BaZi and Zi Wei work **offline with zero installation** — engines are bundled
- Detects cross-system divergence and uses it as the primary interpretation signal
- Supports `verified-chart` mode — paste your existing chart data and skip recalculation

---

## 30 秒上手 / 30-Second Start

```bash
# 克隆 / Clone
git clone https://github.com/VeraSuperHub/vera-akashic-life-reading.git

# 八字（离线可用）/ BaZi (offline)
python3 scripts/bazi_profile.py --input birth.json

# 紫微斗数（离线可用）/ Zi Wei (offline)
node scripts/ziwei_profile.mjs --input birth.json

# 西占 + 古占 + 印占 / Western + Traditional + Vedic
pip install pyswisseph
python3 scripts/astro_profile.py --input birth.json

# 数字学 / Numerology
python3 scripts/numerology_profile.py --input birth.json

# 自检所有脚本 / Self-test everything
python3 scripts/bazi_profile.py --self-test
node scripts/ziwei_profile.mjs --self-test
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

## 在 Claude Code 里使用 / Using in Claude Code

将本文件夹复制到 Claude Code 技能目录，或通过技能注册表安装。  
Copy this folder into your Claude Code skills directory, or install via the skill registry.

```
"帮我做一个完整的多模型灵魂课题解读，结合八字、紫微、星盘和印占"
"I want a full Akashic reading combining BaZi, Zi Wei, and my birth chart"
"只有生日没有时间，能做今生课题的简版吗？"
"我已经有四柱和星盘数据了，直接解读"
```

---

## 五系统一览 / Five Systems

| 系统 | 脚本 | 引擎 | 安装 |
|---|---|---|---|
| 八字 BaZi | `bazi_profile.py` | lunar_python | ✅ 已内置 / bundled |
| 紫微斗数 Zi Wei | `ziwei_profile.mjs` | iztro | ✅ 已内置 / bundled |
| 西占 + 古占 + 印占 | `astro_profile.py` | pyswisseph | 用户自装 / install separately |
| 数字学 Numerology | `numerology_profile.py` | — | ✅ 无依赖 / no deps |

---

## 版权 / License

GPL-3.0 © [VeraSuperHub](https://github.com/VeraSuperHub)

修改和分发本项目的代码，必须以相同的 GPL-3.0 协议开源。  
Anyone who modifies or distributes this code must release it under GPL-3.0.

内置引擎 `lunar_python` 和 `iztro` 保留其原始 MIT 协议。  
Bundled engines `lunar_python` and `iztro` retain their original MIT licenses.

`pyswisseph` 未随本项目分发，使用前请确认 Swiss Ephemeris 的 AGPL / 商业授权。  
`pyswisseph` is not bundled. Confirm Swiss Ephemeris AGPL / commercial license before use.

---

<div align="center">

**[VeraSuperHub](https://github.com/VeraSuperHub)** · 开源命理解读技能生态  
Open-source divination skill ecosystem for domain experts

</div>
