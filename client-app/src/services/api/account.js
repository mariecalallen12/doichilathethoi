import axios from 'axios';
import { getApiBaseUrl } from '../../utils/runtimeConfig';

const API_BASE_URL = getApiBaseUrl();

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

export const accountApi = {
  async login(credentials) {
    try {
      const response = await api.post('/auth/login', credentials);
      // Handle nested response structure from backend
      if (response.data.data) {
        return {
          ...response.data.data,
          success: response.data.success,
          message: response.data.message
        };
      }
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Login failed');
      }
      throw error;
    }
  },
  
  // Note: Use authApi from services/api/auth.js for full authentication features

  async getBalance() {
    try {
      const response = await api.get('/financial/balance');
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch balance');
      }
      throw error;
    }
  },

  async deposit(data) {
    try {
      const response = await api.post('/financial/deposit', data);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to deposit');
      }
      throw error;
    }
  },

  async withdraw(data) {
    try {
      const response = await api.post('/financial/withdraw', data);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to withdraw');
      }
      throw error;
    }
  },

  async getTransactionHistory(filters = {}) {
    try {
      const response = await api.get('/financial/transactions', { params: filters });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch transaction history');
      }
      throw error;
    }
  },
};
