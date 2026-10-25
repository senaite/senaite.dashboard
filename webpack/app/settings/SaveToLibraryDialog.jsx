import React, {useState} from "react";

import Dialog from "../components/Dialog";
import {Field, TextInput} from "./controls";
import {t} from "../i18n";

// A manager keeps the tile in the library, with a line on what it
// shows
export default function SaveToLibraryDialog({onSave, onClose}) {
  const [description, setDescription] = useState("");
  return (
    <Dialog title={t("save_to_library")} submitLabel={t("save")}
            onClose={onClose}
            onSubmit={() => onSave(description.trim())}>
      <p className="sd-hint">{t("save_to_library_hint")}</p>
      <Field label={t("description")}>
        <TextInput label={t("description")} value={description}
                   onChange={setDescription}/>
      </Field>
    </Dialog>
  );
}
