import React from "react";

// Line icons on a 24 unit grid, stroked with the current color
const PATHS = {
  plus: "M12 5v14M5 12h14",
  close: "M6 6l12 12M18 6L6 18",
  check: "M5 12.5l4.5 4.5L19 7.5",
  edit: "M4 20h4L19 9l-4-4L4 16v4zM13.5 6.5l4 4",
  sliders: "M4 7h10M18 7h2M4 17h4M12 17h8M16 5v4M10 15v4",
  grip: "M9 6h.01M15 6h.01M9 12h.01M15 12h.01M9 18h.01M15 18h.01",
  refresh: "M20 11a8 8 0 1 0-2.3 5.7M20 5v6h-6",
  trash: "M5 7h14M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3",
  search: "M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14zM20 20l-4-4",
  external: "M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7" +
    "a1 1 0 0 1 1-1h5",
  more: "M5 12h.01M12 12h.01M19 12h.01",
  chevron: "M6 9l6 6 6-6",
  undo: "M9 14L4 9l5-5M4 9h10a6 6 0 0 1 0 12h-3",
  globe: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM3 12h18M12 3c2.5 3 2.5 " +
    "15 0 18M12 3c-2.5 3-2.5 15 0 18",
  user: "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM5 20a7 7 0 0 1 14 0",
  inbox: "M4 13l2.5-7h11l2.5 7v6H4v-6zM4 13h5l1 2h4l1-2h5",
  flask: "M9 3h6M10 3v6L5 18a2 2 0 0 0 1.7 3h10.6a2 2 0 0 0 1.7-3L14 " +
    "9V3M7.5 14h9",
  send: "M21 3L10 14M21 3l-7 18-4-7-7-4 18-7z",
  alert: "M12 8v5M12 16.5h.01M10.3 4.2L2.6 18a2 2 0 0 0 1.7 3h15.4a2 " +
    "2 0 0 0 1.7-3L13.7 4.2a2 2 0 0 0-3.4 0z",
  clock: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 7v5l3 2",
  file: "M14 3H6v18h12V7l-4-4zM14 3v4h4M9 13h6M9 17h6",
  list: "M9 6h11M9 12h11M9 18h11M4.5 6h.01M4.5 12h.01M4.5 18h.01",
  grid: "M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z",
  layout: "M4 4h16v16H4zM4 10h16M10 10v10",
  kpi: "M4 18V6M4 18h16M8 14l3-3 3 2 5-6",
  bar: "M4 6h10M4 12h16M4 18h7",
  donut: "M12 3a9 9 0 1 0 9 9h-5a4 4 0 1 1-4-4V3z",
  chart: "M4 20V10M9 20V4M14 20v-7M19 20v-11",
  table: "M4 5h16v14H4zM4 10h16M4 15h16M10 5v14",
  links: "M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 " +
    "0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1",
  note: "M5 4h14v12l-4 4H5V4zM15 20v-4h4M9 9h6M9 13h4",
  lock: "M6 11h12v9H6zM8 11V8a4 4 0 0 1 8 0v3",
  eye: "M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12zM12 15a3 3 0 1 " +
    "0 0-6 3 3 0 0 0 0 6z",
  copy: "M8 8h12v12H8zM4 16V4h12"
};

export default function Icon({name, size = 18, title}) {
  const path = PATHS[name] || PATHS.layout;
  return (
    <svg className="sd-icon" width={size} height={size} viewBox="0 0 24 24"
         fill="none" stroke="currentColor" strokeWidth="1.75"
         strokeLinecap="round" strokeLinejoin="round"
         aria-hidden={title ? undefined : "true"} role={title ? "img" : null}>
      {title ? <title>{title}</title> : null}
      <path d={path}/>
    </svg>
  );
}
