import React from "react";

import BarList from "../charts/BarList";
import Donut from "../charts/Donut";

export function BarTile({data}) {
  return <BarList items={data.items} total={data.total}/>;
}

export function DonutTile({data, size}) {
  return (
    <Donut items={data.items} kind={data.kind}
           width={size.width} height={size.height}/>
  );
}
