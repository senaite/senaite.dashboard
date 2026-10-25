import React, {useEffect, useRef} from "react";

import Icon from "./Icon";
import TileBoundary from "./TileBoundary";
import useSize from "../hooks/useSize";
import {namedColor} from "../colors";
import {t, titleText} from "../i18n";
import {getTileType} from "../tiles/registry";
import {resolveUrl} from "../urls";

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

function Skeleton() {
  return (
    <div className="sd-skeleton" aria-busy="true">
      <span/><span/><span/>
    </div>
  );
}

function Body({tile, data, pending, size, context, listing}) {
  const type = getTileType(tile.type);
  if (!type) {
    return <p className="sd-empty">{tile.type}</p>;
  }
  if (tile.source && !data) {
    return <Skeleton/>;
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
                 portalUrl={context.portalUrl} listing={listing}/>
    </div>
  );
}

const ARROWS = {
  ArrowLeft: [-1, 0],
  ArrowRight: [1, 0],
  ArrowUp: [0, -1],
  ArrowDown: [0, 1]
};

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

export default function Tile(props) {
  const {tile, editing, onSettings, onRemove, context, spotlight} = props;
  const [ref, size] = useSize();
  const articleRef = useSpotlight(spotlight);
  const title = titleText(tile.title);
  const link = editing ? null : resolveLink(tile, context);
  const cap = tile.type === "kpi" && tile.options.color
    ? namedColor(tile.options.color) : null;
  return (
    <article ref={articleRef}
             className={`sd-tile sd-tile-${tile.type}` +
                        (editing ? " is-editing" : "") +
                        (spotlight ? " is-spotlight" : "") +
                        (cap ? " has-cap" : "")}
             style={cap ? {"--sd-cap": cap} : null}
             aria-label={title}>
      <header className="sd-tile-head">
        {editing ? (
          <button type="button" className="sd-tile-grip"
                  title={t("keyboard_hint")}
                  aria-label={`${title}: ${t("keyboard_hint")}`}
                  onKeyDown={(event) => onKey(event, tile, props.onNudge)}>
            <Icon name="grip" size={16}/>
          </button>
        ) : null}
        <h3 className="sd-tile-title">
          {link ? <a href={link}>{title}</a> : title}
        </h3>
        {editing ? (
          <div className="sd-tile-tools">
            <button type="button" className="sd-iconbtn"
                    onClick={() => onSettings(tile.id)}
                    title={t("tile_settings")}
                    aria-label={t("tile_settings")}>
              <Icon name="sliders" size={16}/>
            </button>
            <button type="button" className="sd-iconbtn is-danger"
                    onClick={() => onRemove(tile.id)}
                    title={t("hide")} aria-label={t("hide")}>
              <Icon name="close" size={16}/>
            </button>
          </div>
        ) : null}
      </header>
      <div className="sd-tile-body" ref={ref}>
        {size.width ? (
          <TileBoundary tile={tile} data={props.data}>
            <Body {...props} size={size} listing={link}/>
          </TileBoundary>
        ) : null}
      </div>
    </article>
  );
}
