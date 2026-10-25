import React from "react";

import Icon from "./Icon";
import {t} from "../i18n";

// Keeps a tile that fails to render from taking the dashboard with it.
// Tile types may come from add-ons; one broken type shows an error in
// its own tiles and nowhere else.
export default class TileBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {error: null};
  }

  static getDerivedStateFromError(error) {
    return {error};
  }

  componentDidUpdate(prevProps) {
    // A changed tile, or new data for it, gets another chance
    const changed = prevProps.tile !== this.props.tile ||
      prevProps.data !== this.props.data;
    if (this.state.error && changed) {
      this.setState({error: null});
    }
  }

  render() {
    if (this.state.error) {
      return (
        <p className="sd-tile-error">
          <Icon name="alert" size={16}/> {t("tile_failed")}
        </p>
      );
    }
    return this.props.children;
  }
}
