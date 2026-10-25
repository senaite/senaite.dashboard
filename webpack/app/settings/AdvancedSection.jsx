import React, {useEffect, useRef, useState} from "react";

import {t} from "../i18n";

// The parameters of the tile as JSON, for what the other controls
// do not offer. A change applies when the field loses the focus, and
// only if it is a valid JSON object.

// The parameters in the text, or null if it holds no JSON object
function parseParams(text) {
  let params;
  try {
    params = JSON.parse(text);
  } catch (exc) {
    return null;
  }
  const isObject = params && typeof params === "object" &&
    !Array.isArray(params);
  return isObject ? params : null;
}
export default function AdvancedSection({tile, update}) {
  const stored = JSON.stringify(tile.params, null, 2);
  const [text, setText] = useState(stored);
  const [error, setError] = useState(null);
  const editing = useRef(false);
  // Follow changes made with the other controls, unless typing here
  useEffect(() => {
    if (!editing.current) {
      setText(stored);
    }
  }, [stored]);
  if (!tile.source) {
    return null;
  }
  const apply = () => {
    editing.current = false;
    if (text === stored) {
      return;
    }
    const params = parseParams(text);
    if (!params) {
      setError(t("invalid_json"));
      return;
    }
    update({params});
    setError(null);
  };
  return (
    <details className="sd-advanced">
      <summary>{t("advanced")}</summary>
      <textarea className="sd-input is-code" rows={12} value={text}
                spellCheck={false} aria-label={t("advanced")}
                onFocus={() => { editing.current = true; }}
                onChange={(event) => setText(event.target.value)}
                onBlur={apply}/>
      {error ? <span className="sd-field-hint is-error">{error}</span>
        : null}
    </details>
  );
}
