import {useCallback, useEffect, useState} from "react";

import {applyTheme, chooseTheme, initialTheme} from "../theme";

// The theme on screen and a way to change it
export default function useTheme() {
  const [theme, setTheme] = useState(initialTheme);
  useEffect(() => applyTheme(theme), [theme]);
  const change = useCallback((name) => {
    chooseTheme(name);
    setTheme(name);
  }, []);
  return [theme, change];
}
