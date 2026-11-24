import React, {useMemo, useState} from "react";

import Alert from "./Alert";
import DashboardDialogs from "./DashboardDialogs";
import EmptyState from "./EmptyState";
import Grid from "./Grid";
import {Greeting, Tabs} from "./Header";
import Icon from "./Icon";
import Library from "./Library";
import ModeBars from "./ModeBars";
import Toast from "./Toast";
import ViewActions from "./ViewActions";
import TileSettings from "../settings/TileSettings";
import useDashboard from "../hooks/useDashboard";
import useTheme from "../hooks/useTheme";
import {nudgeTile, placeTile, settle} from "../layout";
import {newTileId, tileFromPreset} from "../model";
import {t} from "../i18n";

function byName(items) {
  const map = {};
  items.forEach((item) => { map[item.name] = item; });
  return map;
}

// How many tiles of the view have their data, while some still wait
// for it; null once all of them have it
function loadingProgress(view, pending) {
  const tiles = view ? view.tiles.filter((tile) => tile.source) : [];
  const waiting = tiles.filter((tile) => pending[tile.id]).length;
  return waiting ? {done: tiles.length - waiting, total: tiles.length}
    : null;
}

// Which dashboard a change was made on: its draft is another one
function viewKey(view) {
  return view ? `${view.id}/${view.mode}` : null;
}

