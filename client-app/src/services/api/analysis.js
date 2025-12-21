import axios from 'axios';
import { getApiBaseUrl } from '../../utils/runtimeConfig';
import { tradingFeaturesApi } from './tradingSystem';

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
      // Use TradingSystemAPI binary-array as sentiment indicator
      const response = await tradingFeaturesApi.getBinaryArray();
      return response.data || response;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch sentiment');
      }
      throw error;
    }
  },

  async getSignals(params = {}) {
    try {
      // Call TradingSystemAPI signals endpoint
      const response = await tradingFeaturesApi.getAllSignals();
      return response.data || response;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch signals');
      }
      throw error;
    }
  },

  async getSignalForSymbol(symbol) {
    try {
      const response = await tradingFeaturesApi.getSignalForSymbol(symbol);
      return response.data || response;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch signal');
      }
      throw error;
    }
  },

  async getBinaryArray() {
    try {
      const response = await tradingFeaturesApi.getBinaryArray();
      return response.data || response;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch binary array');
      }
      throw error;
    }
  },

  async getMarketAnalysis() {
    try {
      const response = await tradingFeaturesApi.getMarketAnalysis();
      return response.data || response;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch market analysis');
      }
      throw error;
    }
  },

  async getRecommendations(symbols = []) {
    try {
      const response = await tradingFeaturesApi.getRecommendations();
      return response.data || response;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch recommendations');
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

