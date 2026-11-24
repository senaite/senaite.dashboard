import React, {useCallback, useState} from "react";
import ReactGridLayout, {
  useContainerWidth, verticalCompactor
} from "react-grid-layout";

import Tile from "./Tile";
import {COLUMNS, applyLayout, dropTile, inReadingOrder,
        toItem} from "../layout";

const ROW_HEIGHT = 64;
const MARGIN = [16, 16];
// Below this width the tiles stack in reading order
const STACK_BELOW = 720;
// An opened tile is at least this many rows high, so that its rows fit
const OPEN_ROWS = 6;

// The tile as the grid places it: an opened tile grows for the time it
// is open. The grow is not saved; only a drag or a resize is.
function placed(tile, open) {
  if (!open || tile.layout.h >= OPEN_ROWS) {
    return toItem(tile);
  }
  return {...toItem(tile), h: OPEN_ROWS};
}

// Which tiles are opened to the objects behind their numbers
function useOpenTiles() {
  const [open, setOpen] = useState({});
  const onOpenChange = useCallback((tileId, isOpen) => {
    setOpen((prev) => (Boolean(prev[tileId]) === isOpen ? prev
      : {...prev, [tileId]: isOpen}));
  }, []);
  return [open, onOpenChange];
}

function Stack({tiles, renderTile, open}) {
  return (
    <div className="sd-stack">
      {inReadingOrder(tiles).map((tile) => (
        <div key={tile.id}
             className={`sd-stack-item is-h${tile.layout.h}` +
                        (tile.type === "kpi" ? " is-half" : "") +
                        (open[tile.id] ? " is-open" : "")}>
          {renderTile(tile)}
        </div>
      ))}
    </div>
  );
}

export default function Grid(props) {
  const {tiles, editing, onTilesChange} = props;
  const {width, containerRef, mounted} = useContainerWidth();
  const [open, onOpenChange] = useOpenTiles();

  const renderTile = (tile) => (
    <Tile tile={tile} data={props.results[tile.id]}
          pending={props.pending[tile.id]} editing={editing}
          onSettings={props.onSettings} onRemove={props.onRemove}
          onNudge={props.onNudge} context={props.context}
          spotlight={props.spotlight === tile.id}
          onOpenChange={onOpenChange}/>
  );

  // Only what the user did counts; the grid also reports the layout
  // when it merely tidies up on mount
  const commit = (next) => {
    if (next) {
      onTilesChange(next);
    }
  };
  const onDragStop = (items, oldItem, newItem) =>
    commit(dropTile(tiles, items, oldItem, newItem));
  const onResizeStop = (items) => commit(applyLayout(tiles, items));

  return (
    <div ref={containerRef} className="sd-grid">
      {mounted && width < STACK_BELOW ? (
        <Stack tiles={tiles} renderTile={renderTile} open={open}/>
      ) : null}
      {mounted && width >= STACK_BELOW ? (
        <ReactGridLayout
          width={width}
          layout={tiles.map((tile) => placed(tile, open[tile.id]))}
          gridConfig={{cols: COLUMNS, rowHeight: ROW_HEIGHT,
                       margin: MARGIN, containerPadding: [0, 0]}}
          dragConfig={{enabled: editing, handle: ".sd-tile-head",
                       cancel: ".sd-tile-tools, a, input"}}
          resizeConfig={{enabled: editing, handles: ["se"]}}
          compactor={verticalCompactor}
          onDragStop={onDragStop}
          onResizeStop={onResizeStop}>
          {tiles.map((tile) => (
            <div key={tile.id} className="sd-cell">
              {renderTile(tile)}
            </div>
          ))}
        </ReactGridLayout>
      ) : null}
    </div>
  );
}
