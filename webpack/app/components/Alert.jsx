import React from "react";

import Icon from "./Icon";
import {t} from "../i18n";

// What went wrong, until the user closes it
export default function Alert({message, onClose}) {
  if (!message) {
    return null;
  }
  return (
    <div className="sd-alert" role="alert">
      <Icon name="alert" size={16}/>
      <span>{message}</span>
      <button type="button" className="sd-iconbtn"
              aria-label={t("close")} onClick={onClose}>
        <Icon name="close" size={16}/>
      </button>
    </div>
  );
}
