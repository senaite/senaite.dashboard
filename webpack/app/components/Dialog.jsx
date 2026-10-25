import React, {useEffect, useRef} from "react";

import {t} from "../i18n";

// A modal dialog on the native element: focus stays inside, Escape
// closes it.
export default function Dialog({title, onClose, onSubmit, submitLabel,
                                danger, children}) {
  const ref = useRef(null);
  useEffect(() => {
    const dialog = ref.current;
    dialog.showModal();
    return () => dialog.open && dialog.close();
  }, []);

  const submit = (event) => {
    event.preventDefault();
    onSubmit();
  };

  return (
    <dialog ref={ref} className="sd-dialog" onCancel={onClose}
            aria-label={title}>
      <form onSubmit={submit}>
        <h2 className="sd-dialog-title">{title}</h2>
        <div className="sd-dialog-body">{children}</div>
        <div className="sd-dialog-actions">
          <button type="button" className="sd-btn" onClick={onClose}>
            {t("cancel")}
          </button>
          <button type="submit"
                  className={"sd-btn " + (danger ? "is-danger" : "is-primary")}>
            {submitLabel}
          </button>
        </div>
      </form>
    </dialog>
  );
}
