// The shape of a tile on the client. Tiles from the server are complete;
// tiles from add-on presets may not be.

export function normalizeTile(tile) {
  return {
    source: null,
    ...tile,
    params: tile.params || {},
    options: tile.options || {},
    layout: {x: 0, y: 0, w: 4, h: 3, ...tile.layout}
  };
}

// Eight hex digits, the length of the ids the server makes
export function newTileId() {
  const bytes = crypto.getRandomValues(new Uint8Array(4));
  return Array.from(bytes, (byte) =>
    byte.toString(16).padStart(2, "0")).join("");
}
