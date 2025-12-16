import axios from 'axios';
import { getApiBaseUrl } from '../../utils/runtimeConfig';

const API_BASE_URL = getApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const indicatorsApi = {
  async getIndicators(country = null) {
    try {
      const response = await api.get('/market/indicators', {
        params: country ? { country } : {},
      });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch indicators');
      }
      // No mock data - throw error instead
      throw new Error('Failed to fetch indicators: Network error');
    }
  },

  async getIndicatorById(id) {
    try {
      const response = await api.get(`/market/indicators/${id}`);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch indicator');
      }
      throw error;
    }
  },
};

