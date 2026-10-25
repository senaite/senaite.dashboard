import React, {useState} from "react";

import Dialog from "./Dialog";
import {Field, Segmented, TextInput} from "../settings/controls";
import {t, titleText} from "../i18n";

export function NewDashboardDialog({manage, canCopy, onCreate, onClose}) {
  const [title, setTitle] = useState("");
  const [scope, setScope] = useState("personal");
  const [start, setStart] = useState("empty");
  return (
    <Dialog title={t("create_dashboard")} submitLabel={t("create")}
            onClose={onClose}
            onSubmit={() => title.trim() && onCreate({
              title: title.trim(), scope, copy: start === "copy"})}>
      <Field label={t("dashboard_title")}>
        <TextInput label={t("dashboard_title")} value={title}
                   onChange={setTitle} required/>
      </Field>
      {manage ? (
        <Field label={t("for_roles")} group>
          <Segmented label={t("for_roles")} value={scope}
                     options={[
                       {value: "personal", title: t("new_personal"),
                        icon: "user"},
                       {value: "global", title: t("new_global"),
                        icon: "globe"}]}
                     onChange={setScope}/>
        </Field>
      ) : null}
      {canCopy ? (
        <Field label={t("new_dashboard_hint")} group>
          <Segmented label={t("new_dashboard_hint")} value={start}
                     options={[
                       {value: "empty", title: t("start_empty")},
                       {value: "copy", title: t("start_from_copy"),
                        icon: "copy"}]}
                     onChange={setStart}/>
        </Field>
      ) : null}
    </Dialog>
  );
}

function RoleChecks({roles, selected, onChange, label}) {
  const toggle = (role) => onChange(selected.includes(role)
    ? selected.filter((item) => item !== role) : selected.concat(role));
  return (
    <div className="sd-checks is-columns" role="group" aria-label={label}>
      {roles.map((role) => (
        <label key={role.id} className="sd-check">
          <input type="checkbox" checked={selected.includes(role.id)}
                 onChange={() => toggle(role.id)}/>
          {role.title}
        </label>
      ))}
    </div>
  );
}

export function DashboardSettingsDialog({view, roles, onSave, onClose}) {
  const [title, setTitle] = useState(titleText(view.title));
  const [selected, setSelected] = useState(view.roles || []);
  const global = view.kind === "global";
  return (
    <Dialog title={t("settings")} submitLabel={t("save")} onClose={onClose}
            onSubmit={() => title.trim() && onSave({
              title: title.trim(), roles: global ? selected : undefined})}>
      <Field label={t("dashboard_title")}>
        <TextInput label={t("dashboard_title")} value={title}
                   onChange={setTitle} required/>
      </Field>
      {global ? (
        <Field label={t("for_roles")} group hint={selected.length ? null
          : t("for_everybody")}>
          <RoleChecks roles={roles} selected={selected} label={t("for_roles")}
                      onChange={setSelected}/>
        </Field>
      ) : null}
    </Dialog>
  );
}

export function ConfirmDialog({title, text, label, onConfirm, onClose,
                               danger = true}) {
  return (
    <Dialog title={title} submitLabel={label} danger={danger}
            onClose={onClose}
            onSubmit={onConfirm}>
      <p>{text}</p>
    </Dialog>
  );
}
