// The automatic JSX runtime on top of the shared React of the page.
//
// Libraries compiled for React 17+ import `react/jsx-runtime`. React
// itself comes from senaite.core as a global (see webpack externals);
// this maps the runtime calls onto its createElement, so no second
// copy of React ends up in the bundle.

import React from "react";

function withKey(props, key) {
  return key === undefined ? props : {...props, key};
}

export const Fragment = React.Fragment;

export function jsx(type, props, key) {
  return React.createElement(type, withKey(props, key));
}

export function jsxs(type, props, key) {
  const {children, ...rest} = props;
  return React.createElement(type, withKey(rest, key), ...children);
}

export const jsxDEV = jsx;
