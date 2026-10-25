import React, {useState} from "react";

import AdvancedSection from "./AdvancedSection";
import AppearanceSection from "./AppearanceSection";
import DataSection from "./DataSection";
import Drawer from "../components/Drawer";
import Icon from "../components/Icon";
import SaveToLibraryDialog from "./SaveToLibraryDialog";
import {Section, Segmented, TextInput} from "./controls";
import {t, titleText, withTitle} from "../i18n";
import {getTileType, typesFor} from "../tiles/registry";

// Everything about one tile. Changes apply at once; the tile shows
// them next to the panel.
export default function TileSettings({tile, onChange, onClose, context,
                                      onSaveToLibrary}) {
  const [saving, setSaving] = useState(false);
  const update = (change) => onChange({...tile, ...change});
  const source = context.sources[tile.source];
  const types = source ? typesFor(source.output) : [];
  const type = getTileType(tile.type);
  return (
    <Drawer title={t("tile_settings")} onClose={onClose}
            footer={
              <>
                {onSaveToLibrary ? (
                  <button type="button" className="sd-btn"
                          onClick={() => setSaving(true)}>
                    <Icon name="plus" size={16}/> {t("save_to_library")}
                  </button>
                ) : null}
                <button type="button" className="sd-btn is-primary"
                        onClick={onClose}>{t("done")}</button>
              </>}>
      {saving ? (
        <SaveToLibraryDialog
          onClose={() => setSaving(false)}
          onSave={(description) => {
            setSaving(false);
            onSaveToLibrary(description);
          }}/>
      ) : null}
      <Section title={t("tile_title")}>
        <TextInput label={t("tile_title")} value={titleText(tile.title)}
                   onChange={(text) => update({
                     title: withTitle(tile.title, text)})}/>
      </Section>
      {types.length > 1 ? (
        <Section title={t("tile_type")}>
          <Segmented label={t("tile_type")} value={tile.type}
                     options={types.map((item) => ({
                       value: item.name, title: t(item.label),
                       icon: item.icon}))}
                     onChange={(value) => update({type: value})}/>
        </Section>
      ) : null}
      {type ? null : <p className="sd-hint">{tile.type}</p>}
      <DataSection tile={tile} update={update} context={context}/>
      <AppearanceSection tile={tile} update={update}/>
      <AdvancedSection tile={tile} update={update}/>
    </Drawer>
  );
}
