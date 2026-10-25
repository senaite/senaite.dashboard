// Colors of the data. Validated for color vision deficiencies in the
// order they are used; see the README.
//
// Workflow states keep one color everywhere, by meaning: waiting,
// in work, to verify, verified, published. Other groupings use the
// categorical slots in fixed order. Whatever does not fit is "Other"
// in a neutral gray.

const YELLOW = "#eda100";
const BLUE = "#2a78d6";
const ORANGE = "#eb6834";
const AQUA = "#1baf7a";
const GREEN = "#008300";
const VIOLET = "#6250d6";
const MAGENTA = "#e87ba4";
const RED = "#e34948";
export const NEUTRAL = "#a8a7a0";
const SLATE = "#5b6b7c";

const CATEGORICAL = [
  BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED
];

const STATE_COLORS = {
  // before the laboratory has the sample, or an order not taken on
  to_be_sampled: VIOLET,
  pending: VIOLET,
  scheduled_sampling: VIOLET,
  to_be_preserved: VIOLET,
  registered: VIOLET,
  // waiting for somebody
  sample_due: YELLOW,
  unassigned: YELLOW,
  attachment_due: YELLOW,
  todo: YELLOW,
  // in work
  sample_received: BLUE,
  assigned: BLUE,
  open: BLUE,
  in_work: BLUE,
  // done, to be checked
  to_be_verified: ORANGE,
  complete: ORANGE,
  // checked
  verified: AQUA,
  // out of the door
  published: GREEN,
  // left the workflow
  rejected: NEUTRAL,
  invalid: NEUTRAL,
  retracted: NEUTRAL,
  cancelled: NEUTRAL
};

// Colors a tile may be given by name, e.g. the cap of a number tile
export const NAMED = {
  yellow: YELLOW,
  blue: BLUE,
  orange: ORANGE,
  aqua: AQUA,
  green: GREEN,
  violet: VIOLET,
  magenta: MAGENTA,
  red: RED,
  slate: SLATE
};

export const OTHER_KEYS = ["__other__", "__none__"];

export function namedColor(name) {
  return NAMED[name] || SLATE;
}

// The color of a workflow state, by its meaning
export function stateColor(state) {
  return STATE_COLORS[state] || NEUTRAL;
}

// Colors for the groups of a result, by their key. States by meaning,
// everything else by position, "Other" and "Not set" neutral.
export function groupColors(items, kind) {
  const colors = {};
  let slot = 0;
  for (const item of items) {
    if (OTHER_KEYS.includes(item.key)) {
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
