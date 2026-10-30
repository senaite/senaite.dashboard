// Texts of the page. The server translates them and hands them over
// with the bootstrap data; a missing one shows its key.

let strings = {};
let language = "en";

export function setStrings(values, lang) {
  strings = values || {};
  language = lang || "en";
}

export function t(key) {
  return strings[key] || key;
}

// A text with placeholders such as {count} filled in, so that every
// language puts them where its word order wants them
export function format(key, values) {
  return t(key).replace(/\{(\w+)\}/g, (match, name) =>
    name in values ? String(values[name]) : match);
}

export function getLanguage() {
  return language;
}

// A stored title is text, or {language: text}
export function titleText(title) {
  if (!title || typeof title === "string") {
    return title || "";
  }
  return title[language] || title.en || Object.values(title)[0] || "";
}

// Change a title in the language in use, keeping its other languages
export function withTitle(title, text) {
  if (title && typeof title === "object") {
    return {...title, [language]: text};
  }
  return text;
}

// Change a longer text in the language in use. Unlike a title it is
// kept per language from the first change on, so that a note can say
// the same in every language of the site.
export function withText(value, text) {
  const texts = value && typeof value === "object" ? value
    : (value ? {[language]: value} : {});
  return {...texts, [language]: text};
}
