// The theme of the dashboard: "light", "dark" or "auto", which follows
// the system. The colors are in styles/_themes.scss; the choice is
// set on the root element, so dialogs and drawers outside the app
// follow it as well, and kept per browser.

export const THEMES = ["light", "dark", "auto"];

const STORAGE_KEY = "senaite.dashboard.theme";

function isTheme(name) {
  return THEMES.includes(name);
}

// The storage can be refused, e.g. in a private window; the theme then
// is not remembered, which is no reason to fail
function readStored() {
  try {
    return window.localStorage.getItem(STORAGE_KEY);
  } catch (exc) {
    return null;
  }
}

function writeStored(name) {
  try {
    window.localStorage.setItem(STORAGE_KEY, name);
  } catch (exc) {
    // not remembered, see readStored
  }
}

// The theme chosen in this browser, light as SENAITE otherwise
export function initialTheme() {
  const stored = readStored();
  return isTheme(stored) ? stored : "light";
}

export function applyTheme(name) {
  document.documentElement.setAttribute("data-sd-theme", name);
}

export function chooseTheme(name) {
  applyTheme(name);
  writeStored(name);
}
