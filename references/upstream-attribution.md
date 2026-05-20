# Upstream Attribution

The bundled helper script uses `lunar_python` by 6tail for deterministic BaZi calculation.

- Repository: https://github.com/6tail/lunar-python
- License: MIT
- Role: deterministic Chinese solar/lunar calendar and BaZi calculation backend.

The `lunar_python` package source is vendored under `scripts/vendor/lunar_python` with the upstream MIT license at `scripts/vendor/LICENSE.lunar-python` so the helper can run without network installation. Refresh the vendored package from a trusted upstream release when upgrading the calculation engine.

The bundled Zi Wei Dou Shu helper uses `iztro` by SylarLong.

- Repository: https://github.com/SylarLong/iztro
- License: MIT
- Role: deterministic Zi Wei Dou Shu chart generation backend.

The browser UMD build is vendored under `scripts/vendor/iztro/iztro.min.js` with the upstream MIT license at `scripts/vendor/iztro/LICENSE.iztro` so the helper can run without network installation.

The optional Western astrology/Gu Zhan/Vedic helper uses Swiss Ephemeris through `pyswisseph` when installed by the user.

- Swiss Ephemeris: https://www.astro.com/swisseph/
- Python wrapper: https://github.com/astrorigin/pyswisseph
- License note: Swiss Ephemeris / pyswisseph is AGPL or commercial/professional licensed. Do not bundle it into a product or hosted service without confirming the license path.
- Role: deterministic tropical and sidereal ephemeris backend for planets, houses, ascendant, ayanamsa, nakshatra, and dasha-derived timing context. The Gu Zhan layer reuses tropical positions and adds local calculations for whole-sign houses, sect, traditional rulership, lots, and annual profections; it adds no new upstream dependency.

The numerology helper is local arithmetic code and has no upstream calculation dependency. It reduces date digits only and does not implement name-based Expression/Destiny numbers unless a future version adds an explicit school and transliteration policy.
