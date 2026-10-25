import {useEffect, useRef, useState} from "react";

// The size of an element, kept up to date
export default function useSize() {
  const ref = useRef(null);
  const [size, setSize] = useState({width: 0, height: 0});
  useEffect(() => {
    const element = ref.current;
    if (!element) {
      return undefined;
    }
    const observer = new ResizeObserver(([entry]) => {
      const {width, height} = entry.contentRect;
      setSize({width: Math.floor(width), height: Math.floor(height)});
    });
    observer.observe(element);
    return () => observer.disconnect();
  }, []);
  return [ref, size];
}
