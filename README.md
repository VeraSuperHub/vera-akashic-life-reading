# vera-akashic-life-reading

**A multi-model life interpretation skill for Claude Code**  
**运行于 Claude Code 的多模型生命解读技能**

---

## The Core Idea · 核心理念

> *"I don't treat the chart as truth. I treat it as a model."*  
> *"我不把命盘当真理，我把命盘当模型。"*

Life is a high-dimensional system. BaZi, Zi Wei, Western astrology, Vedic, and Traditional astrology are each a different low-dimensional projection of it — each revealing part of the structure, each necessarily concealing another part.

人生是一个高维复杂系统。八字、紫微斗数、西洋星盘、印度占星、古典占星，都是对它的不同低维投影——每一个都能揭示一部分结构，也必然遮蔽另一部分信息。

The question is never *which system is right*. Every model is right within its own coordinate system. The question is: **what does each model reveal that the others cannot?**

问题从来不是"哪个系统更准"。每个模型在自己的坐标系里都是成立的。真正的问题是：**每个模型能看到什么，是其他模型看不到的？**

This skill's primary move is not stacking systems — it is **cross-system correction**: using the places where models disagree to locate what any single model cannot resolve on its own.

这个技能的核心动作不是堆叠系统，而是**跨模型校正**：用模型之间的分歧，定位任何单一模型无法单独回答的问题。

---

## What Each Model Sees · 每个模型看什么

| System · 系统 | Coordinate space · 坐标系 | Strongest at · 擅长 |
|---|---|---|
| 八字 BaZi | Stems, branches, five phases, ten gods | Energy structure, life rhythm, timing cycles · 气机结构、人生节律、运势周期 |
| 紫微斗数 Zi Wei | 12 palaces, major stars, transformations | Life arenas, role assignment, event fields · 人生宫位、角色分配、事件场域 |
| 西洋占星 Western | Planets, houses, aspects | Psychological texture, expression patterns, relational dynamics · 心理动力、表达方式、关系模式 |
| 古典占星 Traditional | Sect, angularity, lots, time lords | Condition, visibility, symbolic timing · 行星状态、可见性、时间主 |
| 印度占星 Vedic | Sidereal positions, nakshatras, dasha | Lunar mind pattern, karmic timing, dasha background · 月亮心智、业力节律、大运背景 |

---

## How Cross-System Correction Works · 跨模型校正如何运作

A single system answers *what*. Multiple systems together answer *how much*, *under what condition*, and *when*.

单一系统回答"是什么"。多系统一起回答"多少"、"在什么条件下"、"什么时候"。

**Example · 示例**

BaZi shows a strong branch combination — say, a fire formation. Does this mean fire energy is fully expressed in this person's life?

八字里有一个强烈的地支组合，比如形成了火局。这是否意味着火的力量在这个人生命中完全显化？

Not necessarily. The answer depends on what the other models show:

不一定。答案取决于其他模型显示了什么：

- Does Western astrology show fire themes strongly dignified and angular? → full expression likely  
  西洋星盘里火系行星是否入旺且在轴点？→ 很可能完全显化
- Does Vedic dasha activate fire-related planets in the current period? → timing confirmed  
  印占大运是否在当前激活了火系行星？→ 时机确认
- Does Zi Wei's career or expression palace reinforce the same theme? → life arena identified  
  紫微命盘的官禄宫或表达相关宫位是否呼应同一主题？→ 定位人生场域

If all systems point the same direction: the pattern is a life main thread.  
如果所有系统指向同一方向：这个模式是人生主线。

If systems diverge: the pattern may be latent structure, not yet externalized — or expressed only in a specific domain.  
如果系统之间出现分歧：这个模式可能是潜在结构，尚未外显——或只在某个特定领域表达。

This is not astrology versus astrology. This is **ensemble modeling of a complex system**.  
这不是命理和命理之间的竞争，这是**对复杂系统的集成建模**。

---

## Architecture · 架构

The hard boundary: **scripts calculate, the LLM interprets — never the reverse.**  
硬性边界：**脚本负责计算，LLM 负责解读——不能反过来。**

```
Birth data · 出生信息
      │
      ▼
Deterministic calculators · 确定性脚本
  bazi_profile.py        → BaZi pillars, structures, 大运/流年
  ziwei_profile.mjs      → 12 palaces, stars, 四化, horoscopes
  astro_profile.py       → Western / Traditional / Vedic positions
  numerology_profile.py  → Life Path, Birthday Number
      │
      ▼
Confirmed chart summary · 确认后的命盘摘要
      │
      ▼
Cross-system correction · 跨模型校正
      │
      ▼
Akashic reading · 阿卡西解读
```

---

## Five Systems, Four Scripts · 五系统，四个脚本

