// SENAITE dashboard: mounts the dashboard app on its page.

import React from "react";
import {createRoot} from "react-dom/client";

import App from "./components/App";
import DatasetsApp from "./datasets/DatasetsApp";
import {createApi} from "./api";
import {setStrings} from "./i18n";
import {getTileType, getTileTypes, registerTileType} from "./tiles/registry";
import "./tiles";
import "./styles/dashboard.scss";

// Add-ons register their own tile types here, before the app mounts
window.senaite = window.senaite || {};
window.senaite.dashboard = {registerTileType, getTileType, getTileTypes};

// The pages of the add-on, by the element their script mounts on
const PAGES = {
  "senaite-dashboard": App,
  "senaite-dashboard-datasets": DatasetsApp
};

function mount() {
  const data = document.getElementById("senaite-dashboard-bootstrap");
  const id = Object.keys(PAGES).find((key) => document.getElementById(key));
  if (!data || !id) {
    return;
  }
  const boot = JSON.parse(data.textContent);
  const Page = PAGES[id];
  setStrings(boot.strings, boot.language);
  createRoot(document.getElementById(id)).render(
    <Page api={createApi(boot.api_url)} boot={boot}/>);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", mount);
} else {
  mount();
}
