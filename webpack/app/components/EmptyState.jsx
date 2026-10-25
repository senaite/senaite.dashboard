import React from "react";

import Icon from "./Icon";

// An empty board says what is missing and, if the user may, offers
// to fill it, and maybe a second way to do so
export default function EmptyState({text, action, onAction, other,
                                    onOther}) {
  return (
    <div className="sd-emptyboard">
      <Icon name="layout" size={32}/>
      <p>{text}</p>
      {onAction || onOther ? (
        <div className="sd-emptyboard-actions">
          {onAction ? (
            <button type="button" className="sd-btn is-primary"
                    onClick={onAction}>
              <Icon name="plus" size={16}/> {action}
            </button>
          ) : null}
          {onOther ? (
            <button type="button" className="sd-btn" onClick={onOther}>
              <Icon name="undo" size={16}/> {other}
            </button>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
