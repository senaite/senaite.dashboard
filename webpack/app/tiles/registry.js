// Tile types: how a tile shows its data.
//
// An add-on adds its own with
//
//   window.senaite.dashboard.registerTileType("gauge", {
//     label: "Gauge", icon: "kpi", accepts: ["scalar"],
//     component: GaugeTile, size: {w: 3, h: 2}
//   });
//
// `accepts` names the outputs of data sources the type can show; a type
// without a data source accepts nothing and keeps its content in the
// tile options.

const TYPES = {};

export function registerTileType(name, spec) {
  TYPES[name] = {name, accepts: [], size: {w: 4, h: 3}, ...spec};
}

export function getTileType(name) {
  return TYPES[name] || null;
}

export function getTileTypes() {
  return Object.values(TYPES);
}

// Types that can show the output of a source
export function typesFor(output) {
  return getTileTypes().filter((type) => type.accepts.includes(output));
}
