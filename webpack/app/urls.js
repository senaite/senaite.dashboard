// Addresses a user writes into a tile: a full URL stays as it is,
// anything else is a page of the site, e.g. "samples".

const ABSOLUTE = /^(https?:)?\/\//;

export function resolveUrl(url, portalUrl) {
  if (ABSOLUTE.test(url)) {
    return url;
  }
  return `${portalUrl}/${url.replace(/^\/+/, "")}`;
}
