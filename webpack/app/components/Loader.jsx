import React from "react";

// The corners of a cell: the hexagon of the SENAITE logo, point up
const CELL = "10,1 19,6 19,16 10,21 1,16 1,6";

// Three cells of the logo hexagon that light up one after the other
export default function Loader({label}) {
  return (
    <div className="sd-loader" role="status">
      <span className="sd-loader-cells" aria-hidden="true">
        {[0, 1, 2].map((index) => (
          <svg key={index} viewBox="0 0 20 22">
            <polygon points={CELL}/>
          </svg>
        ))}
      </span>
      {label ? <span className="sd-loader-label">{label}</span> : null}
    </div>
  );
}
