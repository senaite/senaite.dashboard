// Colors of the data. They are references to the custom properties of
// the theme (styles/_themes.scss), so the charts follow the theme.
// Set them as style, not as SVG attribute: `fill="var(...)"` is not
// resolved by every browser.
//
// Workflow states keep one color everywhere, by meaning, as in the
// SENAITE listings. Other groupings use the categorical slots in fixed
// order. Whatever does not fit is "Other" in a neutral gray.

function token(name) {
  return `var(--sd-${name})`;
}

export const NEUTRAL = token("neutral");
export const ACCENT = token("accent");

const CATEGORICAL = [1, 2, 3, 4, 5, 6, 7, 8].map(
  (slot) => token(`cat-${slot}`));

// The color group of each workflow state
const STATE_GROUPS = {
  // before the laboratory has the sample, or an order not taken on
  "state-new": [
    "to_be_sampled", "pending", "scheduled_sampling", "to_be_preserved",
    "registered"
  ],
  // waiting for somebody
  "state-due": ["sample_due", "attachment_due", "todo"],
  "state-unassigned": ["unassigned"],
  // in work
  "state-in-work": ["sample_received", "assigned", "open", "in_work"],
  // done, to be checked
  "state-to-be-verified": ["to_be_verified", "complete"],
  "state-verified": ["verified"],
  "state-published": ["published"],
  // left the workflow
  "state-retracted": ["retracted"],
  "state-invalid": ["invalid"],
  "state-rejected": ["rejected"],
  "state-cancelled": ["cancelled"]
};

const STATE_COLORS = Object.fromEntries(
  Object.entries(STATE_GROUPS).flatMap(([name, states]) =>
    states.map((state) => [state, token(name)])));

// Colors a tile may be given by name, e.g. the marker of a number tile
export const NAMED = {
  blue: token("cat-1"),
  orange: token("cat-2"),
  aqua: token("cat-3"),
  yellow: token("cat-4"),
  magenta: token("cat-5"),
  green: token("cat-6"),
  violet: token("cat-7"),
  red: token("cat-8"),
  slate: token("ink-2")
};

export const OTHER_KEYS = ["__other__", "__none__"];

// A color by its name, or the color of a workflow state, so that a
// number of samples in a state is marked in the color of the state
export function namedColor(name) {
  return NAMED[name] || STATE_COLORS[name] || NAMED.slate;
}

// The color of a workflow state, by its meaning
export function stateColor(state) {
  return STATE_COLORS[state] || NEUTRAL;
}

function isOther(item) {
  return OTHER_KEYS.includes(item.key);
}

// Colors for the groups of a result, by their key. States by meaning,
// everything else by position, "Other" and "Not set" neutral.
export function groupColors(items, kind) {
  const colors = {};
  let slot = 0;
  for (const item of items) {
    if (isOther(item)) {
      colors[item.key] = NEUTRAL;
    } else if (kind === "state") {
      colors[item.key] = stateColor(item.key);
    } else {
      colors[item.key] = CATEGORICAL[slot] || NEUTRAL;
      slot += 1;
    }
  }
  return colors;
}