| System · 系统 | Script · 脚本 | Engine · 引擎 | Dependency |
|---|---|---|---|
| 八字 BaZi | `scripts/bazi_profile.py` | `lunar_python` | Vendored MIT · 已内置 |
| 紫微斗数 Zi Wei | `scripts/ziwei_profile.mjs` | `iztro` | Vendored MIT · 已内置 |
| 西洋 + 古典 + 印占 | `scripts/astro_profile.py` | `pyswisseph` | User installs · 用户自装 |
| 数字学 Numerology | `scripts/numerology_profile.py` | None | No dependency · 无依赖 |

BaZi and Zi Wei work **offline with no installation**.  
八字和紫微斗数**无需安装，离线可用**。

---

## Quick Start · 快速开始

```bash
# BaZi · 八字
python3 scripts/bazi_profile.py --input birth.json

# Zi Wei · 紫微斗数
node scripts/ziwei_profile.mjs --input birth.json

# Western / Traditional / Vedic · 西占 / 古占 / 印占
pip install pyswisseph
python3 scripts/astro_profile.py --input birth.json

# Numerology · 数字学
python3 scripts/numerology_profile.py --input birth.json
```

Minimal input · 最简输入：

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

Self-test all scripts · 自检所有脚本：

```bash
python3 scripts/bazi_profile.py --self-test
node scripts/ziwei_profile.mjs --self-test
python3 scripts/astro_profile.py --self-test
python3 scripts/numerology_profile.py --self-test
```

---

## Using as a Claude Code Skill · 作为 Claude Code 技能使用

Install via the Claude Code skill registry or copy this folder into your skills directory.  
通过 Claude Code 技能注册表安装，或将文件夹复制到你的技能目录。

Trigger naturally · 自然语言触发：

- *"帮我做一个多模型灵魂课题解读，结合八字、星盘和紫微"*
- *"I want a full Akashic life reading combining BaZi, Zi Wei, and my birth chart"*
- *"只有生日和时间，能做今生课题的简版吗？"*
- *"我已经有四柱和星盘数据，请直接解读"*

---

## Input Modes · 输入模式

| Mode · 模式 | When · 场景 |
|---|---|
| `full-calculator` | Full birth data, run all systems · 完整出生信息，运行所有系统 |
| `bazi-calculator` | BaZi only · 仅八字 |
| `ziwei-calculator` | Zi Wei only · 仅紫微 |
| `astrology-calculator` | Western / Traditional / Vedic · 西占、古占、印占 |
| `numerology-calculator` | Numerology only · 仅数字学 |
| `verified-chart` | You already have chart data from a trusted app · 已有可信软件的命盘数据 |
| `partial` | Name and date only, no birth time · 仅姓名和生日，无出生时间 |

---

## Repository Structure · 目录结构

```
vera-akashic-life-reading/
├── SKILL.md                          # Workflow and operating rules · 工作流与规则
├── agents/openai.yaml                # Agent interface config · 智能体接口配置
├── references/
│   ├── calculation-contract.md       # Input/output schema · 输入输出规范
│   ├── interpretation-framework.md   # Cross-system synthesis · 跨系统综合规则
│   ├── akashic-style-patterns.md     # Narrative style guide · 叙事风格
│   ├── traditional-astrology-module.md
│   ├── numerology-module.md
│   ├── refinement-patterns.md        # Feedback refinement · 反馈校正模式
│   ├── worked-example-anonymous.md   # Synthetic example · 合成示例
│   ├── safety-privacy-boundary.md    # Safety and privacy · 安全与隐私
│   └── upstream-attribution.md       # Engine licenses · 引擎版权
├── scripts/
│   ├── bazi_profile.py
│   ├── ziwei_profile.mjs
│   ├── astro_profile.py
│   ├── numerology_profile.py
│   ├── requirements.txt
│   ├── requirements-astro.txt
│   └── vendor/                       # Vendored MIT engines · 内置 MIT 引擎
│       ├── lunar_python/
│       └── iztro/
└── test-prompts.json                 # Test cases · 测试用例
```

---

## License Note · 版权说明

The skill's own code and vendored engines (`lunar_python`, `iztro`) are MIT licensed.  
技能本身的代码及内置引擎（`lunar_python`、`iztro`）均为 MIT 协议。

`pyswisseph` wraps Swiss Ephemeris — **AGPL or commercial licensed**.  
`pyswisseph` 封装了 Swiss Ephemeris——**AGPL 或商业授权**。

- Personal / open-source use: AGPL applies · 个人或开源使用：适用 AGPL
- Commercial / hosted service: purchase from [astro.com](https://www.astro.com/swisseph/) · 商业或托管服务：需购买商业授权

BaZi and Zi Wei carry no such restriction.  
八字和紫微斗数无此限制。

---

## Credits · 致谢

- [lunar-python](https://github.com/6tail/lunar-python) by 6tail — BaZi engine (MIT)
- [iztro](https://github.com/SylarLong/iztro) by SylarLong — Zi Wei engine (MIT)
- [Swiss Ephemeris](https://www.astro.com/swisseph/) by Astrodienst — planetary ephemeris (AGPL / commercial)

---

MIT © [VeraSuperHub](https://github.com/VeraSuperHub)
