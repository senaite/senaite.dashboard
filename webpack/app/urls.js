// Addresses a user writes into a tile: a full URL or a mail address
// stays as it is, anything else is a page of the site, e.g. "samples".

const ABSOLUTE = /^((https?:)?\/\/|mailto:)/i;

export function resolveUrl(url, portalUrl) {
  if (ABSOLUTE.test(url)) {
    return url;
  }
  return `${portalUrl}/${url.replace(/^\/+/, "")}`;
}
