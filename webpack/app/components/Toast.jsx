import React, {useEffect} from "react";

import Icon from "./Icon";
import {t} from "../i18n";

// Confirms what an action did, then goes away by itself. An undo
// button takes the action back.
export default function Toast({message, onClose, onUndo}) {
  useEffect(() => {
    if (!message) {
      return undefined;
    }
    const timer = setTimeout(onClose, 5000);
    return () => clearTimeout(timer);
  }, [message]);  // eslint-disable-line react-hooks/exhaustive-deps

  if (!message) {
    return null;
  }
  return (
    <div className="sd-toast" role="status">
      <Icon name="check" size={16}/>
      <span>{t(`notice_${message}`)}</span>
      {onUndo ? (
        <button type="button" className="sd-toast-action"
                onClick={() => { onUndo(); onClose(); }}>
          {t("undo")}
        </button>
      ) : null}
      <button type="button" className="sd-iconbtn is-small"
              aria-label={t("close")} onClick={onClose}>
        <Icon name="close" size={14}/>
      </button>
    </div>
  );
}
