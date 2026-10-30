// A dataset while a manager edits it, and the definition the server
// keeps. Pure functions: definitions and inspections in, drafts out.
//
// A draft holds every field and column the type offers, each marked
// whether it is used, so that unticking and ticking again keeps what
// was entered for it.

// A dataset of a type nobody has picked yet
export function emptyDraft() {
  return {name: null, title: "", portal_type: null, lab_only: true,
          fields: {}, columns: {}, spans: []};
}

function fieldEntry(offered, kept) {
  return {
    use: Boolean(kept),
    title: kept ? kept.title : offered.index,
    kind: kept ? kept.kind : offered.kind,
    portal_type: kept ? kept.portal_type : offered.portal_type,
    lab_only: kept ? kept.lab_only : true
  };
}

function columnEntry(offered, kept) {
  return {
    use: Boolean(kept),
    title: kept ? kept.title : offered.name,
    kind: kept ? kept.kind : offered.kind,
    // Lab-only unless opened, like a field; definitions kept before
    // columns had the flag are lab-only too
    lab_only: kept ? kept.lab_only !== false : true
  };
}

function byKey(items, key) {
  const map = {};
  (items || []).forEach((item) => { map[item[key]] = item; });
  return map;
}

// The draft of a definition, or of a new dataset of the inspected type
export function toDraft(inspection, definition) {
  const keptFields = byKey(definition && definition.fields, "index");
  const keptColumns = byKey(definition && definition.columns, "name");
  const fields = {};
  inspection.fields.forEach((offered) => {
    fields[offered.index] = fieldEntry(offered, keptFields[offered.index]);
  });
  const columns = {};
  inspection.columns.forEach((offered) => {
    columns[offered.name] = columnEntry(offered, keptColumns[offered.name]);
  });
  return {
    name: definition ? definition.name : null,
    title: definition ? definition.title : "",
    portal_type: inspection.type.portal_type,
    lab_only: definition ? definition.lab_only : true,
    fields,
    columns,
    spans: definition ? definition.spans.map((span) => ({...span})) : []
  };
}

// What the server keeps of a draft: the used fields and columns only
export function toDefinition(draft) {
  const used = (entries) => Object.entries(entries)
    .filter(([, entry]) => entry.use);
  return {
    name: draft.name,
    title: draft.title,
    portal_type: draft.portal_type,
    lab_only: draft.lab_only,
    fields: used(draft.fields).map(([index, entry]) => ({
      index, title: entry.title, kind: entry.kind,
      portal_type: entry.kind === "reference" ? entry.portal_type : null,
      lab_only: entry.lab_only
    })),
    columns: used(draft.columns).map(([name, entry]) => ({
      name, title: entry.title, kind: entry.kind, lab_only: entry.lab_only
    })),
    spans: draft.spans.filter((span) => span.start && span.end)
  };
}

// Dates a span may start from, and end at: the end must be an index,
// for the source sorts by it
export function spanDates(inspection) {
  const dates = inspection.columns
    .filter((column) => column.kind === "date")
    .map((column) => column.name);
  return {
    starts: dates,
    ends: dates.filter((name) => inspection.date_indexes.includes(name))
  };
}
