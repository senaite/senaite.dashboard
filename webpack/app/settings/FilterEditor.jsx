import React, {useEffect, useState} from "react";

import Icon from "../components/Icon";
import {loadChoices} from "./choices";
import {Select} from "./controls";
import {t} from "../i18n";

// Date filters a user picks from, instead of writing placeholders
const DATE_PRESETS = [
  ["last_7d", {min: "$today-7d"}],
  ["last_30d", {min: "$today-30d"}],
  ["last_90d", {min: "$today-90d"}],
  ["last_365d", {min: "$today-365d"}],
  ["this_week", {min: "$week"}],
  ["this_month", {min: "$month"}],
  ["this_year", {min: "$year"}],
  ["before_now", {max: "$now"}],
  ["after_now", {min: "$now"}]
];

// Placeholders a value filter offers next to the stored values
function specialChoices(field) {
  if (field.kind === "user") {
    return [{value: "$user", title: t("me")}];
  }
  if (field.name === "getClientUID") {
    return [{value: "$client", title: t("my_client")}];
  }
  return [];
}

function toList(value) {
  if (value === null || value === undefined || value === "") {
    return [];
  }
  return Array.isArray(value) ? value : [value];
}

function defaultValue(field) {
  if (field.kind === "date") {
    return {min: "$today-30d"};
  }
  if (field.kind === "boolean") {
    return true;
  }
  return [];
}

function DateFilter({value, onChange, label}) {
  const current = DATE_PRESETS.find(([key, preset]) =>
    JSON.stringify(preset) === JSON.stringify(value));
  const options = DATE_PRESETS.map(([key]) => ({value: key, title: t(key)}));
  if (!current) {
    options.push({value: "custom", title: t("custom")});
  }
  return (
    <Select label={label} value={current ? current[0] : "custom"}
            options={options}
            onChange={(key) => {
              const preset = DATE_PRESETS.find(([name]) => name === key);
              if (preset) {
                onChange(preset[1]);
              }
            }}/>
  );
}

function BooleanFilter({value, onChange, label}) {
  return (
    <Select label={label} value={value ? "yes" : "no"}
            options={[{value: "yes", title: t("yes")},
                      {value: "no", title: t("no")}]}
            onChange={(key) => onChange(key === "yes")}/>
  );
}

// Values chosen from a list, shown as removable chips
function ValuesFilter({api, dataset, field, value, onChange, label}) {
  const [choices, setChoices] = useState(specialChoices(field));
  const [failed, setFailed] = useState(null);
  useEffect(() => {
    let alive = true;
    setChoices(specialChoices(field));
    setFailed(null);
    loadChoices(api, dataset, field.name).then((loaded) => {
      if (alive) {
        setChoices(specialChoices(field).concat(loaded));
      }
    }).catch((error) => alive && setFailed(error.message));
    return () => { alive = false; };
  }, [api, dataset, field]);

  const selected = toList(value);
  const titleOf = (item) => {
    const choice = choices.find((option) => option.value === item);
    return choice ? choice.title : item;
  };
  const rest = choices.filter((option) => !selected.includes(option.value));
  return (
    <div className="sd-values">
      {selected.map((item) => (
        <span key={item} className="sd-chip is-value">
          {titleOf(item)}
          <button type="button" aria-label={`${t("delete")} ${titleOf(item)}`}
                  onClick={() => onChange(
                    selected.filter((other) => other !== item))}>
            <Icon name="close" size={12}/>
          </button>
        </span>
      ))}
      {rest.length ? (
        <Select label={label} value="" options={rest}
                allowEmpty={selected.length ? t("or") : t("value_any")}
                onChange={(item) => item && onChange(selected.concat(item))}/>
      ) : null}
      {selected.includes("$client") ? (
        <span className="sd-field-hint">{t("my_client_hint")}</span>
      ) : null}
      {failed ? <span className="sd-field-hint is-error">{failed}</span>
        : null}
    </div>
  );
}

function FilterRow({api, dataset, field, value, onChange, onRemove}) {
  const props = {value, onChange, label: field.title};
  let editor;
  if (field.kind === "date") {
    editor = <DateFilter {...props}/>;
  } else if (field.kind === "boolean") {
    editor = <BooleanFilter {...props}/>;
  } else {
    editor = <ValuesFilter {...props} api={api} dataset={dataset}
                           field={field}/>;
  }
  return (
    <div className="sd-filter">
      <div className="sd-filter-head">
        <span className="sd-field-label">{field.title}</span>
        <button type="button" className="sd-iconbtn is-small"
                aria-label={`${t("delete")} ${field.title}`}
                onClick={onRemove}>
          <Icon name="close" size={14}/>
        </button>
      </div>
      {editor}
    </div>
  );
}

// The filters of a tile, one row per field
export default function FilterEditor({api, dataset, filters, onChange}) {
  const fields = dataset.fields;
  const used = Object.keys(filters || {});
  const unused = fields.filter((field) => !used.includes(field.name));
  const set = (name, value) => onChange({...filters, [name]: value});
  const remove = (name) => {
    const next = {...filters};
    delete next[name];
    onChange(next);
  };
  return (
    <div className="sd-filters">
      {used.map((name) => {
        const field = fields.find((item) => item.name === name);
        if (!field) {
          return null;
        }
        return (
          <FilterRow key={name} api={api} dataset={dataset.name}
                     field={field} value={filters[name]}
                     onChange={(value) => set(name, value)}
                     onRemove={() => remove(name)}/>
        );
      })}
      {unused.length ? (
        <Select label={t("add_filter")} value=""
                allowEmpty={`+ ${t("add_filter")}`}
                options={unused.map((field) => ({
                  value: field.name, title: field.title}))}
                onChange={(name) => {
                  const field = fields.find((item) => item.name === name);
                  if (field) {
                    set(name, defaultValue(field));
                  }
                }}/>
      ) : null}
    </div>
  );
}
