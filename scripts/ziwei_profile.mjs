#!/usr/bin/env node
/**
 * Emit normalized Zi Wei Dou Shu JSON using bundled iztro.
 *
 * This script performs calculation only. It does not generate spiritual
 * interpretation text.
 */

import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);

globalThis.self = globalThis;
const iztro = require(resolve(__dirname, "vendor/iztro/iztro.min.js"));
const iztroPackage = JSON.parse(readFileSync(resolve(__dirname, "vendor/iztro/package.json"), "utf8"));

function parseArgs(argv) {
  const args = { input: null, selfTest: false };
  for (let i = 2; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--self-test") {
      args.selfTest = true;
    } else if (arg === "--input") {
      args.input = argv[i + 1];
      i += 1;
    } else {
      throw new Error(`unknown argument: ${arg}`);
    }
  }
  return args;
}

function readPayload(args) {
  if (args.selfTest) {
    return {
      calendar: "solar",
      birth_date: "2000-08-16",
      birth_time: "03:30",
      gender: "male",
      language: "zh-CN",
    };
  }
  const text = args.input ? readFileSync(args.input, "utf8") : readFileSync(0, "utf8");
  const payload = JSON.parse(text);
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    throw new Error("input JSON must be an object");
  }
  return payload;
}

function formatDate(value) {
  if (!value) {
    throw new Error("birth_date is required");
  }
  const parts = String(value).trim().split("-").map((part) => Number(part));
  if (parts.length !== 3 || parts.some((part) => !Number.isInteger(part))) {
    throw new Error("birth_date must use YYYY-MM-DD");
  }
  return `${parts[0]}-${parts[1]}-${parts[2]}`;
}

function parseTime(value) {
  if (!value) {
    throw new Error("birth_time is required for Zi Wei time index");
  }
  const parts = String(value).trim().split(":").map((part) => Number(part));
  if (![2, 3].includes(parts.length) || parts.some((part) => !Number.isFinite(part))) {
    throw new Error("birth_time must use HH:MM or HH:MM:SS");
  }
  const [hour, minute, second = 0] = parts;
  if (hour < 0 || hour > 23 || minute < 0 || minute > 59 || second < 0 || second > 59) {
    throw new Error("birth_time is out of range");
  }
  return { hour, minute, second };
}

function ziweiTimeIndex(payload) {
  if (payload.ziwei_time_index !== undefined) {
    const value = Number(payload.ziwei_time_index);
    if (!Number.isInteger(value) || value < 0 || value > 12) {
      throw new Error("ziwei_time_index must be an integer from 0 to 12");
    }
    return value;
  }
  const { hour, minute, second } = parseTime(payload.birth_time);
  const minutes = hour * 60 + minute + second / 60;
  if (minutes >= 23 * 60) {
    return 12;
  }
  if (minutes < 60) {
    return 0;
  }
  return Math.floor((minutes - 60) / 120) + 1;
}

function normalizeGender(value) {
  if (value === undefined || value === null || value === "") {
    throw new Error("gender is required for Zi Wei Dou Shu calculation");
  }
  const text = String(value).trim().toLowerCase();
  if (["male", "man", "m", "1", "男"].includes(text)) {
    return "男";
  }
  if (["female", "woman", "f", "0", "女"].includes(text)) {
    return "女";
  }
  throw new Error("gender must be male/female, 男/女, 1/0");
}

function normalizeStar(star) {
  const result = {
    name: star.name,
    type: star.type,
    scope: star.scope,
  };
  if (star.brightness) {
    result.brightness = star.brightness;
  }
  if (star.mutagen) {
    result.mutagen = star.mutagen;
  }
  return result;
}

function normalizePalace(palace) {
  return {
    index: palace.index,
    name: palace.name,
    heavenly_stem: palace.heavenlyStem,
    earthly_branch: palace.earthlyBranch,
    is_body_palace: palace.isBodyPalace,
    is_original_palace: palace.isOriginalPalace,
    major_stars: palace.majorStars.map(normalizeStar),
    minor_stars: palace.minorStars.map(normalizeStar),
    adjective_stars: palace.adjectiveStars.map(normalizeStar),
    changsheng12: palace.changsheng12,
    boshi12: palace.boshi12,
    jiangqian12: palace.jiangqian12,
    suiqian12: palace.suiqian12,
    decadal: palace.decadal,
    ages: palace.ages,
  };
}

