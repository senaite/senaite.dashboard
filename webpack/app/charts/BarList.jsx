import React from "react";

import {BLUE_ACCENT} from "./theme";
import {NEUTRAL, OTHER_KEYS} from "../colors";
import {formatNumber, formatPercent} from "../format";

// One measure across categories: horizontal bars in one color, the
// value at the tip. "Other" is gray.
export default function BarList({items, total}) {
  const max = Math.max(1, ...items.map((item) => item.value));
  return (
    <ul className="sd-barlist">
      {items.map((item) => {
        const other = OTHER_KEYS.includes(item.key);
        const share = total ? item.value / total : 0;
        return (
          <li key={item.key} className="sd-barlist-row"
              title={`${item.label}: ${formatNumber(item.value)} ` +
                     `(${formatPercent(share)})`}>
            <span className="sd-barlist-label">{item.label}</span>
            <span className="sd-barlist-track">
              <span className="sd-barlist-bar" style={{
                width: `${(item.value / max) * 100}%`,
                background: other ? NEUTRAL : BLUE_ACCENT
              }}/>
            </span>
            <span className="sd-barlist-value">
              {formatNumber(item.value)}
            </span>
          </li>
        );
      })}
    </ul>
  );
}
