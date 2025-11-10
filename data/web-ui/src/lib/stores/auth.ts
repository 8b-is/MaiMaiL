import { writable, derived } from 'svelte/store';
import type { User, AuthState } from '$lib/types';
import { api } from '$lib/api/client';

function createAuthStore() {
  const initialState: AuthState = {
    user: null,
    isAuthenticated: false,
  };

  const { subscribe, set, update } = writable<AuthState>(initialState);

  return {
    subscribe,

    async init() {
      try {
        const user = await api.getAuthStatus();
        if (user) {
          set({
            user,
            isAuthenticated: true,
          });
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error);
      }
    },

    async login(username: string, password: string) {
      try {
        const user = await api.login({ username, password });
        set({
          user,
          isAuthenticated: true,
        });
        return { success: true };
      } catch (error: any) {
        return { success: false, error: error.message };
      }
    },

    async logout() {
      try {
        await api.logout();
      } catch (error) {
        console.error('Logout error:', error);
      } finally {
        set({
          user: null,
          isAuthenticated: false,
        });
      }
    },

    setUser(user: User | null) {
      update((state) => ({
        ...state,
        user,
        isAuthenticated: !!user,
      }));
    },
  };
}

export const auth = createAuthStore();

// Derived stores
export const currentUser = derived(auth, ($auth) => $auth.user);
export const isAuthenticated = derived(auth, ($auth) => $auth.isAuthenticated);
export const isAdmin = derived(auth, ($auth) => $auth.user?.role === 'admin');
export const isDomainAdmin = derived(
  auth,
  ($auth) => $auth.user?.role === 'admin' || $auth.user?.role === 'domainadmin'
);
