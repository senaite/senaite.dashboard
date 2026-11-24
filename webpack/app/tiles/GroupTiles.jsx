import React from "react";

import BarList from "../charts/BarList";
import Donut from "../charts/Donut";

// A group opens to its objects
function groupPick(onPick) {
  return onPick ? (item, color) => onPick({key: item.key}, item.label, color)
    : null;
}

export function BarTile({data, onPick}) {
  return (
    <BarList items={data.items} total={data.total}
             onPick={groupPick(onPick)}/>
  );
}

export function DonutTile({data, size, onPick}) {
  return (
    <Donut items={data.items} kind={data.kind}
           width={size.width} height={size.height}
           onPick={groupPick(onPick)}/>
  );
}
