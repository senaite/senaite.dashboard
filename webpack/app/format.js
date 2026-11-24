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

// The time of a date from the server, in milliseconds, or null for
// anything that is none. No Date is ever made from it: Intl formats the
// number itself. A browser extension may replace Date with one that
// fails whenever it is made with an argument, and the dashboard must
// not go down with it; Date.parse and Date.now still work then.
export function toTime(value) {
  if (typeof value === "number") {
    return Number.isFinite(value) ? value : null;
  }
  if (typeof value !== "string") {
    return null;
  }
  const time = Date.parse(value);
  return Number.isNaN(time) ? null : time;
}

// Whether a date lies before now
export function isPast(value) {
  const time = toTime(value);
  return time !== null && time < Date.now();
}

function formatTime(time, options) {
  return new Intl.DateTimeFormat(getLanguage(), options).format(time);
}

export function formatDate(iso) {
  const time = toTime(iso);
  if (time === null) {
    return "";
  }
  return formatTime(time, {day: "numeric", month: "short", year: "numeric"});
}

export function formatDateTime(iso) {
  const time = toTime(iso);
  if (time === null) {
    return "";
  }
  return formatTime(time, {
    day: "numeric", month: "short", hour: "2-digit", minute: "2-digit"
  });
}

// "in 3 days", "2 hours ago"
export function formatRelative(iso, now = Date.now()) {
  const time = toTime(iso);
  if (time === null) {
    return "";
  }
  const seconds = (time - now) / 1000;
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
  const time = toTime(iso);
  if (time === null) {
    return "";
  }
  const options = interval === "month"
    ? {month: long ? "long" : "short", year: long ? "numeric" : undefined}
    : {day: "numeric", month: "short"};
  return formatTime(time, options);
}

export function formatToday(iso) {
  const time = toTime(iso);
  return formatTime(time === null ? Date.now() : time,
                    {weekday: "long", day: "numeric", month: "long"});
}

// The hour of the day of a date, 0 to 23, in the time zone of the
// browser
export function hourOf(iso) {
  const time = toTime(iso);
  const hour = new Intl.DateTimeFormat("en-GB", {
    hour: "numeric", hourCycle: "h23"
  }).format(time === null ? Date.now() : time);
  return Number(hour);
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
