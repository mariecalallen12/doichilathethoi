import axios from 'axios';
import { getApiBaseUrl } from '../../utils/runtimeConfig';

const API_BASE_URL = getApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const analysisApi = {
  async getTechnicalAnalysis(symbol) {
    try {
      const response = await api.get(`/analysis/technical/${symbol}`);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch technical analysis');
      }
      throw error;
    }
  },

  async getFundamentalAnalysis(symbol) {
    try {
      const response = await api.get(`/analysis/fundamental/${symbol}`);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch fundamental analysis');
      }
      throw error;
    }
  },

  async getSentiment() {
    try {
      const response = await api.get('/analysis/sentiment');
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch sentiment');
      }
      throw error;
    }
  },

  async getSignals(params = {}) {
    try {
      const response = await api.get('/analysis/signals', { params });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch signals');
      }
      throw error;
    }
  },

  async runBacktest(backtestData) {
    try {
      const response = await api.post('/analysis/backtest', backtestData);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to run backtest');
      }
      throw error;
    }
  }
};

