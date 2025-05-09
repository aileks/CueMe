import { atom } from 'jotai';
import { atomWithStorage } from 'jotai/utils';

const applyTheme = (theme: string) => {
  if (theme === 'dark') {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
};

const getInitialTheme = (): string => {
  const storedTheme = localStorage.getItem('queme-theme');
  if (storedTheme === 'dark' || storedTheme === 'light') {
    return storedTheme;
  }
  return window.matchMedia('(prefers-color-scheme: dark)').matches ?
      'dark'
    : 'light';
};

const themeStorage = {
  getItem: (key: string): string => {
    const storedValue = localStorage.getItem(key);
    return storedValue === null ? getInitialTheme() : storedValue;
  },
  setItem: (key: string, value: string): void => {
    localStorage.setItem(key, value);
    applyTheme(value);
  },
  removeItem: (key: string): void => {
    localStorage.removeItem(key);
  },
};

export const themeAtom = atomWithStorage<string>(
  'queme-theme',
  getInitialTheme(),
  themeStorage
);

export const themeAtomWithEffect = atom(
  get => get(themeAtom),
  (get, set, newTheme?: string) => {
    const theme = newTheme ?? (get(themeAtom) === 'light' ? 'dark' : 'light');
    set(themeAtom, theme);
  }
);

export const initializeTheme = () => {
  const initialTheme = getInitialTheme();
  applyTheme(initialTheme);

  // Ensure localStorage has the current theme
  if (!localStorage.getItem('queme-theme')) {
    localStorage.setItem('queme-theme', initialTheme);
  }
};
