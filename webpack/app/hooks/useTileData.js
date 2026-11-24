import {useCallback, useRef, useState} from "react";

import {t} from "../i18n";

// Data requests at the same time. Each asks for one tile, so a slow
// tile does not hold back the others and the page fills as it goes.
const PARALLEL_REQUESTS = 3;

// What a data request needs of a tile
function requestOf(tile) {
  return {id: tile.id, source: tile.source, params: tile.params};
}

function withId(map, id, value) {
  return {...map, [id]: value};
}

function withoutId(map, id) {
  const next = {...map};
  delete next[id];
  return next;
}

// Runs the task for every item, at most `limit` of them at a time
async function eachLimited(items, limit, task) {
  const queue = items.slice();
  const worker = async () => {
    while (queue.length) {
      await task(queue.shift());
    }
  };
  const workers = Math.min(limit, queue.length);
  await Promise.all(Array.from({length: workers}, worker));
}

// The data a tile keeps after a request: what came back, or, when the
// request failed, the data it had unless that was an error too
function nextResult(previous, answer, failed) {
  if (failed && previous && !previous.error) {
    return previous;
  }
  return answer || {error: failed || t("no_data")};
}

// The data of the tiles on screen: what came back per tile, which tiles
// wait for theirs and when the data was computed. `viewRef` holds the
// dashboard on screen; an answer for a dashboard left meanwhile, or
// overtaken by a newer request for the same tile, is dropped.
export default function useTileData(api, viewRef, onError) {
  const [results, setResults] = useState({});
  const [pending, setPending] = useState({});
  const [updated, setUpdated] = useState(null);
  // The latest request per tile
  const sequence = useRef({count: 0, tiles: {}});

  const keep = useCallback((tileId, answer, failed) => {
    setResults((prev) => withId(
      prev, tileId, nextResult(prev[tileId], answer, failed)));
    setPending((prev) => withoutId(prev, tileId));
  }, []);

  const fetchTile = useCallback(async (tile, isLatest) => {
    let answer = null;
    let failed = null;
    try {
      const response = await api.data([requestOf(tile)]);
      answer = response.results[tile.id];
      setUpdated(response.now);
    } catch (exc) {
      failed = exc.message;
    }
    if (!isLatest(tile.id)) {
      return;
    }
    keep(tile.id, answer, failed);
    if (failed) {
      onError(failed);
    }
  }, [api, keep, onError]);

  // Ask for the data of the tiles that have a source
  const fetchData = useCallback(async (tiles) => {
    const wanted = tiles.filter((tile) => tile.source);
    if (!wanted.length) {
      return;
    }
    const viewId = viewRef.current && viewRef.current.id;
    const seq = (sequence.current.count += 1);
    wanted.forEach((tile) => {
      sequence.current.tiles[tile.id] = seq;
      setPending((prev) => withId(prev, tile.id, true));
    });
    const isLatest = (tileId) => sequence.current.tiles[tileId] === seq &&
      viewRef.current && viewRef.current.id === viewId;
    await eachLimited(wanted, PARALLEL_REQUESTS,
                      (tile) => fetchTile(tile, isLatest));
  }, [viewRef, fetchTile]);

  // Forget the data of a tile, e.g. when it got another source
  const forget = useCallback((tileId) => {
    setResults((prev) => withoutId(prev, tileId));
  }, []);

  const clear = useCallback(() => {
    setResults({});
    setPending({});
  }, []);

  return {results, pending, updated, fetchData, forget, clear};
}
