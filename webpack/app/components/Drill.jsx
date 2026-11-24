import React, {useEffect, useState} from "react";

import Icon from "./Icon";
import {stateColor} from "../colors";
import {formatDate, formatNumber, formatPercent,
        formatRelative} from "../format";
import {format, t} from "../i18n";

// The objects behind a number of a tile, shown in the tile itself. A
// level of the stack is what the server is asked for: a part of the
// tile ({tile, pick}) or an object opened in it ({object}).

function isLate(iso) {
  return Boolean(iso) && new Date(iso) < new Date();
}

// One value of a row as text, by the kind of its column
function Slot({slot}) {
  if (!slot || slot.value === null || slot.value === undefined ||
      slot.value === "") {
    return null;
  }
  const {kind, value} = slot;
  switch (kind) {
    case "due":
      return (
        <time dateTime={value} title={formatDate(value)}
              className={isLate(value) ? "sd-late" : ""}>
          {formatRelative(value)}
        </time>
      );
    case "date":
      return <time dateTime={value}>{formatDate(value)}</time>;
    case "state":
      return value.title;
    case "percent":
      return formatPercent(value / 100);
    case "number":
      return formatNumber(value);
    default:
      return String(value);
  }
}

function hasValue(slot) {
  return slot && slot.value !== null && slot.value !== undefined &&
    slot.value !== "";
}

// The slots of a line joined by a dot
function Joined({slots}) {
  const shown = slots.filter(hasValue);
  return shown.map((slot, index) => (
    <React.Fragment key={index}>
      {index ? " · " : null}
      <Slot slot={slot}/>
    </React.Fragment>
  ));
}

function Row({row, onOpen}) {
  const detail = row.detail.find(hasValue);
  const content = (
    <>
      <span className="sd-dot" aria-hidden="true"
            style={{background: stateColor(row.state)}}/>
      <span className="sd-row-main">
        <span className="sd-row-title">{row.title}</span>
        <span className="sd-row-sub"><Joined slots={row.subtitle}/></span>
      </span>
      <span className="sd-row-side">
        <span><Slot slot={detail}/></span>
        <span className="sd-row-sub"><Slot slot={row.note}/></span>
      </span>
    </>
  );
  return (
    <li className="sd-row">
      {row.opens ? (
        <button type="button" className="sd-row-open"
                onClick={() => onOpen(row)}>
          {content}
          <Icon name="forward" size={14}/>
        </button>
      ) : (
        <div className="sd-row-open is-static">{content}</div>
      )}
      <a className="sd-row-link" href={row.url} title={t("open_object")}
         aria-label={`${row.title}: ${t("open_object")}`}>
        <Icon name="external" size={14}/>
      </a>
    </li>
  );
}

function Facets({facets, scope, onScope}) {
  if (!facets.length) {
    return null;
  }
  return (
    <div className="sd-facets">
      {facets.map((facet) => (
        <div key={facet.name} className="sd-facet" role="group"
             aria-label={facet.title}>
          {facet.values.map((value) => {
            const picked = scope[facet.name] === value.key;
            return (
              <button key={value.key} type="button" aria-pressed={picked}
                      onClick={() => onScope(facet.name,
                                             picked ? null : value.key)}>
                {value.label}
                <span className="sd-facet-count">
                  {formatNumber(value.count)}
                </span>
              </button>
            );
          })}
        </div>
      ))}
    </div>
  );
}

function Facts({object}) {
  const facts = object.facts.filter(hasValue);
  if (!facts.length) {
    return null;
  }
  return (
    <dl className="sd-facts">
      {facts.map((fact) => (
        <div key={fact.title}>
          <dt>{fact.title}</dt>
          <dd><Slot slot={fact}/></dd>
        </div>
      ))}
    </dl>
  );
}

