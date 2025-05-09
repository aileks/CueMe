import { atom } from 'jotai';
import { atomWithStorage } from 'jotai/utils';

export type Theme = 'light' | 'dark';

export const themeAtom = atomWithStorage<Theme>(
  'queme-theme',
  // Default to system preference if available, otherwise default to light
  window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
);

const applyTheme = (theme: Theme) => {
  if (theme === 'dark') {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
};

// Apply theme when atom changes
export const themeAtomWithEffect = atom(
  get => get(themeAtom),
  (get, set, newTheme?: Theme) => {
    // Toggle theme if no value provided
    const theme = newTheme ?? (get(themeAtom) === 'light' ? 'dark' : 'light');
    set(themeAtom, theme);
    applyTheme(theme);
  }
);

export const initializeTheme = () => {
  const storedTheme = localStorage.getItem('queme-theme');
  if (storedTheme) {
    applyTheme(storedTheme as Theme);
  } else {
    // Use system preference
    const prefersDark = window.matchMedia(
      '(prefers-color-scheme: dark)'
    ).matches;
    applyTheme(prefersDark ? 'dark' : 'light');
  }
};
