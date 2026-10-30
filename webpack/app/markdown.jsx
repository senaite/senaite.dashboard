// The part of Markdown a note needs: headings, lists, quotes and
// paragraphs, with bold, italic, code and links inside them.
//
// It builds React elements and never HTML, so nothing a user writes
// runs as markup. A link leads to a page of the site, a web address
// or an e-mail address; any other kind of address stays plain text.

import React from "react";

import {resolveUrl} from "./urls";

const HEADING = /^(#{1,3})\s+(.*)$/;
const BULLET = /^\s*[-*+]\s+(.*)$/;
const NUMBER = /^\s*\d+[.)]\s+(.*)$/;
const QUOTE = /^>\s?(.*)$/;

// Bold, italic, code and links, in the order they are looked for
const INLINE = new RegExp([
  /\*\*(.+?)\*\*/.source,
  // An underscore inside a word, as in sample_due, is no italic
  /\*(.+?)\*|(?<![A-Za-z0-9])_(.+?)_(?![A-Za-z0-9])/.source,
  /`(.+?)`/.source,
  /\[([^\]]+)\]\(([^)\s]+)\)/.source
].join("|"), "g");

// An address with a scheme of its own, e.g. "https:" or "javascript:"
const SCHEME = /^[a-z][a-z0-9+.-]*:/i;
const SAFE_SCHEME = /^(https?|mailto):/i;

// Headings of a note sit below the title of the tile (h3)
const HEADING_TAGS = ["h4", "h5", "h6"];

// Where a link may lead, or null for an address that is not safe
function linkTarget(url, portalUrl) {
  if (SCHEME.test(url)) {
    return SAFE_SCHEME.test(url) ? url : null;
  }
  return resolveUrl(url, portalUrl);
}

// Whether a link leaves the site: compared by origin, as a prefix
// would take https://lims.example.com.other.tld for the site
function isExternal(href, portalUrl) {
  if (!/^(https?:)?\/\//i.test(href)) {
    return false;
  }
  const site = new URL(portalUrl, window.location.href).origin;
  return new URL(href, window.location.href).origin !== site;
}

function renderLink(text, url, key, portalUrl) {
  const href = linkTarget(url, portalUrl);
  const content = renderInline(text, portalUrl);
  if (!href) {
    return <React.Fragment key={key}>{content}</React.Fragment>;
  }
  const external = isExternal(href, portalUrl);
  return (
    <a key={key} href={href}
       {...(external ? {target: "_blank", rel: "noopener noreferrer"}
         : {})}>
      {content}
    </a>
  );
}

function renderMatch(match, key, portalUrl) {
  const [, bold, star, underscore, code, linkText, linkUrl] = match;
  if (bold !== undefined) {
    return <strong key={key}>{renderInline(bold, portalUrl)}</strong>;
  }
  if (star !== undefined || underscore !== undefined) {
    return <em key={key}>{renderInline(star || underscore, portalUrl)}</em>;
  }
  if (code !== undefined) {
    return <code key={key}>{code}</code>;
  }
  return renderLink(linkText, linkUrl, key, portalUrl);
}

// Text with bold, italic, code and links, as a list of elements
function renderInline(text, portalUrl) {
  const parts = [];
  const pattern = new RegExp(INLINE.source, "g");
  let last = 0;
  let match = pattern.exec(text);
  while (match) {
    if (match.index > last) {
      parts.push(text.slice(last, match.index));
    }
    parts.push(renderMatch(match, parts.length, portalUrl));
    last = pattern.lastIndex;
    match = pattern.exec(text);
  }
  if (last < text.length) {
    parts.push(text.slice(last));
  }
  return parts;
}

function blockOf(line) {
  let match = HEADING.exec(line);
  if (match) {
    return {kind: "heading", level: match[1].length, text: match[2]};
  }
  match = BULLET.exec(line);
  if (match) {
    return {kind: "ul", text: match[1]};
  }
  match = NUMBER.exec(line);
  if (match) {
    return {kind: "ol", text: match[1]};
  }
  match = QUOTE.exec(line);
  if (match) {
    return {kind: "quote", text: match[1]};
  }
  return {kind: "p", text: line};
}

// Lines that belong together: list items, quote lines and the lines
// of a paragraph join the block before them; a blank line ends it
function parseBlocks(text) {
  const blocks = [];
  let open = null;
  text.split(/\r?\n/).forEach((line) => {
    if (!line.trim()) {
      open = null;
      return;
    }
    const block = blockOf(line);
    if (block.kind === "heading") {
      blocks.push(block);
      open = null;
    } else if (open && open.kind === block.kind) {
      open.lines.push(block.text);
    } else {
      open = {kind: block.kind, lines: [block.text]};
      blocks.push(open);
    }
  });
  return blocks;
}

// The lines of a paragraph or quote, with the breaks the user made
function withBreaks(lines, portalUrl) {
  return lines.map((line, index) => (
    <React.Fragment key={index}>
      {index ? <br/> : null}
      {renderInline(line, portalUrl)}
    </React.Fragment>
  ));
}

function renderBlock(block, key, portalUrl) {
  switch (block.kind) {
    case "heading": {
      const Tag = HEADING_TAGS[block.level - 1];
      return <Tag key={key}>{renderInline(block.text, portalUrl)}</Tag>;
    }
    case "ul":
    case "ol": {
      const Tag = block.kind;
      return (
        <Tag key={key}>
          {block.lines.map((line, index) => (
            <li key={index}>{renderInline(line, portalUrl)}</li>
          ))}
        </Tag>
      );
    }
    case "quote":
      return (
        <blockquote key={key}>{withBreaks(block.lines, portalUrl)}</blockquote>
      );
    default:
      return <p key={key}>{withBreaks(block.lines, portalUrl)}</p>;
  }
}

export default function Markdown({text, portalUrl}) {
  return parseBlocks(text).map((block, index) =>
    renderBlock(block, index, portalUrl));
}
