import React, {useState} from "react";
import {scaleBand, scaleLinear} from "d3-scale";
import {area, curveMonotoneX, line} from "d3-shape";

import Tooltip, {TooltipRow} from "./Tooltip";
import {ACCENT, AXIS, GRID, MUTED, SURFACE} from "./theme";
import {groupColors} from "../colors";
import {formatNumber, formatPeriod} from "../format";
import {t} from "../i18n";

const MARGIN = {top: 8, right: 8, bottom: 24};
// Width per character of a value label, and the room next to it
const LABEL_CHAR_WIDTH = 7;
const LABEL_GAP = 12;
const MAX_BAR = 24;
const GAP = 2;
const LABEL_SPACE = 56;
// Vertical room per tick label of the value axis
const TICK_SPACE = 28;

// The room the value labels need on the left, so that none is cut
function leftMargin(ticks) {
  const longest = Math.max(1, ...ticks.map(
    (tick) => formatNumber(tick).length));
  return LABEL_GAP + longest * LABEL_CHAR_WIDTH;
}

function stackSeries(series, count) {
  const base = new Array(count).fill(0);
  return series.map((serie) => {
    const lows = base.slice();
    serie.values.forEach((value, index) => { base[index] += value; });
    return {...serie, lows, highs: base.slice()};
  });
}

// A column whose top corners are rounded, growing from the baseline
function columnPath(x, y, width, height, radius) {
  const r = Math.min(radius, width / 2, height);
  return `M${x},${y + height}V${y + r}Q${x},${y} ${x + r},${y}` +
    `H${x + width - r}Q${x + width},${y} ${x + width},${y + r}` +
    `V${y + height}Z`;
}

function Axis({ticks, scale, width}) {
  return (
    <g className="sd-axis">
      {ticks.map((tick) => (
        <g key={tick} transform={`translate(0,${scale(tick)})`}>
          <line x1={0} x2={width} style={{stroke: tick ? GRID : AXIS}}/>
          <text x={-8} dy="0.32em" textAnchor="end" style={{fill: MUTED}}>
            {formatNumber(tick)}
          </text>
        </g>
      ))}
    </g>
  );
}

function Columns({stacked, x, y, colors, active, onPart}) {
  const band = x.bandwidth();
  const width = Math.min(MAX_BAR, band * 0.72);
  const offset = (band - width) / 2;
  return stacked.map((serie, layer) => (
    <g key={serie.key} style={{fill: colors[serie.key]}}>
      {serie.values.map((value, index) => {
        if (!value) {
          return null;
        }
        const top = y(serie.highs[index]);
        const isTop = !stacked.slice(layer + 1).some(
          (above) => above.values[index]);
        const height = Math.max(
          1, y(serie.lows[index]) - top - (serie.lows[index] ? GAP : 0));
        return (
          <path key={index}
                d={columnPath(x(index) + offset, top, width, height,
                              isTop ? 4 : 0)}
                className={onPart ? "is-pickable" : null}
                onClick={onPart ? (event) => {
                  event.stopPropagation();
                  onPart(index, serie);
                } : undefined}
                opacity={active === null || active === index ? 1 : 0.45}/>
        );
      })}
    </g>
  ));
}

function Lines({stacked, series, x, y, colors, style}) {
  const center = (index) => x(index) + x.bandwidth() / 2;
  const source = style === "area" ? stacked : series;
  return source.map((serie) => {
    const top = (value, index) =>
      y(style === "area" ? serie.highs[index] : value);
    const path = line().curve(curveMonotoneX)
      .x((value, index) => center(index)).y(top)(serie.values);
    const fill = style === "area" ? area().curve(curveMonotoneX)
      .x((value, index) => center(index))
      .y0((value, index) => y(serie.lows[index]))
      .y1(top)(serie.values) : null;
    return (
      <g key={serie.key}>
        {fill ? <path d={fill} style={{fill: colors[serie.key]}}
                      opacity={series.length > 1 ? 0.22 : 0.12}/> : null}
        <path d={path} fill="none" style={{stroke: colors[serie.key]}}
              strokeWidth={2} strokeLinejoin="round"
              strokeLinecap="round"/>
      </g>
    );
  });
}

function Markers({stacked, series, x, y, colors, style, index}) {
  if (index === null) {
    return null;
  }
  const source = style === "area" ? stacked : series;
  const cx = x(index) + x.bandwidth() / 2;
  return source.map((serie) => (
    <circle key={serie.key} cx={cx} r={4} strokeWidth={2}
            style={{fill: colors[serie.key], stroke: SURFACE}}
            cy={y(style === "area" ? serie.highs[index]
                  : serie.values[index])}/>
  ));
}

