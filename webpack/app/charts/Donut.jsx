import React, {useState} from "react";
import {arc, pie} from "d3-shape";

import {groupColors} from "../colors";
import {formatNumber, formatPercent} from "../format";
import {t} from "../i18n";

// Parts of a whole. The legend names every part with its number, so
// no part depends on its color alone.
export default function Donut({items, kind, width, height}) {
  const [active, setActive] = useState(null);
  const colors = groupColors(items, kind);
  const total = items.reduce((sum, item) => sum + item.value, 0);
  const side = width > height * 1.6;
  const size = Math.max(80, Math.min(
    side ? height : height * 0.55, side ? width * 0.45 : width));
  const radius = size / 2;
  const slices = pie().sort(null).value((item) => item.value)
    .padAngle(items.length > 1 ? 0.02 : 0)(items);
  const shape = arc().innerRadius(radius * 0.62).outerRadius(radius)
    .cornerRadius(2);
  const focus = items.find((item) => item.key === active);
  // The hole holds the number; in a small ring only the number fits
  const hole = radius * 0.62 * 2;
  const centerStyle = {fontSize: Math.max(13, Math.min(24, hole * 0.28))};

  return (
    <div className={"sd-donut" + (side ? " is-side" : "")}
         onMouseLeave={() => setActive(null)}>
      <div className="sd-donut-figure" style={{width: size, height: size}}>
        <svg width={size} height={size} role="img"
             aria-label={items.map((item) =>
               `${item.label} ${item.value}`).join(", ")}>
          <g transform={`translate(${radius},${radius})`}>
            {slices.map((slice) => (
              <path key={slice.data.key} d={shape(slice)}
                    fill={colors[slice.data.key]}
                    opacity={active && active !== slice.data.key ? 0.3 : 1}
                    onMouseEnter={() => setActive(slice.data.key)}/>
            ))}
          </g>
        </svg>
        <div className="sd-donut-center">
          <span className="sd-donut-value" style={centerStyle}>
            {formatNumber(focus ? focus.value : total)}
          </span>
          {hole >= 90 ? (
            <span className="sd-donut-label">
              {focus ? focus.label : t("total")}
            </span>
          ) : null}
        </div>
      </div>
      <ul className="sd-legend is-list">
        {items.map((item) => (
          <li key={item.key}
              className={active === item.key ? "is-active" : ""}
              onMouseEnter={() => setActive(item.key)}>
            <span className="sd-swatch"
                  style={{background: colors[item.key]}}/>
            <span className="sd-legend-label">{item.label}</span>
            <span className="sd-legend-value">
              {formatNumber(item.value)}
            </span>
            <span className="sd-legend-share">
              {total ? formatPercent(item.value / total) : ""}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
