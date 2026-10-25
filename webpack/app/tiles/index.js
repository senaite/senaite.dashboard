import ChartTile from "./ChartTile";
import KpiTile from "./KpiTile";
import TableTile from "./TableTile";
import {BarTile, DonutTile} from "./GroupTiles";
import {LinksTile, NoteTile} from "./StaticTiles";
import {registerTileType} from "./registry";

registerTileType("kpi", {
  label: "type_kpi", icon: "kpi", component: KpiTile,
  accepts: ["scalar"], size: {w: 3, h: 2}
});
registerTileType("bar", {
  label: "type_bar", icon: "bar", component: BarTile,
  accepts: ["items"], size: {w: 6, h: 4}
});
registerTileType("donut", {
  label: "type_donut", icon: "donut", component: DonutTile,
  accepts: ["items"], size: {w: 4, h: 4}
});
registerTileType("chart", {
  label: "type_chart", icon: "chart", component: ChartTile,
  accepts: ["series"], size: {w: 8, h: 4}
});
registerTileType("table", {
  label: "type_table", icon: "table", component: TableTile,
  accepts: ["rows"], size: {w: 6, h: 4}
});
registerTileType("links", {
  label: "type_links", icon: "links", component: LinksTile,
  size: {w: 4, h: 3}
});
registerTileType("note", {
  label: "type_note", icon: "note", component: NoteTile,
  size: {w: 4, h: 3}
});
