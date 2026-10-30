import React from "react";

import Icon from "../components/Icon";
import {Field, Section, Select, TextInput} from "../settings/controls";
import {spanDates} from "./draft";
import {t, titleText, withTitle} from "../i18n";

// Kinds a column may show its values as
const COLUMN_KINDS = ["text", "date", "number", "state"];

function kindOptions(kinds) {
  return kinds.map((kind) => ({value: kind, title: t(`kind_${kind}`)}));
}

function typeOptions(types) {
  return types.map((type) => ({value: type.portal_type, title: type.title}));
}

function Samples({values}) {
  if (!values.length) {
    return <span className="sd-muted">–</span>;
  }
  return <span className="sd-ds-samples">{values.join(", ")}</span>;
}

function TitleInput({title, label, onChange}) {
  return (
    <TextInput label={label} value={titleText(title)}
               onChange={(text) => onChange(withTitle(title, text))}/>
  );
}

// One index of the catalog: whether it is a field, and as what
function FieldRow({offered, entry, types, onChange}) {
  const set = (change) => onChange({...entry, ...change});
  return (
    <tr className={entry.use ? "is-used" : ""}>
      <td>
        <input type="checkbox" checked={entry.use}
               aria-label={`${t("use")} ${offered.index}`}
               onChange={() => set({use: !entry.use})}/>
      </td>
      <th scope="row"><code>{offered.index}</code></th>
      <td>
        <TitleInput title={entry.title}
                    label={`${t("dashboard_title")} ${offered.index}`}
                    onChange={(title) => set({title})}/>
      </td>
      <td>
        <Select label={`${t("kind")} ${offered.index}`} value={entry.kind}
                options={kindOptions(offered.kinds)}
                onChange={(kind) => set({kind})}/>
      </td>
      <td>
        {entry.kind === "reference" ? (
          <Select label={`${t("points_to")} ${offered.index}`}
                  value={entry.portal_type}
                  allowEmpty="–" options={types}
                  onChange={(portalType) => set({portal_type: portalType})}/>
        ) : null}
      </td>
      <td>
        <input type="checkbox" checked={entry.lab_only}
               aria-label={`${t("lab_only")} ${offered.index}`}
               onChange={() => set({lab_only: !entry.lab_only})}/>
      </td>
      <td><Samples values={offered.samples}/></td>
    </tr>
  );
}

// One metadata column: whether a table may show it, and as what
function ColumnRow({offered, entry, onChange}) {
  const set = (change) => onChange({...entry, ...change});
  return (
    <tr className={entry.use ? "is-used" : ""}>
      <td>
        <input type="checkbox" checked={entry.use}
               aria-label={`${t("use")} ${offered.name}`}
               onChange={() => set({use: !entry.use})}/>
      </td>
      <th scope="row"><code>{offered.name}</code></th>
      <td>
        <TitleInput title={entry.title}
                    label={`${t("dashboard_title")} ${offered.name}`}
                    onChange={(title) => set({title})}/>
      </td>
      <td>
        <Select label={`${t("kind")} ${offered.name}`} value={entry.kind}
                options={kindOptions(COLUMN_KINDS)}
                onChange={(kind) => set({kind})}/>
      </td>
      <td>
        <input type="checkbox" checked={entry.lab_only}
               aria-label={`${t("lab_only")} ${offered.name}`}
               onChange={() => set({lab_only: !entry.lab_only})}/>
      </td>
      <td><Samples values={offered.samples}/></td>
    </tr>
  );
}

function FieldsSection({draft, inspection, setDraft}) {
  const types = typeOptions(inspection.candidates);
  const setField = (index, entry) => setDraft({
    ...draft, fields: {...draft.fields, [index]: entry}});
  return (
    <Section title={t("dataset_fields")}>
      <p className="sd-hint">{t("dataset_fields_hint")}</p>
      <div className="sd-ds-tablewrap">
        <table className="sd-ds-table">
          <thead>
            <tr>
              <th scope="col"><span className="sd-sr">{t("use")}</span></th>
              <th scope="col">{t("index")}</th>
              <th scope="col">{t("dashboard_title")}</th>
              <th scope="col">{t("kind")}</th>
              <th scope="col">{t("points_to")}</th>
              <th scope="col">{t("lab_only")}</th>
              <th scope="col">{t("examples")}</th>
            </tr>
          </thead>
          <tbody>
            {inspection.fields.map((offered) => (
              <FieldRow key={offered.index} offered={offered}
                        entry={draft.fields[offered.index]} types={types}
                        onChange={(entry) => setField(offered.index,
                                                      entry)}/>
            ))}
          </tbody>
        </table>
      </div>
    </Section>
  );
}

