import React, {useRef, useState} from "react";

import Alert from "../components/Alert";
import {ConfirmDialog} from "../components/Dialogs";
import Icon from "../components/Icon";
import Toast from "../components/Toast";
import DatasetEditor from "./DatasetEditor";
import {emptyDraft, toDefinition, toDraft} from "./draft";
import {formatNumber} from "../format";
import {t, titleText} from "../i18n";

function DatasetList({datasets, active, onOpen, onNew}) {
  return (
    <nav className="sd-ds-list" aria-label={t("datasets")}>
      <button type="button" className="sd-btn is-primary" onClick={onNew}>
        <Icon name="plus" size={16}/> {t("new_dataset")}
      </button>
      <ul>
        {datasets.map((dataset) => (
          <li key={dataset.name}>
            <button type="button" className="sd-ds-item"
                    aria-current={dataset.name === active ? "true"
                      : undefined}
                    onClick={() => onOpen(dataset)}>
              <strong>{titleText(dataset.title)}</strong>
              <span>{dataset.portal_type}</span>
            </button>
          </li>
        ))}
      </ul>
      {!datasets.length ? (
        <p className="sd-hint">{t("no_datasets")}</p>
      ) : null}
    </nav>
  );
}

// What deleting a dataset takes along, e.g. "Used by 2 global
// dashboards and 1 tile of the library. Their tiles ..."
function usageText(usage) {
  if (!usage.dashboards && !usage.library) {
    return t("dataset_unused");
  }
  const used = t("dataset_usage")
    .replace("{dashboards}", formatNumber(usage.dashboards))
    .replace("{library}", formatNumber(usage.library));
  return `${used} ${t("delete_dataset_confirm")}`;
}

// The page where managers define datasets of their own. What they
// save is offered on the dashboard once it is loaded again.
export default function DatasetsApp({api, boot}) {
  const [datasets, setDatasets] = useState(boot.datasets);
  const [draft, setDraft] = useState(null);
  const [inspection, setInspection] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState(null);
  const [removing, setRemoving] = useState(null);
  // The number of the latest draft asked for; an answer for an earlier
  // one comes too late and is dropped
  const latest = useRef(0);

  const run = async (action) => {
    setError(null);
    try {
      return await action();
    } catch (exc) {
      setError(exc.message || String(exc));
      return null;
    }
  };

  // The draft of a definition, or of a new dataset of a type. The
  // draft and the inspection change together: the editor shows the
  // fields of the one with the entries of the other.
  const load = (portalType, definition, title) => run(async () => {
    const seq = (latest.current += 1);
    setLoading(true);
    setInspection(null);
    try {
      const answer = await api.inspectType(portalType);
      if (seq !== latest.current) {
        return;
      }
      const next = toDraft(answer, definition);
      setDraft(title === undefined ? next : {...next, title});
      setInspection(answer);
    } finally {
      if (seq === latest.current) {
        setLoading(false);
      }
    }
  });

  const startNew = () => {
    latest.current += 1;
    setLoading(false);
    setInspection(null);
    setDraft(emptyDraft());
  };

  // What was typed while the save was on its way stays; a new dataset
  // takes the name the server gave it
  const save = () => run(async () => {
    const sent = draft;
    const answer = await api.saveDataset(toDefinition(sent));
    setDatasets(answer.datasets);
    setDraft((current) => current && current.name === sent.name &&
      current.portal_type === sent.portal_type
      ? {...current, name: answer.saved} : current);
    setNotice("dataset_saved");
  });

  const askRemove = () => run(async () => {
    const usage = await api.datasetUsage(draft.name);
    setRemoving(usage);
  });

  const remove = () => run(async () => {
    const answer = await api.removeDataset(draft.name);
    setDatasets(answer.datasets);
    setRemoving(null);
    setDraft(null);
    setInspection(null);
    setNotice("dataset_removed");
  });

  return (
    <div className="sd-app sd-ds">
      <header className="sd-ds-head">
        <div>
          <h1 className="sd-hello">{t("datasets")}</h1>
          <p className="sd-today">{t("datasets_hint")}</p>
        </div>
        <a className="sd-btn" href={boot.dashboard_url}>
          <Icon name="layout" size={16}/> {t("back_to_dashboard")}
        </a>
      </header>

      <Alert message={error} onClose={() => setError(null)}/>

      <div className="sd-ds-body">
        <DatasetList datasets={datasets} active={draft && draft.name}
                     onNew={startNew}
                     onOpen={(dataset) => load(dataset.portal_type,
                                               dataset)}/>
        <main className="sd-ds-main">
          {draft ? (
            <>
              <DatasetEditor draft={draft} inspection={inspection}
                             types={boot.types} setDraft={setDraft}
                             onType={(portalType) => portalType &&
                               load(portalType, null, draft.title)}/>
              {loading ? <p className="sd-hint">{t("loading")}</p> : null}
              <footer className="sd-ds-foot">
                {inspection ? (
                  <span className="sd-hint">
                    {formatNumber(inspection.count)} {t("objects_visible")}
                  </span>
                ) : null}
                {draft.name ? (
                  <button type="button" className="sd-btn is-danger"
                          onClick={askRemove}>
                    <Icon name="trash" size={16}/> {t("delete")}
                  </button>
                ) : null}
                <button type="button" className="sd-btn is-primary"
                        disabled={!inspection} onClick={save}>
                  <Icon name="check" size={16}/> {t("save")}
                </button>
              </footer>
            </>
          ) : (
            <p className="sd-ds-empty">{t("pick_dataset")}</p>
          )}
        </main>
      </div>

      {removing ? (
        <ConfirmDialog title={t("delete_dataset")} label={t("delete")}
                       text={usageText(removing)}
                       onClose={() => setRemoving(null)}
                       onConfirm={remove}/>
      ) : null}
      <Toast message={notice} onClose={() => setNotice(null)}/>
    </div>
  );
}
