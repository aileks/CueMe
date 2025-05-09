import { useAtomValue, useSetAtom } from 'jotai';
import { themeAtom, themeAtomWithEffect, type Theme } from '../store/theme';

export function useTheme() {
  const theme = useAtomValue(themeAtom);
  const setTheme = useSetAtom(themeAtomWithEffect);

  const toggleTheme = () => {
    setTheme();
  };

  const changeTheme = (newTheme: Theme) => {
    setTheme(newTheme);
  };

  return {
    theme,
    toggleTheme,
    changeTheme,
    isDark: theme === 'dark',
  };
}