function XLabels({buckets, x, interval, height, every}) {
  return buckets.map((bucket, index) => {
    if ((buckets.length - 1 - index) % every) {
      return null;
    }
    return (
      <text key={bucket} className="sd-axis" x={x(index) + x.bandwidth() / 2}
            y={height + 16} textAnchor="middle" style={{fill: MUTED}}>
        {formatPeriod(bucket, interval)}
      </text>
    );
  });
}

function Legend({series, colors}) {
  if (series.length < 2) {
    return null;
  }
  return (
    <ul className="sd-legend is-row">
      {series.map((serie) => (
        <li key={serie.key}>
          <span className="sd-swatch"
                style={{background: colors[serie.key]}}/>
          <span className="sd-legend-label">{serie.label}</span>
        </li>
      ))}
    </ul>
  );
}

// What a click on a period, or a part of a column, opens: its period
// and, in a stack, its value
function partOf(data, index, serie, colors) {
  const {buckets, series, interval} = data;
  const period = formatPeriod(buckets[index], interval, true);
  if (!serie || series.length < 2) {
    return [{bucket: buckets[index]}, period, null];
  }
  return [{bucket: buckets[index], key: serie.key},
          `${period} · ${serie.label}`, colors[serie.key]];
}

// Counts per period: stacked columns, stacked areas or lines. With
// `onPick` a column, a part of it or a period of a line opens to its
// objects.
export default function TimeChart({data, style, width, height, onPick}) {
  const [active, setActive] = useState(null);
  const {buckets, series, interval, kind} = data;
  const colors = series.length > 1 ? groupColors(series, kind)
    : {[series[0].key]: ACCENT};
  const innerHeight = Math.max(10, height - MARGIN.top - MARGIN.bottom);
  const stacked = stackSeries(series, buckets.length);
  const totals = stacked.length ? stacked[stacked.length - 1].highs : [];
  const peak = style === "line"
    ? Math.max(1, ...series.flatMap((serie) => serie.values))
    : Math.max(1, ...totals);
  const tickCount = Math.max(1, Math.min(4,
    Math.floor(innerHeight / TICK_SPACE)));
  const y = scaleLinear().domain([0, peak]).nice(tickCount)
    .range([innerHeight, 0]);
  const ticks = y.ticks(tickCount);
  const left = leftMargin(ticks);
  const innerWidth = Math.max(10, width - left - MARGIN.right);
  const x = scaleBand().domain(buckets.map((b, index) => index))
    .range([0, innerWidth]).paddingInner(0.12).paddingOuter(0.04);
  const every = Math.max(1, Math.ceil(
    buckets.length * LABEL_SPACE / innerWidth));

  const onMove = (event) => {
    const box = event.currentTarget.getBoundingClientRect();
    const position = event.clientX - box.left - left;
    const index = Math.floor(position / (innerWidth / buckets.length));
    setActive(index >= 0 && index < buckets.length ? index : null);
  };
  const tip = active === null ? null : {
    x: left + x(active) + x.bandwidth() / 2,
    y: MARGIN.top
  };
  const props = {stacked, series, x, y, colors, style};
  const onPart = onPick
    ? (index, serie) => onPick(...partOf(data, index, serie, colors))
    : null;
  const onPeriod = onPick ? () => {
    if (active !== null) {
      onPart(active, null);
    }
  } : undefined;

  return (
    <div className="sd-timechart">
      <div className="sd-timechart-plot">
        <svg width={width} height={height} onMouseMove={onMove}
             onMouseLeave={() => setActive(null)} onClick={onPeriod}
             className={onPick ? "is-pickable" : null} role="img"
             aria-label={series.map((serie) => serie.label).join(", ")}>
          <g transform={`translate(${left},${MARGIN.top})`}>
            <Axis ticks={ticks} scale={y} width={innerWidth}/>
            {active !== null ? (
              <rect x={x(active) - 2} width={x.bandwidth() + 4}
                    y={0} height={innerHeight} className="sd-hoverband"/>
            ) : null}
            {style === "bars"
              ? <Columns {...props} active={active} onPart={onPart}/>
              : <Lines {...props}/>}
            {style !== "bars"
              ? <Markers {...props} index={active}/> : null}
            <XLabels buckets={buckets} x={x} interval={interval}
                     height={innerHeight} every={every}/>
          </g>
        </svg>
        {tip ? (
          <Tooltip x={tip.x} y={tip.y} width={width}>
            <div className="sd-tooltip-title">
              {formatPeriod(buckets[active], interval, true)}
            </div>
            {series.slice().reverse().filter((serie) =>
              serie.values[active]).map((serie) => (
              <TooltipRow key={serie.key} color={colors[serie.key]}
                          label={serie.label}
                          value={formatNumber(serie.values[active])}/>
            ))}
            {series.length > 1 ? (
              <TooltipRow strong label={t("total")}
                          value={formatNumber(totals[active])}/>
            ) : null}
          </Tooltip>
        ) : null}
      </div>
      <Legend series={series} colors={colors}/>
    </div>
  );
}
