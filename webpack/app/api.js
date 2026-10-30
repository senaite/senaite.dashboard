// Talks to the dashboard routes of senaite.jsonapi.

import {format, t} from "./i18n";

class ApiError extends Error {}

function isJson(response) {
  const type = response.headers.get("Content-Type") || "";
  return type.includes("application/json");
}

// Why a request failed. A run-out session answers 401, or a sign-in
// page instead of JSON, with 200 after a redirect.
function failure(response) {
  if (response.status === 401 || response.redirected || response.ok) {
    return t("session_expired");
  }
  return format("request_failed", {status: response.status});
}

async function send(url, options) {
  try {
    return await fetch(url, options);
  } catch (exc) {
    throw new ApiError(t("network_error"));
  }
}

export function createApi(baseUrl) {
  // keepalive lets a save finish while the page is being left; only
  // then, as the browser allows keepalive requests 64 KB in all
  async function request(path, body, keepalive = false) {
    const options = {
      credentials: "same-origin",
      keepalive,
      headers: {Accept: "application/json"}
    };
    if (body !== undefined) {
      options.method = "POST";
      options.headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(body);
    }
    const response = await send(`${baseUrl}${path}`, options);
    if (!isJson(response)) {
      throw new ApiError(failure(response));
    }
    const data = await response.json();
    if (response.status === 401) {
      throw new ApiError(failure(response));
    }
    if (!response.ok || data.success === false) {
      throw new ApiError(data.message || failure(response));
    }
    return data;
  }

  const id = (value) => encodeURIComponent(value);

  return {
    bootstrap: () => request("/bootstrap"),
    list: () => request("/list"),
    view: (dashboardId, draft) =>
      request(`/view/${id(dashboardId)}${draft ? "?draft=1" : ""}`),
    data: (tiles) => request("/data", {tiles}),
    choices: (dataset, field) =>
      request(`/choices/${id(dataset)}/${id(field)}`),
    save: (dashboardId, tiles, leaving) =>
      request(`/save/${id(dashboardId)}`, {tiles}, leaving),
    saveDraft: (dashboardId, tiles, leaving) =>
      request(`/draft/${id(dashboardId)}`, {tiles}, leaving),
    publish: (dashboardId) => request(`/publish/${id(dashboardId)}`, {}),
    discard: (dashboardId) => request(`/discard/${id(dashboardId)}`, {}),
    reset: (dashboardId) => request(`/reset/${id(dashboardId)}`, {}),
    activate: (dashboardId) =>
      request(`/activate/${id(dashboardId)}`, {}),
    create: (payload) => request("/new", payload),
    settings: (dashboardId, payload) =>
      request(`/settings/${id(dashboardId)}`, payload),
    remove: (dashboardId) => request(`/remove/${id(dashboardId)}`, {}),
    restoreDefaults: () => request("/defaults/restore", {}),
    saveToLibrary: (tile, description) =>
      request("/library/save", {tile, description}),
    removeFromLibrary: (presetId) =>
      request(`/library/remove/${id(presetId)}`, {}),
    // Datasets defined in the browser, for managers
    datasets: () => request("/datasets"),
    inspectType: (portalType) =>
      request(`/datasets/inspect/${id(portalType)}`),
    datasetUsage: (name) => request(`/datasets/usage/${id(name)}`),
    saveDataset: (definition) => request("/datasets/save", definition),
    removeDataset: (name) => request(`/datasets/remove/${id(name)}`, {})
  };
}
