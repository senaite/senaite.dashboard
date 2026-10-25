import React, {useEffect, useRef} from "react";

import Icon from "./Icon";
import {t} from "../i18n";

// A panel at the side. It is not modal: the dashboard stays visible and
// usable next to it, so a change shows on the tile while it is made.
// Escape closes it, unless a dialog is open on top; the focus goes
// back to where it came from.
export default function Drawer({title, onClose, children, footer}) {
  const ref = useRef(null);
  const close = useRef(onClose);
  close.current = onClose;

  useEffect(() => {
    const origin = document.activeElement;
    const onKey = (event) => {
      if (event.key === "Escape" && !document.querySelector(
        "dialog[open]")) {
        close.current();
      }
    };
    document.addEventListener("keydown", onKey);
    const first = ref.current.querySelector(
      "input, select, textarea, button:not(.sd-drawer-close)");
    if (first) {
      first.focus();
    }
    return () => {
      document.removeEventListener("keydown", onKey);
      if (origin && document.contains(origin)) {
        origin.focus();
      }
    };
  }, []);

  return (
    <aside className="sd-drawer" aria-label={title} ref={ref}>
      <header className="sd-drawer-head">
        <h2>{title}</h2>
        <button type="button" className="sd-iconbtn sd-drawer-close"
                onClick={onClose} aria-label={t("close")}>
          <Icon name="close"/>
        </button>
      </header>
      <div className="sd-drawer-body">{children}</div>
      {footer ? <footer className="sd-drawer-foot">{footer}</footer> : null}
    </aside>
  );
}
