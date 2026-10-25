import {useCallback, useEffect, useRef, useState} from "react";

import useDebounce from "./useDebounce";
import {normalizeTile} from "../model";

// Data is refreshed this often while the page is visible, in ms
const REFRESH_INTERVAL = 5 * 60 * 1000;
// Changes are saved once the user stopped changing for this long
const SAVE_DELAY = 600;

// What the data of a tile depends on
function signature(tile) {
  return tile.source ? JSON.stringify([tile.source, tile.params]) : null;
}

function dataTiles(tiles) {
  return tiles.filter((tile) => tile.source).map((tile) => ({
    id: tile.id, source: tile.source, params: tile.params
  }));
}

function withIds(map, ids, value) {
  const next = {...map};
  ids.forEach((id) => { next[id] = value; });
  return next;
}

function withoutIds(map, ids) {
  const next = {...map};
  ids.forEach((id) => { delete next[id]; });
  return next;
}

// Everything the page knows about the dashboard on screen, and what
// can be done with it.
export default function useDashboard(api, boot) {
  const [dashboards, setDashboards] = useState(boot.dashboards);
  const [view, setViewState] = useState(null);
  const [results, setResults] = useState({});
  const [pending, setPending] = useState({});
  const [saveState, setSaveState] = useState("idle");
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState(null);
  const [updated, setUpdated] = useState(null);
  // The view as of the last change, not the last render, so that two
  // changes in a row build on each other
  const viewRef = useRef(null);
  // The latest data request per tile; older answers are dropped
  const sequence = useRef({count: 0, tiles: {}});
  // Saves on their way to the server, and the number of the latest
  const saving = useRef({count: 0, requests: new Set()});

  const setView = useCallback((next) => {
    viewRef.current = next;
    setViewState(next);
  }, []);

  const fail = useCallback((exc) => {
    setError(exc.message || String(exc));
  }, []);

  const fetchData = useCallback(async (tiles) => {
    const wanted = dataTiles(tiles);
    if (!wanted.length) {
      return;
    }
    const viewId = viewRef.current && viewRef.current.id;
    const ids = wanted.map((tile) => tile.id);
    const seq = (sequence.current.count += 1);
    ids.forEach((id) => { sequence.current.tiles[id] = seq; });
    const isLatest = (id) => sequence.current.tiles[id] === seq &&
      viewRef.current && viewRef.current.id === viewId;
    setPending((prev) => withIds(prev, ids, true));
    let answers;
    try {
      const answer = await api.data(wanted);
      answers = answer.results;
      setUpdated(answer.now);
    } catch (exc) {
      answers = {};
      ids.forEach((id) => { answers[id] = {error: exc.message}; });
    }
    const current = ids.filter(isLatest);
    setResults((prev) => {
      const next = {...prev};
      current.forEach((id) => { next[id] = answers[id]; });
      return next;
    });
    setPending((prev) => withoutIds(prev, current));
  }, [api]);

  const show = useCallback((answer) => {
    const nextView = {...answer, tiles: answer.tiles.map(normalizeTile)};
    setView(nextView);
    fetchData(nextView.tiles);
  }, [setView, fetchData]);

  const reloadList = useCallback(async () => {
    const answer = await api.list();
    setDashboards(answer.dashboards);
    return answer;
  }, [api]);

  const refresh = useCallback(async () => {
    if (viewRef.current) {
      await fetchData(viewRef.current.tiles);
    }
  }, [fetchData]);

  // -- Saving ---------------------------------------------------------------

  const save = useCallback(async (target, tiles) => {
    const seq = (saving.current.count += 1);
    const isLatest = () => saving.current.count === seq;
    setSaveState("saving");
    try {
      const saved = target.mode === "draft"
        ? await api.saveDraft(target.id, tiles)
        : await api.save(target.id, tiles);
      if (!isLatest()) {
        return;
      }
      // Keep the tiles on screen, take over what the server says
      // about the dashboard (customized, unpublished changes)
      const current = viewRef.current;
      if (current && current.id === saved.id &&
          current.mode === saved.mode) {
        setView({...saved, tiles: current.tiles});
      }
      setSaveState("saved");
      if (target.mode === "draft") {
        reloadList().catch(() => null);
      }
    } catch (exc) {
      setSaveState("error");
      fail(exc);
    }
  }, [api, setView, reloadList, fail]);

  // A save is kept track of until it is done, so that an action can
  // wait for it
  const [persist, flushSave] = useDebounce((target, tiles) => {
    const request = save(target, tiles);
    const requests = saving.current.requests;
    requests.add(request);
    request.finally(() => requests.delete(request));
    return request;
  }, SAVE_DELAY);

  // Send the change still waiting and wait for every save on its way:
  // publishing, discarding or opening another dashboard must not
  // overtake the last change
  const finishSaving = useCallback(async () => {
    flushSave();
    await Promise.all(Array.from(saving.current.requests));
  }, [flushSave]);

  // Change the tiles: a list, or a function from the current tiles
  const setTiles = useCallback((change) => {
    const current = viewRef.current;
    const tiles = typeof change === "function"
      ? change(current.tiles) : change;
    const before = {};
    current.tiles.forEach((tile) => { before[tile.id] = tile; });
    const changed = tiles.filter((tile) => tile.source && (
      !before[tile.id] || signature(before[tile.id]) !== signature(tile)));
    // An answer of another source does not fit the tile any more
    const switched = changed.filter((tile) =>
      before[tile.id] && before[tile.id].source !== tile.source);
    if (switched.length) {
      setResults((prev) => withoutIds(prev, switched.map((tile) => tile.id)));
    }
    setView({...current, tiles});
    persist({id: current.id, mode: current.mode}, tiles);
    if (changed.length) {
      fetchData(changed);
    }
  }, [setView, persist, fetchData]);

  // -- Dashboard actions ----------------------------------------------------

  const open = useCallback(async (dashboardId, draft = false) => {
    await finishSaving();
    setError(null);
    try {
      const nextView = await api.view(dashboardId, draft);
      setResults({});
      setPending({});
      show(nextView);
      api.activate(dashboardId).catch(() => null);
    } catch (exc) {
      fail(exc);
    }
  }, [api, show, fail, finishSaving]);

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

  // Keep the numbers fresh while the page is on screen
  useEffect(() => {
    const timer = setInterval(() => {
      if (document.visibilityState === "visible") {
        refresh();
      }
    }, REFRESH_INTERVAL);
    return () => clearInterval(timer);
  }, [refresh]);

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
