import React, {useState} from "react";

import {formatBucket, formatNumber} from "../format";

// Columns of the last periods; the current one in the tile's color
export default function Sparkline({trend, color}) {
  const [active, setActive] = useState(null);
  if (!trend || !trend.values || !trend.values.length) {
    return null;
  }
  const values = trend.values;
  const max = Math.max(1, ...values);
  const last = values.length - 1;
  const shown = active === null ? last : active;
  return (
    <div className="sd-spark" onMouseLeave={() => setActive(null)}>
      <div className="sd-spark-bars" aria-hidden="true">
        {values.map((value, index) => (
          <span key={index}
                className={"sd-spark-bar" +
                           (index === shown ? " is-active" : "")}
                onMouseEnter={() => setActive(index)}
                style={{
                  height: `${Math.max(6, (value / max) * 100)}%`,
                  background: index === shown ? color : undefined
                }}/>
        ))}
      </div>
      <div className="sd-spark-caption">
        {formatBucket(trend.buckets[shown], trend.interval,
                      shown === last)}
        {": "}
        <strong>{formatNumber(values[shown])}</strong>
      </div>
    </div>
  );
}
