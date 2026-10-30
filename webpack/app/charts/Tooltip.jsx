import React from "react";

// A tooltip at a point of its positioned parent, kept inside it
export default function Tooltip({x, y, width, children}) {
  if (x === null || x === undefined) {
    return null;
  }
  const flip = width && x > width * 0.6;
  const style = flip
    ? {right: Math.max(0, width - x + 12), top: y}
    : {left: x + 12, top: y};
  return (
    <div className="sd-tooltip" style={style}>
      {children}
    </div>
  );
}

export function TooltipRow({color, label, value, strong}) {
  return (
    <div className={"sd-tooltip-row" + (strong ? " is-strong" : "")}>
      {color ? <span className="sd-swatch" style={{background: color}}/>
        : <span className="sd-swatch is-empty"/>}
      <span className="sd-tooltip-label">{label}</span>
      <span className="sd-tooltip-value">{value}</span>
    </div>
  );
}
