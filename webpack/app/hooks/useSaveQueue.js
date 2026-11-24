import {useCallback, useEffect, useRef, useState} from "react";

import useDebounce from "./useDebounce";

// Changes are saved once the user stopped changing for this long
const SAVE_DELAY = 600;

function sendSave(api, target, tiles, leaving) {
  return target.mode === "draft"
    ? api.saveDraft(target.id, tiles, leaving)
    : api.save(target.id, tiles, leaving);
}

// A change that could not be saved is lost when the page is left: the
// browser asks first
function useWarnOnLeave(active) {
  useEffect(() => {
    if (!active) {
      return undefined;
    }
    const warn = (event) => {
      event.preventDefault();
      event.returnValue = "";
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [active]);
}

// Saves the tiles of a dashboard after the user stopped changing them.
// The saves reach the server in order, each waits for the one before;
// only the answer of the latest one is passed to `onSaved`. Returns the
// state of saving, `persist(target, tiles)` and `finishSaving()`, which
// sends a change still waiting and waits for every save on its way.
export default function useSaveQueue(api, onSaved, onError) {
  const [saveState, setSaveState] = useState("idle");
  // The number of the latest save and the end of the chain of saves
  const saving = useRef({count: 0, last: Promise.resolve()});

  const save = useCallback(async (target, tiles, seq, leaving) => {
    setSaveState("saving");
    try {
      const saved = await sendSave(api, target, tiles, leaving);
      if (saving.current.count !== seq) {
        return;
      }
      onSaved(target, saved);
      setSaveState("saved");
    } catch (exc) {
      setSaveState("error");
      onError(exc);
    }
  }, [api, onSaved, onError]);

  // When the page is left there is no time to wait: that save goes out
  // at once, the page is gone before an answer could matter
  const [persist, flushSave] = useDebounce((target, tiles, leaving) => {
    const seq = (saving.current.count += 1);
    if (leaving) {
      return save(target, tiles, seq, true);
    }
    saving.current.last = saving.current.last.then(
      () => save(target, tiles, seq, false));
    return saving.current.last;
  }, SAVE_DELAY);

  const finishSaving = useCallback(async () => {
    flushSave();
    await saving.current.last;
  }, [flushSave]);

  useWarnOnLeave(saveState === "error");

  return {saveState, persist, finishSaving};
}
