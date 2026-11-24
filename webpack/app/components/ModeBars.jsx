import React from "react";

import {DraftBar, EditBar, PendingBar} from "./Bars";

// The bar of the mode the dashboard is in: the draft of a global
// dashboard, changes of it not yet published, or editing in place
export default function ModeBars({view, editing, manage, saveState,
                                  onAdd, onPublish, onDiscard, onLeave,
                                  onOpenDraft, onReset, onDone}) {
  if (!view) {
    return null;
  }
  const draft = view.mode === "draft";
  const unpublished = !editing && manage && view.kind === "global" &&
    view.published && view.has_changes;
  if (draft) {
    return (
      <DraftBar view={view} saveState={saveState} onAdd={onAdd}
                onPublish={onPublish} onDiscard={onDiscard}
                onLeave={onLeave}/>
    );
  }
  if (unpublished) {
    return <PendingBar onOpenDraft={onOpenDraft}/>;
  }
  if (editing) {
    return (
      <EditBar saveState={saveState}
               customized={view.kind === "global" && view.customized}
               onAdd={onAdd} onReset={onReset} onDone={onDone}/>
    );
  }
  return null;
}
