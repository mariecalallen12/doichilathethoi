/**
 * Notifications Store
 * Quản lý notification state và operations
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';
import { getApiBaseUrl } from '../utils/runtimeConfig';
import { success as showSuccessToast, error as showErrorToast } from '../services/utils/toast';

const API_BASE_URL = getApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token') || localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const useNotificationsStore = defineStore('notifications', () => {
  const notifications = ref([]);
  const unreadCount = ref(0);
  const isLoading = ref(false);
  const error = ref(null);
  const preferences = ref({});

  // Computed
  const unreadNotifications = computed(() => {
    return notifications.value.filter(n => !n.is_read && !n.is_dismissed && !n.is_expired);
  });

  const alerts = computed(() => {
    return notifications.value.filter(n => n.type === 'alert' && !n.is_dismissed && !n.is_expired);
  });

  const criticalAlerts = computed(() => {
    return alerts.value.filter(n => n.severity === 'high' || n.severity === 'critical');
  });

  /**
   * Fetch notifications
   */
  async function fetchNotifications(options = {}) {
    const {
      unreadOnly = false,
      category = null,
      limit = 50,
      skip = 0,
    } = options;

    isLoading.value = true;
    error.value = null;

    try {
      const params = {
        skip,
        limit,
        unread_only: unreadOnly,
      };
      if (category) {
        params.category = category;
      }

      const response = await api.get('/notifications', { params });
      const data = response.data;

      if (skip === 0) {
        // Replace notifications if first page
        notifications.value = data.notifications || [];
      } else {
        // Append if pagination
        notifications.value.push(...(data.notifications || []));
      }

      unreadCount.value = data.unread_count || 0;

      return data;
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to fetch notifications';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Fetch unread count
   */
  async function fetchUnreadCount(category = null) {
    try {
      const params = category ? { category } : {};
      const response = await api.get('/notifications/unread-count', { params });
      unreadCount.value = response.data.unread_count || 0;
      return unreadCount.value;
    } catch (err) {
      console.error('Error fetching unread count:', err);
      return 0;
    }
  }

  /**
   * Mark notification as read
   */
  async function markAsRead(notificationId) {
    try {
      const response = await api.post(`/notifications/${notificationId}/read`);
      const updated = response.data;

      // Update in local state
      const index = notifications.value.findIndex(n => n.id === notificationId);
      if (index !== -1) {
        notifications.value[index] = updated;
      }

      // Update unread count
      if (updated.is_read && !notifications.value[index]?.is_read) {
        unreadCount.value = Math.max(0, unreadCount.value - 1);
      }

      return updated;
    } catch (err) {
      const message = err.response?.data?.detail || err.message || 'Failed to mark as read';
      showErrorToast(message);
      throw err;
    }
  }

  /**
   * Mark all notifications as read
   */
  async function markAllAsRead(category = null) {
    try {
      const params = category ? { category } : {};
      const response = await api.post('/notifications/mark-all-read', null, { params });
      const count = response.data.marked_count || 0;

      // Update local state
      notifications.value.forEach(n => {
        if (!n.is_read && (!category || n.category === category)) {
          n.is_read = true;
          n.read_at = new Date().toISOString();
        }
      });

      // Update unread count
      unreadCount.value = Math.max(0, unreadCount.value - count);

      showSuccessToast(`Marked ${count} notification(s) as read`);
      return count;
    } catch (err) {
      const message = err.response?.data?.detail || err.message || 'Failed to mark all as read';
      showErrorToast(message);
      throw err;
    }
  }

  /**
   * Dismiss notification
   */
  async function dismissNotification(notificationId) {
    try {
      const response = await api.post(`/notifications/${notificationId}/dismiss`);
      const updated = response.data;

      // Update in local state
      const index = notifications.value.findIndex(n => n.id === notificationId);
      if (index !== -1) {
        notifications.value[index] = updated;
      }

      return updated;
    } catch (err) {
      const message = err.response?.data?.detail || err.message || 'Failed to dismiss notification';
      showErrorToast(message);
      throw err;
    }
  }

  /**
   * Add notification to local state (for real-time updates)
   */
  function addNotification(notification) {
    // Check if already exists
    const exists = notifications.value.find(n => n.id === notification.id);
    if (!exists) {
      notifications.value.unshift(notification);
      
      // Update unread count if unread
      if (!notification.is_read && !notification.is_dismissed) {
        unreadCount.value++;
      }
    }
  }

  /**
   * Fetch notification preferences
   */
  async function fetchPreferences() {
    try {
      const response = await api.get('/notification-preferences');
      const prefs = {};
      response.data.forEach(p => {
        prefs[p.category] = {
          email_enabled: p.email_enabled,
          in_app_enabled: p.in_app_enabled,
          push_enabled: p.push_enabled,
          webhook_url: p.webhook_url,
        };
      });
      preferences.value = prefs;
      return prefs;
    } catch (err) {
      console.error('Error fetching preferences:', err);
      return {};
    }
  }

  /**
   * Update notification preference
   */
  async function updatePreference(category, preferenceData) {
    try {
      const response = await api.put(`/notification-preferences/${category}`, preferenceData);
      const updated = response.data;

      // Update local state
      preferences.value[category] = {
        email_enabled: updated.email_enabled,
        in_app_enabled: updated.in_app_enabled,
        push_enabled: updated.push_enabled,
        webhook_url: updated.webhook_url,
      };

      showSuccessToast('Notification preferences updated');
      return updated;
    } catch (err) {
      const message = err.response?.data?.detail || err.message || 'Failed to update preferences';
      showErrorToast(message);
      throw err;
    }
  }

  /**
   * Initialize store
   */
  async function initialize() {
    try {
      await Promise.all([
        fetchNotifications({ limit: 20 }),
        fetchUnreadCount(),
        fetchPreferences(),
      ]);
    } catch (err) {
      console.error('Error initializing notifications store:', err);
    }
  }

  return {
    // State
    notifications,
    unreadCount,
    isLoading,
    error,
    preferences,
    
    // Computed
    unreadNotifications,
    alerts,
    criticalAlerts,
    
    // Actions
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    dismissNotification,
    addNotification,
    fetchPreferences,
    updatePreference,
    initialize,
  };
});

