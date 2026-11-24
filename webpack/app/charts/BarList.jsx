import React from "react";

import {ACCENT, NEUTRAL, OTHER_KEYS} from "../colors";
import {formatNumber, formatPercent} from "../format";

function BarRow({item, max}) {
  const other = OTHER_KEYS.includes(item.key);
  return (
    <>
      <span className="sd-barlist-label">{item.label}</span>
      <span className="sd-barlist-track">
        <span className="sd-barlist-bar" style={{
          width: `${(item.value / max) * 100}%`,
          background: other ? NEUTRAL : ACCENT
        }}/>
      </span>
      <span className="sd-barlist-value">
        {formatNumber(item.value)}
      </span>
    </>
  );
}

// One measure across categories: horizontal bars in one color, the
// value at the tip. "Other" is gray. With `onPick` a bar opens to its
// objects.
export default function BarList({items, total, onPick}) {
  const max = Math.max(1, ...items.map((item) => item.value));
  return (
    <ul className="sd-barlist">
      {items.map((item) => {
        const share = total ? item.value / total : 0;
        const tip = `${item.label}: ${formatNumber(item.value)} ` +
          `(${formatPercent(share)})`;
        return (
          <li key={item.key} title={tip}
              className={"sd-barlist-row" + (onPick ? " is-pickable" : "")}>
            {onPick ? (
              <button type="button" onClick={() => onPick(item, null)}>
                <BarRow item={item} max={max}/>
              </button>
            ) : <BarRow item={item} max={max}/>}
          </li>
        );
      })}
    </ul>
  );
}
