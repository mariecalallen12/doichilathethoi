import { defineStore } from 'pinia';
import api from '../services/api';

export const useUserStore = defineStore('user', {
  state: () => ({
    users: [],
    currentUser: null,
    loading: false,
    pagination: {
      page: 1,
      limit: 50,
      total: 0,
    },
    filters: {
      search: '',
      status: 'all',
      sortBy: 'created_at',
      sortOrder: 'desc',
    },
  }),

  getters: {
    filteredUsers: (state) => {
      let filtered = [...state.users];

      // Search filter
      if (state.filters.search) {
        const search = state.filters.search.toLowerCase();
        filtered = filtered.filter(
          (user) =>
            user.email?.toLowerCase().includes(search) ||
            user.full_name?.toLowerCase().includes(search) ||
            user.phone?.includes(search)
        );
      }

      // Status filter
      if (state.filters.status !== 'all') {
        filtered = filtered.filter((user) => user.status === state.filters.status);
      }

      // Sort
      filtered.sort((a, b) => {
        const aVal = a[state.filters.sortBy];
        const bVal = b[state.filters.sortBy];
        if (state.filters.sortOrder === 'asc') {
          return aVal > bVal ? 1 : -1;
        }
        return aVal < bVal ? 1 : -1;
      });

      return filtered;
    },
  },

  actions: {
    async fetchUsers(params = {}) {
      this.loading = true;
      try {
        const queryParams = {
          ...this.pagination,
          ...this.filters,
          ...params,
        };
        const response = await api.get('/api/admin/users', queryParams);
        
        // Handle nested response structure
        const data = response.data || response;
        
        if (data.users) {
          this.users = data.users;
        } else if (Array.isArray(data)) {
          this.users = data;
        }
        
        if (data.pagination) {
          this.pagination = { ...this.pagination, ...data.pagination };
        } else if (data.total !== undefined) {
          this.pagination.total = data.total;
        }
        
        return response;
      } catch (error) {
        console.error('Fetch users error:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchUserById(userId) {
      this.loading = true;
      try {
        const response = await api.get(`/api/admin/users/${userId}`);
        
        // Handle nested response structure
        const data = response.data || response;
        this.currentUser = data.user || data;
        
        return response;
      } catch (error) {
        console.error('Fetch user error:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async updateUser(userId, data) {
      try {
        const response = await api.put(`/api/admin/users/${userId}`, data);
        
        // Handle nested response structure
        const updatedUser = response.data?.user || response.user || response;
        
        const index = this.users.findIndex((u) => u.id === userId);
        if (index !== -1) {
          this.users[index] = { ...this.users[index], ...updatedUser };
        }
        
        // Update currentUser if it's the same user
        if (this.currentUser && this.currentUser.id === userId) {
          this.currentUser = { ...this.currentUser, ...updatedUser };
        }
        
        return response;
      } catch (error) {
        console.error('Update user error:', error);
        throw error;
      }
    },

    async updateUserStatus(userId, status) {
      return this.updateUser(userId, { status });
    },

    async bulkUpdateStatus(userIds, status) {
      try {
        const response = await api.post('/api/admin/users/bulk-update', {
          user_ids: userIds,
          status,
        });
        // Refresh users list
        await this.fetchUsers();
        return response;
      } catch (error) {
        console.error('Bulk update error:', error);
        throw error;
      }
    },

    setFilters(filters) {
      this.filters = { ...this.filters, ...filters };
    },

    setPagination(pagination) {
      this.pagination = { ...this.pagination, ...pagination };
    },
  },
});

