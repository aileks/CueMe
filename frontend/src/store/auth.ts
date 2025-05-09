import { atom } from 'jotai';

export interface User {
  id: string;
  username: string;
  email: string;
}

export const userAtom = atom<User | null>(null);
export const isLoadingAtom = atom<boolean>(true);

export const isAuthenticatedAtom = atom(get => get(userAtom) !== null);

export const loginAction = atom(
  get => get(userAtom),
  (_, set, userData: User) => {
    set(userAtom, userData);
  }
);

export const logoutAction = atom(
  get => get(userAtom),
  async (_, set) => {
    try {
      const response = await fetch('/api/auth/logout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });

      if (response.ok) {
        set(userAtom, null);
      } else {
        console.error('Logout failed');
      }
    } catch (error) {
      console.error('Logout failed:', error);
    }
  }
);

export const checkAuthAction = atom(
  get => get(isLoadingAtom),
  async (_, set) => {
    set(isLoadingAtom, true);
    try {
      const response = await fetch('/api/auth/', {
        credentials: 'include',
      });

      if (response.ok) {
        const userData = await response.json();
        set(userAtom, userData);
      } else {
        // Clear user data if not authenticated
        set(userAtom, null);
      }
    } catch (error) {
      console.error('Authentication check failed:', error);
      set(userAtom, null);
    } finally {
      set(isLoadingAtom, false);
    }
  }
);
