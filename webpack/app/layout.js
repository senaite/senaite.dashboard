// Where tiles sit on the grid. Pure functions: tiles in, tiles out.

import {cloneLayout, moveElement, verticalCompactor} from
  "react-grid-layout/core";

export const COLUMNS = 12;
// The server keeps no taller tiles than this
const MAX_HEIGHT = 24;

// The smallest a tile gets; a number needs less room than a chart
function minSize(tile) {
  return tile.type === "kpi" ? {w: 2, h: 2} : {w: 3, h: 2};
}

export function toItem(tile) {
  const min = minSize(tile);
  return {i: tile.id, ...tile.layout, minW: min.w, minH: min.h,
          maxH: MAX_HEIGHT};
}

export function inReadingOrder(tiles) {
  return tiles.slice().sort((a, b) =>
    a.layout.y - b.layout.y || a.layout.x - b.layout.x);
}

function sameLayout(a, b) {
  return a.x === b.x && a.y === b.y && a.w === b.w && a.h === b.h;
}

// Apply grid items to the tiles; null when nothing moved
export function applyLayout(tiles, items) {
  const byId = {};
  items.forEach((item) => { byId[item.i] = item; });
  let moved = false;
  const next = tiles.map((tile) => {
    const item = byId[tile.id];
    if (!item) {
      return tile;
    }
    const layout = {x: item.x, y: item.y, w: item.w, h: item.h};
    if (sameLayout(tile.layout, layout)) {
      return tile;
    }
    moved = true;
    return {...tile, layout};
  });
  return moved ? next : null;
}

// Close the gaps and resolve overlaps the way the grid does
export function settle(tiles) {
  const items = verticalCompactor.compact(tiles.map(toItem), COLUMNS);
  return applyLayout(tiles, items) || tiles;
}

// The tile of the same size the dragged tile was dropped onto, if any
function swapTarget(tiles, oldItem, newItem) {
  return tiles.find((tile) => {
    const {x, y, w, h} = tile.layout;
    return tile.id !== newItem.i && w === oldItem.w && h === oldItem.h &&
      Math.abs(x - newItem.x) <= w / 2 && Math.abs(y - newItem.y) <= h / 2;
  });
}

function place(tile, x, y) {
  return {...tile, layout: {...tile.layout, x, y}};
}

// After a drag: tiles of the same size trade places; anything else
// makes room the way the grid does, by moving the others down
export function dropTile(tiles, items, oldItem, newItem) {
  const target = swapTarget(tiles, oldItem, newItem);
  if (!target) {
    return applyLayout(tiles, items);
  }
  return settle(tiles.map((tile) => {
    if (tile.id === newItem.i) {
      return place(tile, target.layout.x, target.layout.y);
    }
    return tile.id === target.id ? place(tile, oldItem.x, oldItem.y) : tile;
  }));
}

function clamp(value, low, high) {
  return Math.max(low, Math.min(high, value));
}

// A step from the keyboard: {x, y} moves the tile, {w, h} resizes it
export function nudgeTile(tiles, tileId, step) {
  const tile = tiles.find((item) => item.id === tileId);
  const items = cloneLayout(tiles.map(toItem));
  const item = items.find((entry) => entry.i === tileId);
  const min = minSize(tile);
  if (step.w || step.h) {
    item.w = clamp(item.w + (step.w || 0), min.w, COLUMNS - item.x);
    item.h = clamp(item.h + (step.h || 0), min.h, MAX_HEIGHT);
    return settle(applyLayout(tiles, items) || tiles);
  }
  const x = clamp(item.x + (step.x || 0), 0, COLUMNS - item.w);
  const y = Math.max(0, item.y + (step.y || 0));
  const moved = moveElement(items, item, x, y, true, false, "vertical",
                            COLUMNS);
  return settle(applyLayout(tiles, moved) || tiles);
}

function overlaps(a, b) {
  return a.x < b.x + b.w && b.x < a.x + a.w &&
    a.y < b.y + b.h && b.y < a.y + a.h;
}

// Where a new tile of the size goes: the first free place in reading
// order, so it fills a gap before it goes below everything else
export function findFreePlace(tiles, w, h) {
  const taken = tiles.map((tile) => tile.layout);
  const bottom = taken.reduce((max, l) => Math.max(max, l.y + l.h), 0);
  for (let y = 0; y <= bottom; y += 1) {
    for (let x = 0; x + w <= COLUMNS; x += 1) {
      const spot = {x, y, w, h};
      if (!taken.some((layout) => overlaps(layout, spot))) {
        return spot;
      }
    }
  }
  return {x: 0, y: bottom, w, h};
}
