// Talks to the dashboard routes of senaite.jsonapi.

export class ApiError extends Error {}

export function createApi(baseUrl) {
  // keepalive lets a save finish while the page is being left
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
    const response = await fetch(`${baseUrl}${path}`, options);
    let data = {};
    try {
      data = await response.json();
    } catch (error) {
      throw new ApiError(response.statusText);
    }
    if (!response.ok || data.success === false) {
      throw new ApiError(data.message || response.statusText);
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
    save: (dashboardId, tiles) =>
      request(`/save/${id(dashboardId)}`, {tiles}, true),
    saveDraft: (dashboardId, tiles) =>
      request(`/draft/${id(dashboardId)}`, {tiles}, true),
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
