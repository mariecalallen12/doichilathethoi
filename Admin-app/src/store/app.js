import { defineStore } from 'pinia';
import api from '../services/api';

export const useAppStore = defineStore('app', {
  state: () => ({
    sidebarOpen: true,
    theme: 'dark',
    notifications: [],
    settings: {
      platformName: 'CMEETRADING',
      platformURL: 'https://digitalutopia.com',
      supportEmail: 'support@digitalutopia.com',
      timezone: 'UTC',
      defaultLanguage: 'en',
      maintenanceMode: false,
      allowRegistrations: true,
    },
  }),

  getters: {
    isSidebarOpen: (state) => state.sidebarOpen,
  },

  actions: {
    toggleSidebar() {
      this.sidebarOpen = !this.sidebarOpen;
    },

    setSidebarOpen(open) {
      this.sidebarOpen = open;
    },

    setTheme(theme) {
      this.theme = theme;
    },

    async fetchSettings() {
      try {
        const response = await api.get('/api/admin/settings');
        const data = response.data?.data || response.data || {};
        this.settings = { ...this.settings, ...data };
      } catch (error) {
        console.error('Fetch settings error:', error);
        // Keep existing settings on error
      }
    },

    async updateSettings(settings) {
      try {
        await api.put('/api/admin/settings', settings);
      this.settings = { ...this.settings, ...settings };
      } catch (error) {
        console.error('Update settings error:', error);
        throw error;
      }
    },
  },
});

