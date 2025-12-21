/**
 * Auth Store
 * Manages authentication state and tokens
 */
import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') || localStorage.getItem('auth_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    user: null,
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  
  actions: {
    setToken(token) {
      this.token = token;
      localStorage.setItem('access_token', token);
    },
    
    setRefreshToken(refreshToken) {
      this.refreshToken = refreshToken;
      localStorage.setItem('refresh_token', refreshToken);
    },
    
    setUser(user) {
      this.user = user;
    },
    
    logout() {
      this.token = null;
      this.refreshToken = null;
      this.user = null;
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('auth_token');
    },
    
    // Initialize from localStorage
    init() {
      this.token = localStorage.getItem('access_token') || localStorage.getItem('auth_token') || null;
      this.refreshToken = localStorage.getItem('refresh_token') || null;
    },
  },
});