export default function App({api, boot}) {
  const {dashboards, view, results, pending, saveState, error, updated,
         notice, actions} = useDashboard(api, boot);
  const [editing, setEditing] = useState(false);
  const [panel, setPanel] = useState(null);
  const [dialog, setDialog] = useState(null);
  const [spotlight, setSpotlight] = useState(null);
  const [undo, setUndo] = useState(null);
  const [library, setLibrary] = useState({
    presets: boot.presets, categories: boot.categories
  });
  const permissions = boot.permissions;
  const [theme, setTheme] = useTheme();

  const context = useMemo(() => ({
    api,
    portalUrl: boot.portal_url,
    datasets: byName(boot.datasets),
    sources: byName(boot.sources),
    limits: boot.limits,
    defaultTrend: boot.default_trend
  }), [api, boot]);

  const progress = loadingProgress(view, pending);
  const draft = view && view.mode === "draft";
  const isEditing = Boolean(view) && (draft || editing);

  const close = () => {
    setPanel(null);
    setDialog(null);
  };
  const open = (dashboardId, asDraft = false) => {
    close();
    setEditing(false);
    setUndo(null);
    actions.dismissNotice();
    actions.open(dashboardId, asDraft);
  };

  const addTile = (preset) => {
    const tile = tileFromPreset(preset);
    actions.setTiles((tiles) => tiles.concat(placeTile(tiles, tile)));
    setSpotlight(tile.id);
    // A tile that shows nothing yet is filled in right away
    if (preset.configure) {
      setPanel({kind: "settings", tileId: tile.id});
    }
  };
  // A tile may change its size with its kind; the others make room
  const changeTile = (tile) => actions.setTiles((tiles) =>
    settle(tiles.map((item) => item.id === tile.id ? tile : item)));
  const updateLibrary = async (change) => {
    const answer = await change;
    if (answer) {
      setLibrary({presets: answer.presets, categories: answer.categories});
    }
  };
  const nudge = (tileId, step) =>
    actions.setTiles((tiles) => nudgeTile(tiles, tileId, step));
  const removeTile = (tileId) => {
    if (panel && panel.tileId === tileId) {
      setPanel(null);
    }
    const before = view.tiles;
    actions.setTiles(settle(before.filter((tile) => tile.id !== tileId)));
    setUndo({key: viewKey(view), tiles: before});
    actions.notify("tile_removed");
  };

  const create = async ({title, scope, copy}) => {
    close();
    // A copy gets tiles of its own, never the ids of the original
    const tiles = copy && view
      ? view.tiles.map((tile) => ({...tile, id: newTileId()})) : [];
    const created = await actions.create({title, scope, tiles});
    if (created) {
      setEditing(true);
      if (!tiles.length) {
        setPanel({kind: "library"});
      }
    }
  };

  const panelTile = panel && panel.kind === "settings" && view
    ? view.tiles.find((tile) => tile.id === panel.tileId) : null;
  // Undo puts the tiles back only on the dashboard they were taken from
  const onUndo = notice === "tile_removed" && undo &&
    undo.key === viewKey(view) ? () => actions.setTiles(undo.tiles) : null;

  return (
    <div className={"sd-app" + (isEditing ? " is-editing" : "") +
                    (panel ? " has-panel" : "")}>
      <Greeting user={boot.user} now={boot.now} updated={updated}
                progress={progress} onRefresh={actions.refresh}/>
      <Tabs dashboards={dashboards} activeId={view && view.id}
            manage={permissions.manage} onOpen={(id) => open(id)}>
        {permissions.customize ? (
          <button type="button" className="sd-tab-add"
                  onClick={() => setDialog("new")}
                  title={t("create_dashboard")}>
            <Icon name="plus" size={16}/>
            <span>{t("create_dashboard")}</span>
          </button>
        ) : null}
        {view && !isEditing ? (
          <ViewActions view={view} permissions={permissions}
                       datasetsUrl={boot.datasets_url}
                       onEdit={() => setEditing(true)}
                       onEditDraft={() => open(view.id, true)}
                       onDialog={setDialog}
                       theme={theme} onTheme={setTheme}/>
        ) : null}
      </Tabs>

      <Alert message={error} onClose={actions.dismissError}/>

      <ModeBars view={view} editing={editing}
                manage={permissions.manage} saveState={saveState}
                onAdd={() => setPanel({kind: "library"})}
                onPublish={() => { close(); actions.publish(); }}
                onDiscard={actions.discard}
                onLeave={() => open(view.id)}
                onOpenDraft={() => open(view.id, true)}
                onReset={() => setDialog("reset")}
                onDone={() => { close(); setEditing(false); }}/>

      <main className="sd-main">
        {view && view.tiles.length ? (
          <Grid tiles={view.tiles} results={results} pending={pending}
                editing={isEditing} context={context}
                spotlight={spotlight}
                onTilesChange={actions.setTiles}
                onSettings={(tileId) => setPanel({kind: "settings", tileId})}
                onRemove={removeTile} onNudge={nudge}/>
        ) : null}
        {view && !view.tiles.length ? (
          <EmptyState text={t("empty_dashboard")} action={t("add_tile")}
                      onAction={permissions.customize ? () => {
                        setEditing(true);
                        setPanel({kind: "library"});
                      } : null}/>
        ) : null}
        {!dashboards.length ? (
          <EmptyState text={t("no_dashboards")}
                      action={t("create_dashboard")}
                      onAction={permissions.customize
                        ? () => setDialog("new") : null}
                      other={t("restore_defaults")}
                      onOther={permissions.manage
                        ? () => setDialog("defaults") : null}/>
        ) : null}
      </main>

      {panel && panel.kind === "library" ? (
        <Library presets={library.presets} categories={library.categories}
                 onAdd={addTile} onClose={close}
                 onRemove={(preset) => updateLibrary(
                   actions.removeFromLibrary(preset.id))}/>
      ) : null}
      {panelTile ? (
        <TileSettings key={panelTile.id} tile={panelTile} context={context}
                      onChange={changeTile} onClose={close}
                      onSaveToLibrary={permissions.manage
                        ? (description) => updateLibrary(
                          actions.saveToLibrary(panelTile, description))
                        : null}/>
      ) : null}

      <Toast message={notice} onUndo={onUndo}
             onClose={() => { setUndo(null); actions.dismissNotice(); }}/>

      <DashboardDialogs
        dialog={dialog} view={view} roles={boot.roles}
        manage={permissions.manage}
        canCopy={Boolean(view && view.tiles.length)}
        onClose={close} onCreate={create}
        onSettings={(settings) => { close(); actions.settings(settings); }}
        onDelete={() => { close(); actions.remove(); }}
        onRestoreDefaults={() => {
          close();
          setEditing(false);
          actions.restoreDefaults();
        }}
        onReset={() => {
          close();
          setEditing(false);
          actions.reset();
        }}/>
    </div>
  );
}
