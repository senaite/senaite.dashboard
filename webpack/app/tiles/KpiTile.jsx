import React from "react";

import Sparkline from "../charts/Sparkline";
import {namedColor} from "../colors";
import {formatDuration, formatNumber} from "../format";
import {t} from "../i18n";

function Fact({label, children}) {
  return <div><dt>{label}</dt><dd>{children}</dd></div>;
}

function durationText(hours) {
  const duration = formatDuration(hours);
  return `${duration.value} ${duration.unit}`;
}

// How long something takes: the average, with the median, the 90th
// percentile and how many objects it was measured on
function Duration({data}) {
  const value = formatDuration(data.value);
  return (
    <div className="sd-kpi">
      <div className="sd-kpi-value">
        {value.value}<span className="sd-kpi-unit">{value.unit}</span>
      </div>
      {data.count ? (
        <dl className="sd-kpi-facts">
          <Fact label={t("median")}>{durationText(data.median)}</Fact>
          <Fact label={t("p90")}>{durationText(data.p90)}</Fact>
          <Fact label={t("measured")}>{formatNumber(data.count)}</Fact>
        </dl>
      ) : null}
    </div>
  );
}

// One number, with its course over the last periods when there is one
export default function KpiTile({tile, data}) {
  if (data.unit === "hours") {
    return <Duration data={data}/>;
  }
  const color = namedColor(tile.options.color);
  return (
    <div className="sd-kpi">
      <div className="sd-kpi-value">{formatNumber(data.value)}</div>
      <Sparkline trend={data.trend} color={color}/>
    </div>
  );
}
