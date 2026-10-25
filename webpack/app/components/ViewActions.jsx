import React from "react";

import Icon from "./Icon";
import Menu from "./Menu";
import {t} from "../i18n";

// The ways to change a global dashboard: for oneself, and for
// everybody if the user manages dashboards
function customizeItems(view, permissions, onEdit, onEditDraft) {
  if (view.kind !== "global") {
    return [];
  }
  return [
    permissions.customize && {
      key: "mine", icon: "user", label: t("edit_mine"),
      hint: t("edit_mine_hint"), onClick: onEdit},
    permissions.manage && {
      key: "draft", icon: "globe", label: t("edit_draft"),
      hint: t("edit_draft_hint"), onClick: onEditDraft}
  ].filter(Boolean);
}

// Everything else, in the menu behind the three dots
function moreItems(view, permissions, datasetsUrl, onDialog) {
  const global = view.kind === "global";
  // A personal dashboard is the user's own; a global one is a
  // manager's to rename and delete
  const owns = !global || permissions.manage;
  return [
    owns && {key: "settings", icon: "sliders", label: t("settings"),
             onClick: () => onDialog("settings")},
    global && view.customized && {
      key: "reset", icon: "undo", label: t("reset"),
      onClick: () => onDialog("reset")},
    permissions.manage && {
      key: "defaults", icon: "undo", label: t("restore_defaults"),
      hint: t("restore_defaults_hint"),
      onClick: () => onDialog("defaults")},
    permissions.manage && {
      key: "datasets", icon: "list", label: t("manage_datasets"),
      hint: t("manage_datasets_hint"),
      onClick: () => { window.location.href = datasetsUrl; }},
    // A danger stays last
    owns && {key: "delete", icon: "trash", danger: true,
             label: t("delete_dashboard"),
             onClick: () => onDialog("delete")}
  ].filter(Boolean);
}

// The actions of the dashboard on screen, depending on what it is and
// what the user may do. One way to customize is a button, two are a
// menu; a personal dashboard is customized in place.
export default function ViewActions({view, permissions, datasetsUrl,
                                     onEdit, onEditDraft, onDialog}) {
  const customize = customizeItems(view, permissions, onEdit, onEditDraft);
  const more = moreItems(view, permissions, datasetsUrl, onDialog);
  const personal = view.kind !== "global" && permissions.customize;
  const button = customize.length === 1 || personal;
  return (
    <div className="sd-viewactions">
      {view.customized ? (
        <span className="sd-badge" title={t("edit_mine_hint")}>
          {t("customized")}
        </span>
      ) : null}
      {customize.length > 1 ? (
        <Menu label={t("customize")} icon="edit" items={customize}/>
      ) : null}
      {button ? (
        <button type="button" className="sd-btn"
                onClick={personal ? onEdit : customize[0].onClick}>
          <Icon name="edit" size={16}/> {t("customize")}
        </button>
      ) : null}
      {more.length ? <Menu icon="more" ariaLabel={t("more")} items={more}
                           className="is-compact"/> : null}
    </div>
  );
}
