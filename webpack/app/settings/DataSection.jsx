import React from "react";

import FilterEditor from "./FilterEditor";
import SOURCE_FIELDS, {options} from "./SourceFields";
import {Field, Section, Segmented, Select} from "./controls";
import {datasetsFor, paramsOnDataset, switchSource} from "./params";
import {t} from "../i18n";
import {typesFor} from "../tiles/registry";

// What the tile shows: the kind of data, the dataset, the parameters
// of the source and the filters

function SourceField({tile, update, context}) {
  // Sources with a dataset to work on and a tile type to show them
  const kinds = Object.values(context.sources)
    .filter((source) => datasetsFor(source.name, context).length &&
            typesFor(source.output).length)
    .map((source) => ({value: source.name, title: source.title}));
  return (
    <Field label={t("source")} group>
      <Segmented label={t("source")} value={tile.source} options={kinds}
                 onChange={(name) => update(
                   switchSource(tile, name, context))}/>
    </Field>
  );
}

// The tile's dataset is gone, or the user may not use it: the tile
// can move to another one
function MissingDataset({tile, update, context}) {
  const datasets = datasetsFor(tile.source, context);
  return (
    <Section title={t("data")}>
      <SourceField tile={tile} update={update} context={context}/>
      <Field label={t("dataset")} hint={t("dataset_missing")}>
        <Select label={t("dataset")} options={options(datasets)} value=""
                allowEmpty="–"
                onChange={(name) => name && update({
                  params: paramsOnDataset(tile, context.datasets[name],
                                          context)})}/>
      </Field>
    </Section>
  );
}

export default function DataSection({tile, update, context}) {
  const params = tile.params;
  const dataset = context.datasets[params.dataset];
  // Notes, links and other tiles without data, and sources of add-ons
  // that work on no dataset, have nothing to set here
  const source = tile.source && context.sources[tile.source];
  if (!source || !source.params.includes("dataset")) {
    return null;
  }
  if (!dataset) {
    return <MissingDataset tile={tile} update={update} context={context}/>;
  }
  const dateFields = dataset.fields.filter((f) => f.kind === "date");
  const groupFields = dataset.fields.filter((f) => f.groupable);
  const SourceFields = SOURCE_FIELDS[tile.source];
  const setParam = (change) => update({params: {...params, ...change}});
  const datasets = datasetsFor(tile.source, context);
  return (
    <Section title={t("data")}>
      <SourceField tile={tile} update={update} context={context}/>
      <Field label={t("dataset")}>
        <Select label={t("dataset")} options={options(datasets)}
                value={dataset.name}
                onChange={(name) => update({
                  params: paramsOnDataset(tile, context.datasets[name],
                                          context)})}/>
      </Field>
      {SourceFields ? (
        <SourceFields params={params} setParam={setParam} dataset={dataset}
                      dateFields={dateFields} groupFields={groupFields}
                      limits={context.limits}
                      defaultTrend={context.defaultTrend}/>
      ) : null}
      <h4 className="sd-subtitle">{t("filters")}</h4>
      <FilterEditor api={context.api} dataset={dataset}
                    filters={params.filters || {}}
                    onChange={(filters) => setParam({filters})}/>
    </Section>
  );
}
