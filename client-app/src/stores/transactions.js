import { defineStore } from 'pinia';
import { ref } from 'vue';
import { clientApi } from '../services/api/client';
import websocketService from '../services/websocket';
import { useWebSocketStore } from './websocket';
import { getWsBaseUrl } from '../utils/runtimeConfig';
import axios from 'axios';
import { getApiBaseUrl } from '../utils/runtimeConfig';

const API_BASE_URL = getApiBaseUrl();

// Giữ lại instance api cũ cho export /financial/transactions/export nếu backend đã hỗ trợ
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const useTransactionsStore = defineStore('transactions', () => {
  const transactions = ref([]);
  const deposits = ref([]);
  const withdrawals = ref([]);
  const orders = ref([]);
  const isLoading = ref(false);
  const error = ref(null);
  const pagination = ref({
    page: 1,
    limit: 50,
    total: 0,
  });

  async function fetchTransactions(filters = {}) {
    isLoading.value = true;
    error.value = null;

    try {
      const params = {
        ...filters,
        page: filters.page || pagination.value.page,
        limit: filters.limit || pagination.value.limit,
      };

      // Ưu tiên dùng clientApi.getTransactions (module client),
      // fallback sang /api/financial/transactions nếu cần.
      let data;
      try {
        const clientResponse = await clientApi.getTransactions(params);
        data = clientResponse;
      } catch {
        const response = await api.get('/financial/transactions', { params });
        data = response.data;
      }

      const payload = data.data || data;

      if (payload.transactions) {
        transactions.value = payload.transactions;
      } else if (Array.isArray(payload)) {
        transactions.value = payload;
      } else if (Array.isArray(payload.items)) {
        transactions.value = payload.items;
      } else {
        transactions.value = [];
      }

      if (payload.pagination?.total !== undefined) {
        pagination.value.total = payload.pagination.total;
      } else if (payload.total !== undefined) {
        pagination.value.total = payload.total;
      } else if (payload.count !== undefined) {
        pagination.value.total = payload.count;
      }

      // Separate by type
      deposits.value = transactions.value.filter(t => t.type === 'deposit' || t.transaction_type === 'deposit');
      withdrawals.value = transactions.value.filter(t => t.type === 'withdrawal' || t.transaction_type === 'withdrawal');
      
      return data;
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to fetch transactions';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function exportTransactions(format = 'csv', filters = {}) {
    isLoading.value = true;
    error.value = null;

    try {
      const params = {
        ...filters,
        format,
      };
      const response = await api.get('/financial/transactions/export', {
        params,
        responseType: 'blob',
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `transactions.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      return response.data;
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to export transactions';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // WebSocket integration for real-time transaction updates
  function setupWebSocketListeners() {
    if (typeof window === 'undefined') return;
    
    // Ensure WebSocket is connected
    const wsStore = useWebSocketStore();
    const wsUrl = getWsBaseUrl();
    if (!wsStore.isConnected) {
      wsStore.connect(wsUrl);
    }
    
    // Listen for transaction updates
    websocketService.subscribe('transactions', (message) => {
      const data = message.data || message;
      if (data.transaction) {
        // Add or update transaction
        const index = transactions.value.findIndex(t => t.id === data.transaction.id);
        if (index >= 0) {
          transactions.value[index] = { ...transactions.value[index], ...data.transaction };
        } else {
          transactions.value.unshift(data.transaction);
        }
        
        // Update pagination total if needed
        if (data.transaction.status === 'completed' || data.transaction.status === 'pending') {
          pagination.value.total = (pagination.value.total || 0) + 1;
        }
        
        // Update separated lists
        if (data.transaction.type === 'deposit' || data.transaction.transaction_type === 'deposit') {
          const depositIndex = deposits.value.findIndex(d => d.id === data.transaction.id);
          if (depositIndex >= 0) {
            deposits.value[depositIndex] = data.transaction;
          } else {
            deposits.value.unshift(data.transaction);
          }
        } else if (data.transaction.type === 'withdrawal' || data.transaction.transaction_type === 'withdrawal') {
          const withdrawalIndex = withdrawals.value.findIndex(w => w.id === data.transaction.id);
          if (withdrawalIndex >= 0) {
            withdrawals.value[withdrawalIndex] = data.transaction;
          } else {
            withdrawals.value.unshift(data.transaction);
          }
        }
      }
    });
  }

  // Setup WebSocket on store initialization
  if (typeof window !== 'undefined') {
    setupWebSocketListeners();
  }

  return {
    transactions,
    deposits,
    withdrawals,
    orders,
    isLoading,
    error,
    pagination,
    fetchTransactions,
    exportTransactions,
    setupWebSocketListeners,
  };
});
