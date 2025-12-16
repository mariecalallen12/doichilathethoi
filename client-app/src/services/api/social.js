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

export const socialApi = {
  async getFeed(symbol = null, limit = 10) {
    try {
      // Use the correct endpoint: /trading/social-signals
      const params = { limit };
      if (symbol) {
        params.symbol = symbol;
      }
      const response = await api.get('/trading/social-signals', { params });
      
      // Transform response to match expected format
      if (response.data && response.data.signals) {
        return {
          success: true,
          feed: response.data.signals,
          total: response.data.total
        };
      }
      return response.data;
    } catch (error) {
      // Return empty feed instead of throwing to prevent page crash
      console.warn('Social feed API error:', error.message);
      return { 
        success: false, 
        feed: [],
        total: 0,
        error: error.message 
      };
    }
  },

  async getRankings() {
    try {
      const response = await api.get('/trading/social/rankings');
      return response.data;
    } catch (error) {
      console.warn('Rankings API not available');
      return { rankings: [] };
    }
  },

  async likePost(postId) {
    try {
      const response = await api.post(`/trading/social/posts/${postId}/like`);
      return response.data;
    } catch (error) {
      console.warn('Like post API not available');
      return { likes: 0 };
    }
  },

  async commentPost(postId, data) {
    try {
      const response = await api.post(`/trading/social/posts/${postId}/comment`, data);
      return response.data;
    } catch (error) {
      console.warn('Comment post API not available');
      return { comments: 0 };
    }
  },
};

