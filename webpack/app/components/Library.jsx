import React, {useState} from "react";

import {ConfirmDialog} from "./Dialogs";
import Drawer from "./Drawer";
import Icon from "./Icon";
import {t, titleText} from "../i18n";
import {getTileType} from "../tiles/registry";

function matches(preset, query) {
  if (!query) {
    return true;
  }
  const text = `${titleText(preset.tile.title)} ${preset.description}`;
  return text.toLowerCase().includes(query.toLowerCase());
}

function PresetCard({preset, added, onAdd, onRemove}) {
  const type = getTileType(preset.tile.type);
  return (
    <li className="sd-preset">
      <span className="sd-preset-icon">
        <Icon name={type ? type.icon : "layout"} size={20}/>
      </span>
      <span className="sd-preset-text">
        <strong>{titleText(preset.tile.title)}</strong>
        <span>{preset.description}</span>
      </span>
      <button type="button"
              className={"sd-btn is-small" + (added ? " is-done" : "")}
              onClick={() => onAdd(preset)}
              aria-label={`${t("add_to_dashboard")}: ` +
                          titleText(preset.tile.title)}>
        <Icon name={added ? "check" : "plus"} size={16}/>
        {t("add_to_dashboard")}
      </button>
      {preset.removable ? (
        <button type="button" className="sd-iconbtn is-small is-danger"
                onClick={() => onRemove(preset)}
                title={t("remove_from_library")}
                aria-label={`${t("remove_from_library")}: ` +
                            titleText(preset.tile.title)}>
          <Icon name="trash" size={14}/>
        </button>
      ) : null}
    </li>
  );
}

// Ready-made tiles, by category; one click adds a tile
export default function Library({presets, categories, onAdd, onRemove,
                                 onClose}) {
  const [query, setQuery] = useState("");
  const [removing, setRemoving] = useState(null);
  const [category, setCategory] = useState(null);
  const [added, setAdded] = useState({});
  const used = categories.filter((cat) =>
    presets.some((preset) => preset.category === cat.id));
  // A category whose last preset was removed shows all again
  const active = used.some((cat) => cat.id === category) ? category : null;
  const shown = presets.filter((preset) =>
    (!active || preset.category === active) && matches(preset, query));

  const add = (preset) => {
    onAdd(preset);
    setAdded((prev) => ({...prev, [preset.id]: true}));
  };

  return (
    <Drawer title={t("library")} onClose={onClose}>
      <p className="sd-hint">{t("library_hint")}</p>
      <label className="sd-search">
        <Icon name="search" size={16}/>
        <input type="search" value={query} placeholder={t("search_tiles")}
               aria-label={t("search_tiles")}
               onChange={(event) => setQuery(event.target.value)}/>
      </label>
      <div className="sd-chips" role="group">
        <button type="button" aria-pressed={!active}
                className="sd-chip" onClick={() => setCategory(null)}>
          {t("all")}
        </button>
        {used.map((cat) => (
          <button key={cat.id} type="button" className="sd-chip"
                  aria-pressed={active === cat.id}
                  onClick={() => setCategory(cat.id)}>
            {cat.title}
          </button>
        ))}
      </div>
      <ul className="sd-presets">
        {shown.map((preset) => (
          <PresetCard key={preset.id} preset={preset}
                      added={added[preset.id]} onAdd={add}
                      onRemove={setRemoving}/>
        ))}
      </ul>
      {removing ? (
        <ConfirmDialog title={t("remove_from_library")}
                       text={titleText(removing.tile.title)}
                       label={t("delete")}
                       onClose={() => setRemoving(null)}
                       onConfirm={() => {
                         onRemove(removing);
                         setRemoving(null);
                       }}/>
      ) : null}
    </Drawer>
  );
}
