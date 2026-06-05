import { writable } from 'svelte/store';
import type { Theme } from '$lib/types';

function createThemeStore() {
  // Get initial theme from localStorage or system preference
  const getInitialTheme = (): Theme => {
    if (typeof window === 'undefined') return 'system';

    const stored = localStorage.getItem('theme') as Theme;
    if (stored && ['light', 'dark', 'system'].includes(stored)) {
      return stored;
    }

    return 'system';
  };

  const { subscribe, set } = writable<Theme>(getInitialTheme());

  const applyTheme = (theme: Theme) => {
    if (typeof window === 'undefined') return;

    const root = document.documentElement;

    if (theme === 'system') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.classList.toggle('dark', prefersDark);
    } else {
      root.classList.toggle('dark', theme === 'dark');
    }
  };

  return {
    subscribe,

    init() {
      const theme = getInitialTheme();
      applyTheme(theme);

      // Listen for system theme changes
      if (typeof window !== 'undefined') {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
          const currentTheme = localStorage.getItem('theme') as Theme;
          if (!currentTheme || currentTheme === 'system') {
            applyTheme('system');
          }
        });
      }
    },

    setTheme(theme: Theme) {
      if (typeof window !== 'undefined') {
        localStorage.setItem('theme', theme);
      }
      set(theme);
      applyTheme(theme);
    },

    toggle() {
      const currentTheme = getInitialTheme();
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      this.setTheme(newTheme);
    },
  };
}

export const theme = createThemeStore();
