import React from "react";

import {Field, NumberInput, Segmented, Select} from "./controls";
import {t} from "../i18n";

// The parameters each data source has, as fields of the panel. Each
// gets the parameters of the tile and `setParam` to change some of
// them.

const INTERVALS = ["day", "week", "month"];
// What a source takes when a tile does not say
const DEFAULT_PERIODS = 12;
const DEFAULT_LIMIT = 10;

export function options(items) {
  return items.map((item) => ({value: item.name, title: item.title}));
}

// How many entries a list or a grouping shows
function LimitField({params, setParam, max}) {
  return (
    <Field label={t("limit")}>
      <NumberInput label={t("limit")} value={params.limit || DEFAULT_LIMIT}
                   min={1} max={max}
                   onChange={(value) => setParam({limit: value})}/>
    </Field>
  );
}

function TimeFields({params, setParam, dateFields, limits}) {
  const interval = params.interval || "week";
  const periods = params.periods || DEFAULT_PERIODS;
  return (
    <>
      <Field label={t("interval")} group>
        <Segmented label={t("interval")} value={interval}
                   options={INTERVALS.map((value) => ({
                     value, title: t(`interval_${value}`)}))}
                   onChange={(value) => setParam({
                     interval: value,
                     periods: Math.min(periods, limits.periods[value])})}/>
      </Field>
      <Field label={t("periods")}>
        <NumberInput label={t("periods")} value={periods}
                     min={2} max={limits.periods[interval]}
                     onChange={(value) => setParam({periods: value})}/>
      </Field>
      <Field label={t("date_field")}>
        <Select label={t("date_field")} options={options(dateFields)}
                value={params.date_field || "created"}
                onChange={(value) => setParam({date_field: value})}/>
      </Field>
    </>
  );
}

function CountFields({params, setParam, dateFields, limits,
                      defaultTrend}) {
  const trend = params.trend;
  return (
    <>
      <Field label={t("trend")} group>
        <Segmented label={t("trend")} value={trend ? "on" : "off"}
                   options={[{value: "off", title: t("no")},
                             {value: "on", title: t("yes")}]}
                   onChange={(value) => setParam({
                     trend: value === "on" ? defaultTrend : null})}/>
      </Field>
      {trend ? (
        <TimeFields params={trend} dateFields={dateFields} limits={limits}
                    setParam={(change) => setParam({
                      trend: {...trend, ...change}})}/>
      ) : null}
    </>
  );
}

function GroupFields({params, setParam, groupFields, limits}) {
  return (
    <>
      <Field label={t("group_by")}>
        <Select label={t("group_by")} options={options(groupFields)}
                value={params.group_by}
                onChange={(value) => setParam({group_by: value})}/>
      </Field>
      <LimitField params={params} setParam={setParam} max={limits.groups}/>
    </>
  );
}

function SeriesFields({params, setParam, dateFields, groupFields,
                       limits}) {
  return (
    <>
      <TimeFields params={params} setParam={setParam}
                  dateFields={dateFields} limits={limits}/>
      <Field label={t("stack_by")}>
        <Select label={t("stack_by")} options={options(groupFields)}
                value={params.stack_by} allowEmpty={t("none")}
                onChange={(value) => setParam({stack_by: value})}/>
      </Field>
    </>
  );
}

function ListFields({params, setParam, dataset, dateFields, limits}) {
  const columns = params.columns || [];
  const toggle = (name) => setParam({
    columns: columns.includes(name)
      ? columns.filter((column) => column !== name)
      : dataset.columns.map((column) => column.name).filter(
        (column) => columns.includes(column) || column === name)
  });
  return (
    <>
      <Field label={t("columns")} group>
        <div className="sd-checks" role="group" aria-label={t("columns")}>
          {dataset.columns.map((column) => (
            <label key={column.name} className="sd-check">
              <input type="checkbox" checked={columns.includes(column.name)}
                     onChange={() => toggle(column.name)}/>
              {column.title}
            </label>
          ))}
        </div>
      </Field>
      <Field label={t("sort_on")}>
        <Select label={t("sort_on")} options={options(dateFields)}
                value={params.sort_on || "created"}
                onChange={(value) => setParam({sort_on: value})}/>
      </Field>
      <Segmented label={t("sort_on")}
                 value={params.sort_order || "descending"}
                 options={[{value: "descending", title: t("descending")},
                           {value: "ascending", title: t("ascending")}]}
                 onChange={(value) => setParam({sort_order: value})}/>
      <LimitField params={params} setParam={setParam} max={limits.rows}/>
    </>
  );
}

function SpanFields({params, setParam, dataset}) {
  return (
    <Field label={t("span")}>
      <Select label={t("span")} options={options(dataset.spans)}
              value={params.span}
              onChange={(value) => setParam({span: value})}/>
    </Field>
  );
}

// The fields of each source, by its name
export default {
  count: CountFields,
  group: GroupFields,
  timeseries: SeriesFields,
  list: ListFields,
  span: SpanFields
};
