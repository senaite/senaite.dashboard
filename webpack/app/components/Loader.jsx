import React from "react";

// The loader of the SENAITE listings: four dots that circle each other
export default function Loader({label}) {
  return (
    <div className="sd-loader" role="status">
      <span className="sd-loader-dots" aria-hidden="true">
        <span/><span/><span/><span/>
      </span>
      {label ? <span className="sd-loader-label">{label}</span> : null}
    </div>
  );
}
