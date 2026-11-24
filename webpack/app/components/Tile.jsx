import React, {useCallback, useEffect, useRef, useState} from "react";

import Icon from "./Icon";
import {DrillHead, DrillLevel} from "./Drill";
import TileBoundary from "./TileBoundary";
import useSize from "../hooks/useSize";
import {namedColor, stateColor} from "../colors";
import {t, titleText} from "../i18n";
import {getTileType} from "../tiles/registry";
import {resolveUrl} from "../urls";

// The sources whose tiles open to the objects behind their numbers
const DRILLABLE = ["count", "group", "timeseries"];

// A tile that waits longer than this says so
const SLOW_MS = 4000;

// The placeholders of a tile while it waits, in the shape of what
// comes: a number, bars or rows
const SKELETONS = {
  kpi: {className: "is-kpi", widths: [null]},
  bar: {className: "is-bars", widths: [100, 85, 60, 45, 30]},
  donut: {className: "is-bars", widths: [100, 70, 45]},
  chart: {className: "is-bars", widths: [100, 90, 75, 55]}
};
const ROWS = {className: "", widths: [92, 85, 88, 70]};

const ARROWS = {
  ArrowLeft: [-1, 0],
  ArrowRight: [1, 0],
  ArrowUp: [0, -1],
  ArrowDown: [0, 1]
};

function isEmpty(data) {
  if (data.items) {
    return !data.items.length;
  }
  if (data.rows) {
    return !data.rows.length;
  }
  if (data.series) {
    return !data.series.some((serie) => serie.values.some(Boolean));
  }
  return false;
}

// Where the title leads: the tile's own link, else the listing of its
// dataset
function resolveLink(tile, context) {
  if (tile.options.link) {
    return resolveUrl(tile.options.link, context.portalUrl);
  }
  const dataset = context.datasets[tile.params.dataset];
  return dataset ? dataset.listing : null;
}

function useSlow() {
  const [slow, setSlow] = useState(false);
  useEffect(() => {
    const timer = setTimeout(() => setSlow(true), SLOW_MS);
    return () => clearTimeout(timer);
  }, []);
  return slow;
}

function Skeleton({type}) {
  const slow = useSlow();
  const shape = SKELETONS[type] || ROWS;
  return (
    <div className={"sd-skeleton " + shape.className} aria-busy="true">
      {shape.widths.map((width, index) => (
        <span key={index} style={width ? {width: `${width}%`} : null}/>
      ))}
      {slow ? (
        <p className="sd-slow">{t("slow_tile")}</p>
      ) : null}
    </div>
  );
}

function Body({tile, data, pending, size, context, listing, onPick}) {
  const type = getTileType(tile.type);
  if (!type) {
    return <p className="sd-empty">{tile.type}</p>;
  }
  if (tile.source && !data) {
    return <Skeleton type={tile.type}/>;
  }
  if (data && data.error) {
    return (
      <p className="sd-tile-error">
        <Icon name="alert" size={16}/> {data.error}
      </p>
    );
  }
  if (data && isEmpty(data)) {
    return <p className="sd-empty">{t("no_data")}</p>;
  }
  const Component = type.component;
  return (
    <div className={"sd-tile-content" + (pending ? " is-pending" : "")}>
      <Component tile={tile} data={data || {}} size={size}
                 portalUrl={context.portalUrl} listing={listing}
                 onPick={onPick}/>
    </div>
  );
}

// Arrow keys move the tile by one cell, with Shift they resize it
function onKey(event, tile, onNudge) {
  const step = ARROWS[event.key];
  if (!step) {
    return;
  }
  event.preventDefault();
  const [dx, dy] = step;
  onNudge(tile.id, event.shiftKey ? {w: dx, h: dy} : {x: dx, y: dy});
}

// Bring a tile that was just added into view, and mark it for a moment
function useSpotlight(active) {
  const ref = useRef(null);
  useEffect(() => {
    if (active && ref.current) {
      ref.current.scrollIntoView({behavior: "smooth", block: "center"});
    }
  }, [active]);
  return ref;
}

