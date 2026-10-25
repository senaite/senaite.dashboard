# -*- coding: utf-8 -*-
"""Titles, in one language or in several.

A title is a message id of the code, a text, or {language: text} for
what users write on a site with several languages: dashboards, tiles,
notes, datasets defined in the browser.
"""

import re
import unicodedata

from bika.lims import api
from senaite.core.i18n import translate
from senaite.dashboard import messagefactory as _
from senaite.dashboard.exceptions import QueryError
from zope.i18nmessageid import Message

MAX_TITLE_LENGTH = 200
MAX_TITLE_LANGUAGES = 20

LANGUAGE_RE = re.compile(r"^[a-z]{2,3}(-[a-z]{2,4})?\Z", re.IGNORECASE)


def is_language(value):
    return isinstance(value, basestring) and bool(LANGUAGE_RE.match(value))


def clean_text_title(title):
    if not isinstance(title, basestring):
        return u""
    return title.strip()[:MAX_TITLE_LENGTH]


def clean_title(title):
    """A title is text, or {language: text} with non-empty texts."""
    if not isinstance(title, dict):
        return clean_text_title(title)
    texts = {lang: clean_text_title(text) for lang, text in title.items()
             if is_language(lang)}
    texts = {lang: text for lang, text in texts.items() if text}
    if len(texts) > MAX_TITLE_LANGUAGES:
        raise QueryError(_("A title has too many languages"))
    return texts


def title_text(title, language="en"):
    """Return a title as text, in the language if it has several."""
    if isinstance(title, dict):
        return (title.get(language) or title.get("en") or
                next(iter(title.values()), u""))
    return title or u""


def get_language():
    """The language of the current request."""
    return api.get_request().get("LANGUAGE", "") or "en"


def display_title(title):
    """A title as the user of the request reads it.

    A message id of the code is translated; a title written for
    several languages shows the one of the request.
    """
    if isinstance(title, Message):
        return translate(title, to_utf8=False)
    return api.safe_unicode(title_text(title, get_language()))


def slugify(title, default):
    """An id from a title; accents fold to their base letter."""
    text = api.safe_unicode(title_text(title))
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", text)[:40].strip("-")
    return str(slug or default)
