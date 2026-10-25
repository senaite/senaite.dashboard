import React from "react";

import Icon from "../components/Icon";
import Markdown from "../markdown";
import {t, titleText} from "../i18n";
import {resolveUrl} from "../urls";

export function LinksTile({tile, portalUrl}) {
  const links = (tile.options.links || []).filter((link) => link.url);
  if (!links.length) {
    return <p className="sd-empty">{t("empty_tile")}</p>;
  }
  return (
    <ul className="sd-links">
      {links.map((link, index) => (
        <li key={index}>
          <a href={resolveUrl(link.url, portalUrl)}>
            <Icon name={link.icon || "external"} size={16}/>
            <span>{link.title || link.url}</span>
          </a>
        </li>
      ))}
    </ul>
  );
}

// A text in Markdown, in the language of the page; as a notice it
// stands out in the color of its kind
export function NoteTile({tile, portalUrl}) {
  const text = titleText(tile.options.text).trim();
  if (!text) {
    return <p className="sd-empty">{t("note_placeholder")}</p>;
  }
  const style = tile.options.style || "plain";
  return (
    <div className={`sd-note is-${style}`}>
      <Markdown text={text} portalUrl={portalUrl}/>
    </div>
  );
}
