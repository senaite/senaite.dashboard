// How the parameters of a tile follow its dataset and its source.
// Pure functions: a tile in, parameters or a tile out.

import {typesFor} from "../tiles/registry";

// Datasets a source can work on; a duration needs spans
export function datasetsFor(sourceName, context) {
  return Object.values(context.datasets).filter((item) =>
    sourceName !== "span" || item.spans.length);
}

// Parameters that only make sense for one dataset
function forDataset(params, dataset) {
  const names = dataset.fields.map((field) => field.name);
  const filters = {};
  Object.entries(params.filters || {}).forEach(([name, value]) => {
    if (names.includes(name)) {
      filters[name] = value;
    }
  });
  const groupable = dataset.fields.filter((field) => field.groupable);
  return {
    ...params,
    dataset: dataset.name,
    filters,
    group_by: names.includes(params.group_by) ? params.group_by
      : (groupable[0] || {}).name,
    stack_by: names.includes(params.stack_by) ? params.stack_by : null,
    columns: (params.columns || []).filter((name) =>
      dataset.columns.some((column) => column.name === name)),
    span: dataset.spans.some((span) => span.name === params.span)
      ? params.span : (dataset.spans[0] || {}).name
  };
}

// Only the parameters the source takes
function pickParams(params, names) {
  const picked = {};
  names.forEach((name) => {
    if (params[name] !== undefined && params[name] !== null) {
      picked[name] = params[name];
    }
  });
  return picked;
}

// The parameters of the tile on another dataset, those its source
// takes only
export function paramsOnDataset(tile, dataset, context) {
  const source = context.sources[tile.source];
  return pickParams(forDataset(tile.params, dataset), source.params);
}

// The tile on another source: its dataset and filters stay where the
// source can take them, its type and size become the first that can
// show the output of the source
export function switchSource(tile, sourceName, context) {
  const source = context.sources[sourceName];
  const current = context.datasets[tile.params.dataset];
  const datasets = datasetsFor(sourceName, context);
  const dataset = datasets.includes(current) ? current : datasets[0];
  const type = typesFor(source.output)[0];
  return {
    ...tile,
    source: sourceName,
    type: type.name,
    params: pickParams(forDataset(tile.params, dataset), source.params),
    layout: {...tile.layout, ...type.size}
  };
}