function targetDates(payload) {
  if (Array.isArray(payload.target_dates)) {
    return payload.target_dates.map((value) => String(value));
  }
  if (Array.isArray(payload.target_years)) {
    return payload.target_years.map((value) => `${Number(value)}-1-1`);
  }
  if (payload.target_years !== undefined) {
    return [String(Number(payload.target_years)) + "-1-1"];
  }
  return [];
}

function normalizeHoroscope(horoscope, targetDate) {
  return {
    target_date: targetDate,
    solar_date: horoscope.solarDate,
    lunar_date: horoscope.lunarDate,
    decadal: horoscope.decadal,
    age: horoscope.age,
    yearly: horoscope.yearly,
    monthly: horoscope.monthly,
    daily: horoscope.daily,
    hourly: horoscope.hourly,
  };
}

function buildProfile(payload) {
  const calendar = String(payload.calendar || "solar").trim().toLowerCase();
  const date = formatDate(payload.birth_date);
  const timeIndex = ziweiTimeIndex(payload);
  const gender = normalizeGender(payload.gender);
  const language = payload.language || "zh-CN";
  const fixLeap = payload.fix_leap === undefined ? true : Boolean(payload.fix_leap);
  const isLeapMonth = Boolean(payload.is_lunar_leap_month);

  let astrolabe;
  if (["solar", "gregorian", "公历", "阳历"].includes(calendar)) {
    astrolabe = iztro.astro.bySolar(date, timeIndex, gender, fixLeap, language);
  } else if (["lunar", "chinese_lunar", "农历", "阴历"].includes(calendar)) {
    astrolabe = iztro.astro.byLunar(date, timeIndex, gender, isLeapMonth, fixLeap, language);
  } else {
    throw new Error("calendar must be solar/gregorian or lunar/chinese_lunar");
  }

  const targets = targetDates(payload);
  return {
    ok: true,
    mode: "ziwei-calculator",
    engine: {
      name: "iztro",
      version: iztroPackage.version,
      upstream: "https://github.com/SylarLong/iztro",
      license: "MIT",
    },
    input: {
      calendar,
      birth_date: payload.birth_date,
      birth_time: payload.birth_time,
      gender: payload.gender,
      ziwei_time_index: timeIndex,
      is_lunar_leap_month: isLeapMonth,
      fix_leap: fixLeap,
      language,
    },
    ziwei: {
      solar_date: astrolabe.solarDate,
      lunar_date: astrolabe.lunarDate,
      chinese_date: astrolabe.chineseDate,
      time: astrolabe.time,
      time_range: astrolabe.timeRange,
      sign: astrolabe.sign,
      zodiac: astrolabe.zodiac,
      soul: astrolabe.soul,
      body: astrolabe.body,
      five_elements_class: astrolabe.fiveElementsClass,
      earthly_branch_of_soul_palace: astrolabe.earthlyBranchOfSoulPalace,
      earthly_branch_of_body_palace: astrolabe.earthlyBranchOfBodyPalace,
      palaces: astrolabe.palaces.map(normalizePalace),
      horoscopes: targets.map((dateValue) => normalizeHoroscope(astrolabe.horoscope(dateValue), dateValue)),
    },
    calculation_notes: [
      `Zi Wei output is calculated with the bundled MIT iztro ${iztroPackage.version} UMD build.`,
      "timeIndex uses iztro's 0-12 Chinese-hour convention: early Zi, Chou...Hai, late Zi.",
      "This helper does not apply geocoding or true-solar-time correction before Zi Wei calculation.",
      "Different Zi Wei schools vary on leap-month, year-boundary, and transformation rules; confirm settings before interpretation.",
    ],
  };
}

function main() {
  try {
    const args = parseArgs(process.argv);
    const result = buildProfile(readPayload(args));
    if (args.selfTest) {
      if (result.ziwei.soul !== "破军" || result.ziwei.body !== "文昌" || result.ziwei.palaces.length !== 12) {
        throw new Error("self-test mismatch");
      }
    }
    process.stdout.write(JSON.stringify(result, null, 2));
    process.stdout.write("\n");
  } catch (error) {
    process.stdout.write(JSON.stringify({ ok: false, error: error.message }, null, 2));
    process.stdout.write("\n");
    process.exitCode = 1;
  }
}

main();
