// Numbers, dates and durations in the language of the page.

import {format, getLanguage, t} from "./i18n";

export function formatNumber(value) {
  if (value === null || value === undefined) {
    return "–";
  }
  const compact = Math.abs(value) >= 10000;
  return new Intl.NumberFormat(getLanguage(), {
    notation: compact ? "compact" : "standard",
    maximumFractionDigits: compact ? 1 : 0
  }).format(value);
}

function formatDecimal(value, digits = 1) {
  return new Intl.NumberFormat(getLanguage(), {
    maximumFractionDigits: digits
  }).format(value);
}

export function formatPercent(value) {
  return new Intl.NumberFormat(getLanguage(), {
    style: "percent",
    maximumFractionDigits: 0
  }).format(value);
}

// A duration in hours: hours below two days, days above
export function formatDuration(hours) {
  if (hours === null || hours === undefined) {
    return {value: "–", unit: ""};
  }
  if (hours < 48) {
    return {value: formatDecimal(hours, hours < 10 ? 1 : 0),
            unit: t("hours")};
  }
  return {value: formatDecimal(hours / 24, 1), unit: t("days")};
}

// A date from the server, or null for anything that is none. The text
// is read with Date.parse and the date made from the number: a script
// of the page or of the browser may replace Date with one that fails
// on what the browser's own reads, and an invalid date must not reach
// Intl, which throws on it.
export function toDate(value) {
  if (value instanceof Date) {
    return Number.isNaN(value.getTime()) ? null : value;
  }
  if (typeof value !== "string" && typeof value !== "number") {
    return null;
  }
  const time = typeof value === "number" ? value : Date.parse(value);
  return Number.isNaN(time) ? null : new Date(time);
}

// Whether a date lies before now
export function isPast(value) {
  const date = toDate(value);
  return Boolean(date) && date.getTime() < Date.now();
}

export function formatDate(iso) {
  const date = toDate(iso);
  if (!date) {
    return "";
  }
  return new Intl.DateTimeFormat(getLanguage(), {
    day: "numeric", month: "short", year: "numeric"
  }).format(date);
}

export function formatDateTime(iso) {
  const date = toDate(iso);
  if (!date) {
    return "";
  }
  return new Intl.DateTimeFormat(getLanguage(), {
    day: "numeric", month: "short", hour: "2-digit", minute: "2-digit"
  }).format(date);
}

// "in 3 days", "2 hours ago"
export function formatRelative(iso, now = Date.now()) {
  const date = toDate(iso);
  if (!date) {
    return "";
  }
  const seconds = (date.getTime() - now) / 1000;
  const units = [
    ["day", 86400], ["hour", 3600], ["minute", 60]
  ];
  const rtf = new Intl.RelativeTimeFormat(getLanguage(), {numeric: "auto"});
  for (const [unit, size] of units) {
    if (Math.abs(seconds) >= size || unit === "minute") {
      return rtf.format(Math.round(seconds / size), unit);
    }
  }
  return "";
}

// Label of a period on a time axis
export function formatPeriod(iso, interval, long = false) {
  const date = toDate(iso);
  if (!date) {
    return "";
  }
  const options = interval === "month"
    ? {month: long ? "long" : "short", year: long ? "numeric" : undefined}
    : {day: "numeric", month: "short"};
  return new Intl.DateTimeFormat(getLanguage(), options).format(date);
}

export function formatToday(iso) {
  return new Intl.DateTimeFormat(getLanguage(), {
    weekday: "long", day: "numeric", month: "long"
  }).format(toDate(iso) || new Date());
}

// Caption of one period of a trend: "This week", "Week of 12 Oct"
export function formatBucket(iso, interval, current) {
  if (current) {
    return t(`current_${interval}`);
  }
  if (interval === "week") {
    return format("week_of", {date: formatPeriod(iso, interval)});
  }
  return formatPeriod(iso, interval, interval === "month");
}
