import React from "react";

import {stateColor} from "../colors";
import {formatDate, formatNumber, formatPercent,
        formatRelative} from "../format";
import {format, t} from "../i18n";

function DateCell({value, column}) {
  if (!value) {
    return <span className="sd-muted">–</span>;
  }
  // A due date is read against today, any other date as a date
  if (column.kind === "due") {
    const late = new Date(value) < new Date();
    return (
      <time dateTime={value} title={formatDate(value)}
            className={late ? "sd-late" : ""}>
        {formatRelative(value)}
      </time>
    );
  }
  return <time dateTime={value}>{formatDate(value)}</time>;
}

function StateCell({value}) {
  if (!value) {
    return null;
  }
  return (
    <span className="sd-state"
          style={{"--sd-state-color": stateColor(value.value)}}>
      {value.title}
    </span>
  );
}

// A percentage from 0 to 100 as a bar
function ProgressCell({value}) {
  const percent = value || 0;
  const text = formatPercent(percent / 100);
  return (
    <span className="sd-progress" role="progressbar"
          aria-valuenow={percent} aria-valuemin={0} aria-valuemax={100}
          aria-valuetext={text} title={text}>
      <span style={{width: `${percent}%`}}/>
    </span>
  );
}

function Cell({value, column}) {
  switch (column.kind) {
    case "date":
    case "due":
      return <DateCell value={value} column={column}/>;
    case "state":
      return <StateCell value={value}/>;
    case "percent":
      return <ProgressCell value={value}/>;
    case "number":
      return formatNumber(value);
    default:
      return value === null || value === undefined ? "" : String(value);
  }
}

export default function TableTile({data, listing}) {
  return (
    <div className="sd-table-wrap">
      <table className="sd-table">
        <thead>
          <tr>
            {data.columns.map((column) => (
              <th key={column.name} scope="col"
                  className={`is-${column.kind}`}>{column.title}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.rows.map((row) => (
            <tr key={row.uid}>
              {data.columns.map((column, index) => {
                const cell = (
                  <Cell value={row.cells[column.name]} column={column}/>
                );
                // The first cell leads to the object
                return (
                  <td key={column.name} className={`is-${column.kind}`}>
                    {index === 0 ? <a href={row.url}>{cell}</a> : cell}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      {data.total > data.rows.length ? (
        <div className="sd-table-foot">
          {format("of_total", {shown: formatNumber(data.rows.length),
                               total: formatNumber(data.total)})}
          {listing ? <a href={listing}>{t("open_list")}</a> : null}
        </div>
      ) : null}
    </div>
  );
}