// The levels a tile was opened to, like a navigation stack: a part of
// the tile first, then objects opened from its rows
function useDrill(tile, context, editing, onOpenChange) {
  const [stack, setStack] = useState([]);
  const forward = useRef(true);
  const open = stack.length > 0;

  useEffect(() => {
    if (editing) {
      setStack([]);
    }
  }, [editing]);

  useEffect(() => {
    if (onOpenChange) {
      onOpenChange(tile.id, open);
    }
  }, [open]);  // eslint-disable-line react-hooks/exhaustive-deps

  const push = useCallback((level) => {
    forward.current = true;
    setStack((prev) => prev.concat({scope: {}, ...level}));
  }, []);

  const canPick = !editing && DRILLABLE.includes(tile.source);
  // A part without a title of its own, e.g. the number of a count, is
  // all objects of the dataset the tile counts
  const dataset = context.datasets[tile.params.dataset];
  const fallback = dataset ? dataset.title : "";
  const pick = useCallback((part, title, color) => push({
    title: title || fallback, color,
    request: {tile: {source: tile.source, params: tile.params}, pick: part}
  }), [push, tile.source, tile.params, fallback]);

  const actions = {
    // A row of a level opens its object
    openRow: (row) => push({
      title: row.title,
      color: row.state ? stateColor(row.state) : null,
      request: {object: {dataset: row.dataset, uid: row.uid}}
    }),
    back: () => {
      forward.current = false;
      setStack((prev) => prev.slice(0, -1));
    },
    setScope: (name, value) => setStack((prev) => {
      const top = prev[prev.length - 1];
      return prev.slice(0, -1).concat(
        {...top, scope: {...top.scope, [name]: value}});
    }),
    // What the server answered, for the head of the tile. A row may
    // open another object than its own, e.g. an analysis its sample;
    // the level is named after what it shows.
    keepAnswer: (depth, answer) => setStack((prev) => prev.map(
      (level, index) => (index === depth - 1 ? named(level, answer)
        : level)))
  };
  return {stack, forward: forward.current, pick: canPick ? pick : null,
          actions};
}

function named(level, answer) {
  const object = answer.object;
  if (!object) {
    return {...level, answer};
  }
  return {...level, answer, title: object.title,
          color: object.state ? stateColor(object.state) : level.color};
}

// Esc and the way back take the focus along
function useDrillFocus(articleRef, depth) {
  useEffect(() => {
    if (depth && articleRef.current) {
      const back = articleRef.current.querySelector(".sd-drill-back");
      if (back) {
        back.focus({preventScroll: true});
      }
    }
  }, [articleRef, depth]);
}

function DrillBody({stack, forward, context, actions}) {
  const depth = stack.length;
  const level = stack[depth - 1];
  return (
    <div key={depth}
         className={"sd-drill " + (forward ? "is-forward" : "is-back")}>
      <DrillLevel api={context.api} level={level}
                  onScope={actions.setScope} onOpen={actions.openRow}
                  onAnswer={(answer) => actions.keepAnswer(depth, answer)}/>
    </div>
  );
}

// The head of a tile at rest: its title, and its tools while editing
function TileHead({tile, title, link, editing, props}) {
  const marker = tile.type === "kpi" && tile.options.color
    ? namedColor(tile.options.color) : null;
  return (
    <header className="sd-tile-head">
      {editing ? (
        <button type="button" className="sd-tile-grip"
                title={t("keyboard_hint")}
                aria-label={`${title}: ${t("keyboard_hint")}`}
                onKeyDown={(event) => onKey(event, tile, props.onNudge)}>
          <Icon name="grip" size={16}/>
        </button>
      ) : null}
      {marker ? (
        <span className="sd-marker" aria-hidden="true"
              style={{"--sd-marker": marker}}/>
      ) : null}
      <h3 className="sd-tile-title">
        {link ? <a href={link}>{title}</a> : title}
      </h3>
      {editing ? (
        <div className="sd-tile-tools">
          <button type="button" className="sd-iconbtn"
                  onClick={() => props.onSettings(tile.id)}
                  title={t("tile_settings")}
                  aria-label={t("tile_settings")}>
            <Icon name="sliders" size={16}/>
          </button>
          <button type="button" className="sd-iconbtn is-danger"
                  onClick={() => props.onRemove(tile.id)}
                  title={t("hide")} aria-label={t("hide")}>
            <Icon name="close" size={16}/>
          </button>
        </div>
      ) : null}
    </header>
  );
}

export default function Tile(props) {
  const {tile, editing, context, spotlight} = props;
  const [ref, size] = useSize();
  const articleRef = useSpotlight(spotlight);
  const drill = useDrill(tile, context, editing, props.onOpenChange);
  const depth = drill.stack.length;
  useDrillFocus(articleRef, depth);
  const title = titleText(tile.title);
  const link = editing ? null : resolveLink(tile, context);
  const onKeyDown = (event) => {
    if (event.key === "Escape" && depth) {
      event.stopPropagation();
      drill.actions.back();
    }
  };
  return (
    <article ref={articleRef}
             className={`sd-tile sd-tile-${tile.type}` +
                        (editing ? " is-editing" : "") +
                        (depth ? " is-drilled" : "") +
                        (spotlight ? " is-spotlight" : "")}
             aria-label={title} onKeyDown={onKeyDown}>
      {depth ? (
        <header className="sd-tile-head">
          <DrillHead stack={drill.stack} tileTitle={title}
                     onBack={drill.actions.back}/>
        </header>
      ) : (
        <TileHead tile={tile} title={title} link={link} editing={editing}
                  props={props}/>
      )}
      <div className="sd-tile-body" ref={ref}>
        {depth ? (
          <DrillBody stack={drill.stack} forward={drill.forward}
                     context={context} actions={drill.actions}/>
        ) : null}
        {!depth && size.width ? (
          <TileBoundary tile={tile} data={props.data}>
            <Body {...props} size={size} listing={link}
                  onPick={drill.pick}/>
          </TileBoundary>
        ) : null}
      </div>
    </article>
  );
}
