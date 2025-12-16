import { defineStore } from 'pinia';
import authService from '../services/auth';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    loading: false,
  }),

  getters: {
    currentUser: (state) => state.user,
    hasPermission: (state) => (permission) => {
      if (!state.user) return false;
      // Admin role has all permissions, owner role also has all
      if (state.user.role === 'admin' || state.user.role === 'owner' || state.user.role === 'SUPER_ADMIN') {
        return true;
      }
      return state.user.permissions?.includes(permission) || false;
    },
    hasRole: (state) => (role) => {
      if (!state.user) return false;
      return state.user.role === role || state.user.role === 'SUPER_ADMIN';
    },
  },

  actions: {
    async login(credentials) {
      this.loading = true;
      try {
        console.log('[AuthStore] Starting login process');
        const response = await authService.login(credentials);
        
        // Ensure user is set from response or localStorage
        this.user = response.user || authService.getCurrentUser();
        
        // Only set authenticated if we have both user and token
        const hasToken = !!authService.getToken();
        const hasUser = !!this.user;
        this.isAuthenticated = hasToken && hasUser;
        
        console.log('[AuthStore] Login completed:', {
          hasUser: hasUser,
          hasToken: hasToken,
          isAuthenticated: this.isAuthenticated,
          userEmail: this.user?.email
        });
        
        if (!this.isAuthenticated) {
          console.warn('[AuthStore] Login succeeded but authentication state not set properly');
        }
        
        return response;
      } catch (error) {
        console.error('[AuthStore] Login failed:', error);
        // Clear state on error
        this.user = null;
        this.isAuthenticated = false;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async logout() {
      try {
        await authService.logout();
      } finally {
        this.user = null;
        this.isAuthenticated = false;
      }
    },

    async checkAuth() {
      try {
        // Wrap in try-catch to ensure it never throws and blocks render
        const hasToken = authService.isAuthenticated();
        console.log('[AuthStore] Checking auth, hasToken:', hasToken);
        
        if (hasToken) {
          const user = authService.getCurrentUser();
          if (user) {
            this.user = user;
            this.isAuthenticated = true;
            console.log('[AuthStore] Auth check: authenticated as', user.email);
          } else {
            // Token exists but no user data, clear auth state
            console.warn('[AuthStore] Token exists but no user data, clearing auth state');
            this.user = null;
            this.isAuthenticated = false;
          }
        } else {
          this.user = null;
          this.isAuthenticated = false;
          console.log('[AuthStore] Auth check: not authenticated');
        }
      } catch (error) {
        console.error('[AuthStore] Check auth error:', error);
        // Ensure state is set even on error to prevent blocking
        this.user = null;
        this.isAuthenticated = false;
      }
    },

    setUser(user) {
      this.user = user;
      this.isAuthenticated = !!user;
    },
  },
});

