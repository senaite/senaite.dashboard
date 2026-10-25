import React, {useState} from "react";

import Icon from "../components/Icon";

// Form controls of the settings panel, labelled the same way

// A control with its label. A group of buttons or checkboxes labels
// itself and must not sit in a label: a click on the label would press
// its first button.
export function Field({label, hint, group, children}) {
  const Tag = group ? "div" : "label";
  return (
    <Tag className="sd-field">
      <span className="sd-field-label">{label}</span>
      {children}
      {hint ? <span className="sd-field-hint">{hint}</span> : null}
    </Tag>
  );
}

export function Select({value, options, onChange, label, allowEmpty}) {
  return (
    <select className="sd-input" value={value === null ||
                                       value === undefined ? "" : value}
            aria-label={label}
            onChange={(event) => onChange(event.target.value || null)}>
      {allowEmpty !== undefined ? <option value="">{allowEmpty}</option>
        : null}
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.title}
        </option>
      ))}
    </select>
  );
}

// A choice among a few, as one row of buttons
export function Segmented({value, options, onChange, label}) {
  return (
    <div className="sd-segmented" role="radiogroup" aria-label={label}>
      {options.map((option) => (
        <button key={option.value} type="button" role="radio"
                aria-checked={value === option.value}
                onClick={() => onChange(option.value)}>
          {option.icon ? <Icon name={option.icon} size={16}/> : null}
          <span>{option.title}</span>
        </button>
      ))}
    </div>
  );
}

// A number in a range. What is typed stays as it is while the field
// has the focus, so that "12" can be typed where the least is 2; only
// a number in the range is taken over.
export function NumberInput({value, onChange, min, max, label}) {
  const [text, setText] = useState(null);
  const change = (event) => {
    const number = parseInt(event.target.value, 10);
    setText(event.target.value);
    if (number >= min && number <= max) {
      onChange(number);
    }
  };
  return (
    <input className="sd-input is-number" type="number" min={min} max={max}
           value={text === null ? value : text} aria-label={label}
           onChange={change} onBlur={() => setText(null)}/>
  );
}

export function TextInput({value, onChange, label, placeholder, required}) {
  return (
    <input className="sd-input" type="text" value={value || ""}
           aria-label={label} placeholder={placeholder} required={required}
           onChange={(event) => onChange(event.target.value)}/>
  );
}

export function Section({title, children}) {
  return (
    <section className="sd-section">
      <h3 className="sd-section-title">{title}</h3>
      {children}
    </section>
  );
}
