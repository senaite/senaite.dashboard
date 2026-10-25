import React, {useEffect, useRef, useState} from "react";

import Icon from "./Icon";

const MOVES = {ArrowDown: 1, ArrowUp: -1};

// A button that opens a short list of actions. Focus moves into the
// list, the arrow keys move between the actions, Escape closes it and
// gives the focus back to the button. Tab closes it and moves on.
export default function Menu({label, ariaLabel, icon, items, className}) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);
  const trigger = useRef(null);
  const actions = items.filter(Boolean);

  const buttons = () => [...ref.current.querySelectorAll("[role=menuitem]")];
  const close = (refocus) => {
    setOpen(false);
    if (refocus && trigger.current) {
      trigger.current.focus();
    }
  };

  useEffect(() => {
    if (!open) {
      return undefined;
    }
    buttons()[0].focus();
    const onDown = (event) => {
      if (!ref.current.contains(event.target)) {
        close(false);
      }
    };
    document.addEventListener("mousedown", onDown);
    return () => document.removeEventListener("mousedown", onDown);
  }, [open]);  // eslint-disable-line react-hooks/exhaustive-deps

  const onKeyDown = (event) => {
    if (event.key === "Escape") {
      event.stopPropagation();
      close(true);
      return;
    }
    if (event.key === "Tab") {
      close(false);
      return;
    }
    const move = MOVES[event.key];
    if (!move) {
      return;
    }
    event.preventDefault();
    const list = buttons();
    const index = list.indexOf(document.activeElement);
    list[(index + move + list.length) % list.length].focus();
  };

  return (
    <div className={"sd-menu " + (className || "")} ref={ref}
         onKeyDown={open ? onKeyDown : undefined}>
      <button type="button" className="sd-btn" aria-haspopup="menu"
              aria-expanded={open} ref={trigger}
              aria-label={label ? undefined : ariaLabel}
              onClick={() => setOpen(!open)}>
        {icon ? <Icon name={icon} size={16}/> : null}
        {label ? <span>{label}</span> : null}
        {label ? <Icon name="chevron" size={14}/> : null}
      </button>
      {open ? (
        <ul className="sd-menu-list" role="menu">
          {actions.map((item) => (
            <li key={item.key} role="none">
              <button type="button" role="menuitem"
                      className={item.danger ? "is-danger" : ""}
                      onClick={() => { close(true); item.onClick(); }}>
                <Icon name={item.icon} size={16}/>
                <span>
                  <strong>{item.label}</strong>
                  {item.hint ? <small>{item.hint}</small> : null}
                </span>
              </button>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
