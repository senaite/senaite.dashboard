import React from "react";

import TimeChart from "../charts/TimeChart";

// Room the legend takes below the plot
const LEGEND_HEIGHT = 30;

export default function ChartTile({tile, data, size}) {
  const legend = data.series.length > 1 ? LEGEND_HEIGHT : 0;
  return (
    <TimeChart data={data} style={tile.options.style || "bars"}
               width={size.width}
               height={Math.max(60, size.height - legend)}/>
  );
}
