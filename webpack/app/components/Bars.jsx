import React from "react";

import Icon from "./Icon";
import {t} from "../i18n";

function SaveState({state}) {
  if (state === "idle") {
    return null;
  }
  return (
    <span className={`sd-savestate is-${state}`} role="status">
      {state === "saved" ? <Icon name="check" size={14}/> : null}
      {t(state === "error" ? "error" : state)}
    </span>
  );
}

// Shown while a user arranges a dashboard for themselves
export function EditBar({saveState, customized, onAdd, onReset, onDone}) {
  return (
    <div className="sd-bar is-edit">
      <p className="sd-bar-text">{t("edit_hint")}</p>
      <SaveState state={saveState}/>
      <div className="sd-bar-actions">
        {customized ? (
          <button type="button" className="sd-btn" onClick={onReset}>
            <Icon name="undo" size={16}/> {t("reset")}
          </button>
        ) : null}
        <button type="button" className="sd-btn" onClick={onAdd}>
          <Icon name="plus" size={16}/> {t("add_tile")}
        </button>
        <button type="button" className="sd-btn is-primary" onClick={onDone}>
          <Icon name="check" size={16}/> {t("done")}
        </button>
      </div>
    </div>
  );
}

// Shown to an administrator on a global dashboard whose draft has
// changes nobody else sees yet
export function PendingBar({onOpenDraft}) {
  return (
    <div className="sd-bar is-draft is-static">
      <p className="sd-bar-text">
        <strong>{t("draft")}</strong> {t("pending_hint")}
      </p>
      <div className="sd-bar-actions">
        <button type="button" className="sd-btn is-primary"
                onClick={onOpenDraft}>
          <Icon name="globe" size={16}/> {t("open_draft")}
        </button>
      </div>
    </div>
  );
}

// Shown while an administrator edits the draft of a global dashboard
export function DraftBar({view, saveState, onAdd, onPublish, onDiscard,
                          onLeave}) {
  return (
    <div className="sd-bar is-draft">
      <p className="sd-bar-text">
        <strong>{t("draft")}</strong> {t(view.published && !view.has_changes
          ? "draft_hint_published" : "draft_hint")}
      </p>
      <SaveState state={saveState}/>
      <div className="sd-bar-actions">
        <button type="button" className="sd-btn" onClick={onAdd}>
          <Icon name="plus" size={16}/> {t("add_tile")}
        </button>
        {view.published && view.has_changes ? (
          <button type="button" className="sd-btn" onClick={onDiscard}>
            <Icon name="undo" size={16}/> {t("discard_draft")}
          </button>
        ) : null}
        <button type="button" className="sd-btn" onClick={onLeave}>
          <Icon name="eye" size={16}/> {t("view_as_user")}
        </button>
        <button type="button" className="sd-btn is-primary"
                disabled={view.published && !view.has_changes}
                onClick={onPublish}>
          <Icon name="send" size={16}/> {t("publish")}
        </button>
      </div>
    </div>
  );
}