// The rows of a level; more come with the last row
function Rows({answer, more, loadingMore, onMore, onOpen}) {
  const rows = answer.rows.concat(more);
  const left = answer.total - rows.length;
  return (
    <ul className="sd-rows">
      {rows.map((row) => (
        <Row key={row.uid} row={row} onOpen={onOpen}/>
      ))}
      {left > 0 ? (
        <li className="sd-row is-more">
          <button type="button" className="sd-row-open"
                  disabled={loadingMore} onClick={onMore}>
            <span>{format("show_more", {count: formatNumber(
              Math.min(left, answer.rows.length))})}</span>
          </button>
        </li>
      ) : null}
      {answer.listing && !answer.object ? (
        <li className="sd-row is-more">
          <a className="sd-row-open" href={answer.listing}>
            <span>{t("open_list")}</span>
            <Icon name="forward" size={14}/>
          </a>
        </li>
      ) : null}
    </ul>
  );
}

function useLevel(api, level, scope) {
  const [state, setState] = useState({answer: null, error: null});
  const request = JSON.stringify({...level.request, scope});
  useEffect(() => {
    let current = true;
    setState((prev) => ({answer: prev.answer, error: null}));
    api.drill(JSON.parse(request)).then(
      (answer) => current && setState({answer, error: null}),
      (exc) => current && setState({answer: null, error: exc.message}));
    return () => { current = false; };
  }, [api, request]);
  return state;
}

// One level of the stack: its facets, the object opened and its rows
export function DrillLevel({api, level, onScope, onOpen, onAnswer}) {
  const scope = level.scope || {};
  const {answer, error} = useLevel(api, level, scope);
  const [more, setMore] = useState([]);
  const [loadingMore, setLoadingMore] = useState(false);

  useEffect(() => {
    setMore([]);
    if (answer) {
      onAnswer(answer);
    }
  }, [answer]);  // eslint-disable-line react-hooks/exhaustive-deps

  const loadMore = async () => {
    setLoadingMore(true);
    try {
      const next = await api.drill({
        ...level.request, scope,
        offset: answer.rows.length + more.length
      });
      setMore((prev) => prev.concat(next.rows));
    } finally {
      setLoadingMore(false);
    }
  };

  if (error) {
    return (
      <p className="sd-tile-error">
        <Icon name="alert" size={16}/> {error}
      </p>
    );
  }
  if (!answer) {
    return (
      <div className="sd-skeleton" aria-busy="true">
        {[92, 85, 88, 70].map((width) => (
          <span key={width} style={{width: `${width}%`}}/>
        ))}
      </div>
    );
  }
  return (
    <div className="sd-drill-level">
      {answer.object ? <Facts object={answer.object}/> : null}
      {answer.section ? (
        <h4 className="sd-drill-section">{answer.section}</h4>
      ) : null}
      <Facets facets={answer.facets || []} scope={scope}
              onScope={onScope}/>
      {answer.rows ? (
        answer.total ? (
          <Rows answer={answer} more={more} loadingMore={loadingMore}
                onMore={loadMore} onOpen={onOpen}/>
        ) : <p className="sd-empty">{t("no_data")}</p>
      ) : null}
    </div>
  );
}

// The head of an opened tile: the way back, what is shown and the
// page of SENAITE it stands for
export function DrillHead({stack, tileTitle, onBack}) {
  const top = stack[stack.length - 1];
  const previous = stack.length > 1
    ? stack[stack.length - 2].title : tileTitle;
  const link = top.answer && (top.answer.object
    ? top.answer.object.url : top.answer.listing);
  const total = top.answer && top.answer.rows ? top.answer.total : null;
  return (
    <>
      <button type="button" className="sd-drill-back" onClick={onBack}
              aria-label={format("back_to", {title: previous})}>
        <Icon name="back" size={16}/>
        <span>{previous}</span>
      </button>
      <h3 className="sd-tile-title sd-drill-title">
        {top.color ? (
          <span className="sd-marker" aria-hidden="true"
                style={{"--sd-marker": top.color}}/>
        ) : null}
        <span className="sd-drill-name">{top.title}</span>
        {total !== null && !top.answer.object ? (
          <span className="sd-drill-count">{formatNumber(total)}</span>
        ) : null}
      </h3>
      {link ? (
        <a className="sd-iconbtn" href={link} title={t("open_object")}
           aria-label={t("open_object")}>
          <Icon name="external" size={16}/>
        </a>
      ) : null}
    </>
  );
}
