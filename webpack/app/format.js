// Numbers, dates and durations in the language of the page.

import {getLanguage, t} from "./i18n";

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

export function formatDate(iso) {
  if (!iso) {
    return "";
  }
  return new Intl.DateTimeFormat(getLanguage(), {
    day: "numeric", month: "short", year: "numeric"
  }).format(new Date(iso));
}

export function formatDateTime(iso) {
  if (!iso) {
    return "";
  }
  return new Intl.DateTimeFormat(getLanguage(), {
    day: "numeric", month: "short", hour: "2-digit", minute: "2-digit"
  }).format(new Date(iso));
}

// "in 3 days", "2 hours ago"
export function formatRelative(iso, now = new Date()) {
  if (!iso) {
    return "";
  }
  const seconds = (new Date(iso) - now) / 1000;
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
  const date = new Date(iso);
  const options = interval === "month"
    ? {month: long ? "long" : "short", year: long ? "numeric" : undefined}
    : {day: "numeric", month: "short"};
  return new Intl.DateTimeFormat(getLanguage(), options).format(date);
}

export function formatToday(iso) {
  return new Intl.DateTimeFormat(getLanguage(), {
    weekday: "long", day: "numeric", month: "long"
  }).format(iso ? new Date(iso) : new Date());
}

// Caption of one period of a trend: "This week", "Week of 12 Oct"
export function formatBucket(iso, interval, current) {
  if (current) {
    return t(`current_${interval}`);
  }
  if (interval === "week") {
    return `${t("week_of")} ${formatPeriod(iso, interval)}`;
  }
  return formatPeriod(iso, interval, interval === "month");
}
