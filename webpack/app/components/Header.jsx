import React, {useState} from "react";

import Icon from "./Icon";
import {formatDateTime, formatToday} from "../format";
import {format, t, titleText} from "../i18n";

// The answers are often cached and back at once: the button turns at
// least this long, so that a click is seen to do something
const REFRESH_MIN_MS = 600;

function greeting(now) {
  const hour = new Date(now).getHours();
  if (hour < 12) {
    return t("good_morning");
  }
  return hour < 18 ? t("good_afternoon") : t("good_evening");
}

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function RefreshButton({updated, onRefresh}) {
  const [busy, setBusy] = useState(false);
  const refresh = async () => {
    setBusy(true);
    try {
      await Promise.all([onRefresh(), wait(REFRESH_MIN_MS)]);
    } finally {
      setBusy(false);
    }
  };
  return (
    <button type="button" className={"sd-refresh" + (busy ? " is-busy" : "")}
            onClick={refresh} disabled={busy} aria-busy={busy}
            title={t("refresh")}>
      <Icon name="refresh" size={16}/>
      <span role="status">
        {busy ? t("refreshing")
          : updated ? format("last_updated",
                             {time: formatDateTime(updated)})
            : t("refresh")}
      </span>
    </button>
  );
}

// How far the data of the dashboard has come, while it is loading
function LoadingStatus({progress}) {
  return (
    <p className="sd-loading" role="status">
      <span className="sd-spinner" aria-hidden="true"/>
      {format("loading_progress", progress)}
    </p>
  );
}

export function Greeting({user, now, updated, progress, onRefresh}) {
  return (
    <div className="sd-greeting">
      <div>
        <h1 className="sd-hello">
          {greeting(now)}, {user.fullname.split(" ")[0]}
        </h1>
        <p className="sd-today">{formatToday(now)}</p>
      </div>
      {progress ? <LoadingStatus progress={progress}/>
        : <RefreshButton updated={updated} onRefresh={onRefresh}/>}
    </div>
  );
}

function TabBadge({dashboard, manage}) {
  if (!manage || dashboard.kind !== "global") {
    return null;
  }
  if (!dashboard.published) {
    return <span className="sd-badge is-draft">{t("not_published")}</span>;
  }
  if (dashboard.has_changes) {
    return (
      <span className="sd-badge is-draft"
            title={t("unpublished_changes")}>{t("draft")}</span>
    );
  }
  return null;
}

// The dashboards a user can switch between. Each is a page of its own,
// so this is navigation, not a tab widget.
export function Tabs({dashboards, activeId, manage, loading, onOpen,
                     children}) {
  return (
    <nav className="sd-tabs" aria-label={t("dashboards")}>
      {loading ? <span className="sd-progress" aria-hidden="true"/> : null}
      <ul>
        {dashboards.map((dashboard) => (
          <li key={dashboard.id}>
            <button type="button" className="sd-tab"
                    aria-current={dashboard.id === activeId
                      ? "page" : undefined}
                    onClick={() => onOpen(dashboard.id)}
                    title={dashboard.kind === "personal"
                      ? t("personal") : t("global")}>
              {dashboard.kind === "personal"
                ? <Icon name="user" size={14}/> : null}
              <span>{titleText(dashboard.title)}</span>
              <TabBadge dashboard={dashboard} manage={manage}/>
            </button>
          </li>
        ))}
      </ul>
      {children}
    </nav>
  );
}
