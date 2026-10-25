import React from "react";

import Icon from "../components/Icon";
import {Field, Section, Segmented, TextInput} from "./controls";
import {NAMED} from "../colors";
import {newTileId} from "../model";
import {t, titleText, withText} from "../i18n";

// How the tile looks, by its type: the color of a number, the style
// of a chart, the text of a note, the links of a link tile

const NOTE_STYLES = ["plain", "info", "warning"];

function LinksEditor({links, onChange}) {
  const set = (index, change) => onChange(links.map((link, i) =>
    i === index ? {...link, ...change} : link));
  return (
    <div className="sd-linklist">
      {links.map((link, index) => (
        <div key={link.id || index} className="sd-linkrow">
          <TextInput label={t("tile_title")} value={link.title}
                     placeholder={t("tile_title")}
                     onChange={(title) => set(index, {title})}/>
          <TextInput label={t("url")} value={link.url}
                     placeholder="samples"
                     onChange={(url) => set(index, {url})}/>
          <button type="button" className="sd-iconbtn is-small"
                  aria-label={t("delete")}
                  onClick={() => onChange(links.filter((other, position) =>
                    position !== index))}>
            <Icon name="close" size={14}/>
          </button>
        </div>
      ))}
      <button type="button" className="sd-btn is-small"
              onClick={() => onChange(links.concat(
                {id: newTileId(), title: "", url: ""}))}>
        <Icon name="plus" size={16}/> {t("add_link")}
      </button>
    </div>
  );
}

export default function AppearanceSection({tile, update}) {
  const setOption = (change) =>
    update({options: {...tile.options, ...change}});
  const fields = [];
  if (tile.type === "kpi") {
    fields.push(
      <Field key="color" label={t("color")} group>
        <div className="sd-swatches" role="radiogroup"
             aria-label={t("color")}>
          {Object.entries(NAMED).map(([name, color]) => (
            <button key={name} type="button" role="radio"
                    aria-checked={tile.options.color === name}
                    aria-label={name} style={{background: color}}
                    onClick={() => setOption({color: name})}/>
          ))}
        </div>
      </Field>);
  }
  if (tile.type === "chart") {
    fields.push(
      <Field key="style" label={t("style")} group>
        <Segmented label={t("style")} value={tile.options.style || "bars"}
                   options={["bars", "area", "line"].map((value) => ({
                     value, title: t(`style_${value}`)}))}
                   onChange={(value) => setOption({style: value})}/>
      </Field>);
  }
  if (tile.source) {
    fields.push(
      <Field key="link" label={t("link")} hint={t("link_hint")}>
        <TextInput label={t("link")} value={tile.options.link}
                   placeholder="samples"
                   onChange={(link) => setOption({link})}/>
      </Field>);
  }
  if (tile.type === "note") {
    fields.push(
      <Field key="note_style" label={t("style")} group>
        <Segmented label={t("style")} value={tile.options.style || "plain"}
                   options={NOTE_STYLES.map((value) => ({
                     value, title: t(`note_${value}`)}))}
                   onChange={(value) => setOption({style: value})}/>
      </Field>,
      <Field key="text" label={t("type_note")} hint={t("markdown_hint")}>
        <textarea className="sd-input" rows={10}
                  value={titleText(tile.options.text)}
                  placeholder={t("note_placeholder")}
                  onChange={(event) => setOption({
                    text: withText(tile.options.text, event.target.value)
                  })}/>
      </Field>);
  }
  if (tile.type === "links") {
    fields.push(
      <LinksEditor key="links" links={tile.options.links || []}
                   onChange={(links) => setOption({links})}/>);
  }
  return fields.length
    ? <Section title={t("appearance")}>{fields}</Section> : null;
}
