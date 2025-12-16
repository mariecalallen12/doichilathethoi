import axios from 'axios';
import { getApiBaseUrl } from '../../utils/runtimeConfig';

const API_BASE_URL = getApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const newsApi = {
  async getNews(filters = {}) {
    try {
      const response = await api.get('/market/news', {
        params: filters,
      });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch news');
      }
      // No mock data - throw error instead
      throw new Error('Failed to fetch news: Network error');
    }
  },

  async getNewsById(id) {
    try {
      const response = await api.get(`/market/news/${id}`);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch news item');
      }
      throw error;
    }
  },
};

