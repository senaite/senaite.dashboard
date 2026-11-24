import React from "react";

import {ConfirmDialog, DashboardSettingsDialog,
        NewDashboardDialog} from "./Dialogs";
import {t, withTitle} from "../i18n";

// The dialog that is open, by its name, or nothing
export default function DashboardDialogs({dialog, view, roles, manage,
                                          canCopy, onClose, onCreate,
                                          onSettings, onDelete,
                                          onRestoreDefaults, onReset}) {
  switch (dialog) {
  case "new":
    return (
      <NewDashboardDialog manage={manage} canCopy={canCopy}
                          onCreate={onCreate} onClose={onClose}/>
    );
  case "settings":
    return (
      <DashboardSettingsDialog
        view={view} roles={roles} onClose={onClose}
        onSave={({title, roles: chosen}) => onSettings({
          title: withTitle(view.title, title), roles: chosen})}/>
    );
  case "delete":
    return (
      <ConfirmDialog title={t("delete_dashboard")}
                     text={t("delete_confirm")} label={t("delete")}
                     onClose={onClose} onConfirm={onDelete}/>
    );
  case "defaults":
    return (
      <ConfirmDialog title={t("restore_defaults")}
                     text={t("restore_defaults_confirm")}
                     label={t("restore")} danger={false}
                     onClose={onClose} onConfirm={onRestoreDefaults}/>
    );
  case "reset":
    return (
      <ConfirmDialog title={t("reset")} text={t("reset_confirm")}
                     label={t("reset")} onClose={onClose}
                     onConfirm={onReset}/>
    );
  default:
    return null;
  }
}
