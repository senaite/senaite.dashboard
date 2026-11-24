import {useCallback, useEffect, useRef, useState} from "react";

import useSaveQueue from "./useSaveQueue";
import useTileData from "./useTileData";
import {normalizeTile} from "../model";

// Data is refreshed this often while the page is visible, in ms
const REFRESH_INTERVAL = 5 * 60 * 1000;

// What the data of a tile depends on
function signature(tile) {
  return tile.source ? JSON.stringify([tile.source, tile.params]) : null;
}

function byId(tiles) {
  const map = {};
  tiles.forEach((tile) => { map[tile.id] = tile; });
  return map;
}

// Whether a tile needs new data after a change: it is new, or its
// source or parameters changed
function needsData(tile, before) {
  return Boolean(tile.source) &&
    (!before || signature(before) !== signature(tile));
}

// Whether the data a tile has is of another source than it has now
function switchedSource(tile, before) {
  return Boolean(before) && before.source !== tile.source;
}

// A request whose failure does not matter, e.g. telling the server
// which dashboard was opened last: the page works without it
function ignoreFailure(promise) {
  return promise.catch(() => null);
}

function errorText(exc) {
  return exc.message || String(exc);
}

// Refresh while the page is on screen
function useAutoRefresh(refresh) {
  useEffect(() => {
    const timer = setInterval(() => {
      if (document.visibilityState === "visible") {
        refresh();
      }
    }, REFRESH_INTERVAL);
    return () => clearInterval(timer);
  }, [refresh]);
}

// Everything the page knows about the dashboard on screen, and what
// can be done with it.
export default function useDashboard(api, boot) {
  const [dashboards, setDashboards] = useState(boot.dashboards);
  const [view, setViewState] = useState(null);
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState(null);
  // The view as of the last change, not the last render, so that two
  // changes in a row build on each other
  const viewRef = useRef(null);

  const setView = useCallback((next) => {
    viewRef.current = next;
    setViewState(next);
  }, []);

  const fail = useCallback((exc) => setError(errorText(exc)), []);

  const {results, pending, updated, fetchData, forget, clear} =
    useTileData(api, viewRef, setError);

  const reloadList = useCallback(async () => {
    const answer = await api.list();
    setDashboards(answer.dashboards);
    return answer;
  }, [api]);

  // Keep the tiles on screen, take over what the server says about
  // the dashboard (customized, unpublished changes)
  const onSaved = useCallback((target, saved) => {
    const current = viewRef.current;
    if (current && current.id === saved.id && current.mode === saved.mode) {
      setView({...saved, tiles: current.tiles});
    }
    if (target.mode === "draft") {
      ignoreFailure(reloadList());
    }
  }, [setView, reloadList]);

  const {saveState, persist, finishSaving} = useSaveQueue(
    api, onSaved, fail);

  const show = useCallback((answer) => {
    const nextView = {...answer, tiles: answer.tiles.map(normalizeTile)};
    setView(nextView);
    fetchData(nextView.tiles);
  }, [setView, fetchData]);

  const refresh = useCallback(async () => {
    if (viewRef.current) {
      await fetchData(viewRef.current.tiles);
    }
  }, [fetchData]);

  // Change the tiles: a list, or a function from the current tiles
  const setTiles = useCallback((change) => {
    const current = viewRef.current;
    const tiles = typeof change === "function"
      ? change(current.tiles) : change;
    const before = byId(current.tiles);
    // An answer of another source does not fit the tile any more
    tiles.filter((tile) => switchedSource(tile, before[tile.id]))
      .forEach((tile) => forget(tile.id));
    setView({...current, tiles});
    persist({id: current.id, mode: current.mode}, tiles);
    fetchData(tiles.filter((tile) => needsData(tile, before[tile.id])));
  }, [setView, persist, fetchData, forget]);

  const open = useCallback(async (dashboardId, draft = false) => {
    await finishSaving();
    setError(null);
    try {
      const nextView = await api.view(dashboardId, draft);
      clear();
      show(nextView);
      ignoreFailure(api.activate(dashboardId));
    } catch (exc) {
      fail(exc);
    }
  }, [api, show, fail, finishSaving, clear]);

  // Runs an action after the saves on their way; its failure is shown
  const run = useCallback(async (action) => {
    await finishSaving();
    setError(null);
    try {
      return await action();
    } catch (exc) {
      fail(exc);
      return null;
    }
  }, [fail, finishSaving]);

  const afterChange = useCallback(async (nextView, message) => {
    if (nextView) {
      show(nextView);
      await reloadList();
      setNotice(message || null);
    }
    return nextView;
  }, [show, reloadList]);

  const currentId = () => viewRef.current.id;

  const actions = {
    open,
    refresh,
    setTiles,
    // Once published, the draft has nothing left to show: back to the
    // dashboard as everybody sees it
    publish: () => run(async () => {
      const dashboardId = currentId();
      await api.publish(dashboardId);
      await open(dashboardId);
      await reloadList();
      setNotice("published");
    }),
    discard: () => run(async () =>
      afterChange(await api.discard(currentId()), "discarded")),
    reset: () => run(async () =>
      afterChange(await api.reset(currentId()), "was_reset")),
    create: (payload) => run(async () =>
      afterChange(await api.create(payload))),
    settings: (payload) => run(async () =>
      afterChange(await api.settings(currentId(), payload))),
    remove: () => run(async () => {
      await api.remove(currentId());
      const answer = await reloadList();
      if (answer.active) {
        await open(answer.active);
      } else {
        setView(null);
      }
    }),
    // Missing default dashboards come back as drafts: the first one
    // opens, so that it can be looked at and published
    restoreDefaults: () => run(async () => {
      const answer = await api.restoreDefaults();
      setDashboards(answer.dashboards);
      if (!answer.created.length) {
        setNotice("defaults_complete");
        return;
      }
      await open(answer.created[0], true);
      setNotice("defaults_restored");
    }),
    // The library as the server has it after the change, or null
    saveToLibrary: (tile, description) => run(async () => {
      const answer = await api.saveToLibrary(tile, description);
      setNotice("saved_to_library");
      return answer;
    }),
    removeFromLibrary: (presetId) => run(async () => {
      const answer = await api.removeFromLibrary(presetId);
      setNotice("removed_from_library");
      return answer;
    }),
    notify: (message) => setNotice(message),
    dismissError: () => setError(null),
    dismissNotice: () => setNotice(null)
  };

  useAutoRefresh(refresh);

  useEffect(() => {
    if (boot.active) {
      open(boot.active);
    }
  }, []);  // eslint-disable-line react-hooks/exhaustive-deps

  return {
    dashboards, view, results, pending, saveState, error, updated, notice,
    actions
  };
}