function ColumnsSection({draft, inspection, setDraft}) {
  const setColumn = (name, entry) => setDraft({
    ...draft, columns: {...draft.columns, [name]: entry}});
  return (
    <Section title={t("dataset_columns")}>
      <p className="sd-hint">{t("dataset_columns_hint")}</p>
      <div className="sd-ds-tablewrap">
        <table className="sd-ds-table">
          <thead>
            <tr>
              <th scope="col"><span className="sd-sr">{t("use")}</span></th>
              <th scope="col">{t("column")}</th>
              <th scope="col">{t("dashboard_title")}</th>
              <th scope="col">{t("kind")}</th>
              <th scope="col">{t("lab_only")}</th>
              <th scope="col">{t("examples")}</th>
            </tr>
          </thead>
          <tbody>
            {inspection.columns.map((offered) => (
              <ColumnRow key={offered.name} offered={offered}
                         entry={draft.columns[offered.name]}
                         onChange={(entry) => setColumn(offered.name,
                                                        entry)}/>
            ))}
          </tbody>
        </table>
      </div>
    </Section>
  );
}

function SpansSection({draft, inspection, setDraft}) {
  const {starts, ends} = spanDates(inspection);
  const dateOptions = (names) => names.map((name) => ({
    value: name,
    title: titleText((draft.columns[name] || {}).title) || name
  }));
  const setSpans = (spans) => setDraft({...draft, spans});
  const setSpan = (index, change) => setSpans(draft.spans.map(
    (span, position) => position === index ? {...span, ...change} : span));
  if (!ends.length) {
    return null;
  }
  return (
    <Section title={t("dataset_spans")}>
      <p className="sd-hint">{t("dataset_spans_hint")}</p>
      {draft.spans.map((span, index) => (
        <div key={index} className="sd-ds-span">
          <TitleInput title={span.title} label={t("dashboard_title")}
                      onChange={(title) => setSpan(index, {title})}/>
          <Select label={t("span_from")} value={span.start} allowEmpty="–"
                  options={dateOptions(starts)}
                  onChange={(start) => setSpan(index, {start})}/>
          <Select label={t("span_to")} value={span.end} allowEmpty="–"
                  options={dateOptions(ends)}
                  onChange={(end) => setSpan(index, {end})}/>
          <button type="button" className="sd-iconbtn is-small"
                  aria-label={t("delete")}
                  onClick={() => setSpans(draft.spans.filter(
                    (other, position) => position !== index))}>
            <Icon name="close" size={14}/>
          </button>
        </div>
      ))}
      <button type="button" className="sd-btn is-small"
              onClick={() => setSpans(draft.spans.concat(
                {title: "", start: null, end: null}))}>
        <Icon name="plus" size={16}/> {t("add_span")}
      </button>
    </Section>
  );
}

// Everything about one dataset: what it is made of, what tiles may
// filter and group by, what tables may show
export default function DatasetEditor({draft, inspection, types, setDraft,
                                       onType}) {
  return (
    <>
      <Section title={t("dataset_general")}>
        <Field label={t("dashboard_title")}>
          <TitleInput title={draft.title} label={t("dashboard_title")}
                      onChange={(title) => setDraft({...draft, title})}/>
        </Field>
        <Field label={t("dataset_type")}
               hint={draft.name ? t("dataset_type_fixed") : null}>
          {draft.name ? (
            <span className="sd-ds-type">
              {inspection ? inspection.type.title : draft.portal_type}
            </span>
          ) : (
            <Select label={t("dataset_type")} value={draft.portal_type}
                    allowEmpty="–" options={typeOptions(types)}
                    onChange={onType}/>
          )}
        </Field>
        <label className="sd-check">
          <input type="checkbox" checked={draft.lab_only}
                 onChange={() => setDraft({
                   ...draft, lab_only: !draft.lab_only})}/>
          {t("dataset_lab_only")}
        </label>
        <p className="sd-ds-warning">
          <Icon name="alert" size={16}/> {t("dataset_warning")}
        </p>
      </Section>
      {inspection ? (
        <>
          <FieldsSection draft={draft} inspection={inspection}
                         setDraft={setDraft}/>
          <ColumnsSection draft={draft} inspection={inspection}
                          setDraft={setDraft}/>
          <SpansSection draft={draft} inspection={inspection}
                        setDraft={setDraft}/>
        </>
      ) : null}
    </>
  );
}
