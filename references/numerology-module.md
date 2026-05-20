# Numerology Module

Use numerology as an optional supplemental lens. It should never override verified chart mechanics.

## When To Include

- The user asks for numerology, life path, birthday number, name number, or a multi-system reading.
- The chart systems show a tension that numerology can name cleanly, such as private seeker versus public builder.
- The user only has name and birth date and wants a partial reflective reading.

Do not include numerology just to make the reading look larger.

## Deterministic Date Numbers

Use `scripts/numerology_profile.py` for date-based calculations.

- **Life Path:** use the full-date digit-sum convention: sum all digits in `YYYYMMDD`, then reduce the sum, preserving 11, 22, and 33 as master numbers.
- **Birthday Number:** reduce the day of month; retain the compound display such as `26/8` when applicable.
- **Attitude Number:** reduce month plus day; use only as a secondary lens.

Some numerology schools reduce year, month, and day separately first, then sum those components. If the user prefers that component-first school, state the convention mismatch and ask whether to calculate manually from their chosen method or treat numerology as user-verified input.

## Name-Based Numbers

Expression/Destiny Number depends on school, script, transliteration, birth name versus preferred name, and alphabet mapping. Do not calculate it unless the user explicitly supplies the name form and asks for that method.

For Chinese names, ask whether the user wants a transliteration-based Western numerology reading or a separate name-symbolism reading. Do not pretend one is mathematically equivalent to the other.

## Cross-Mapping

- Life Path can be treated as purpose vector.
- Birthday Number can be treated as outer role, performance style, or pressure point.
- BaZi day master can be treated as temperament and energy mechanics.
- Western Sun can be treated as conscious vitality; Ascendant as presentation and body-facing style.
- Vedic Moon nakshatra can be treated as instinctive mind pattern.

Use numerology to create a triangle of "purpose, temperament, presentation" only when the data is verified or clearly marked partial.
