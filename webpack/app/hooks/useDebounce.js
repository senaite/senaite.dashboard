import {useCallback, useEffect, useRef} from "react";

// A stable function that runs the callback once calls have stopped for
// `wait` milliseconds, and a flush that runs a pending call at once.
// A pending call also runs when the page is left or hidden, so that a
// change made just before is not lost.
export default function useDebounce(callback, wait) {
  const timer = useRef(null);
  const pending = useRef(null);
  const latest = useRef(callback);
  latest.current = callback;

  const flush = useCallback(() => {
    clearTimeout(timer.current);
    const args = pending.current;
    pending.current = null;
    if (args) {
      latest.current(...args);
    }
  }, []);

  const debounced = useCallback((...args) => {
    pending.current = args;
    clearTimeout(timer.current);
    timer.current = setTimeout(flush, wait);
  }, [flush, wait]);

  useEffect(() => {
    const onHide = () => {
      if (document.visibilityState === "hidden") {
        flush();
      }
    };
    window.addEventListener("pagehide", flush);
    document.addEventListener("visibilitychange", onHide);
    return () => {
      window.removeEventListener("pagehide", flush);
      document.removeEventListener("visibilitychange", onHide);
      flush();
    };
  }, [flush]);

  return [debounced, flush];
}
