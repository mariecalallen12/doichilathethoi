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

export const supportApi = {
  async getArticles(params = {}) {
    try {
      const response = await api.get('/support/articles', { params });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch articles');
      }
      throw error;
    }
  },

  async getArticleById(articleId) {
    try {
      const response = await api.get(`/support/articles/${articleId}`);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch article');
      }
      throw error;
    }
  },

  async getCategories() {
    try {
      const response = await api.get('/support/categories');
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch categories');
      }
      throw error;
    }
  },

  async searchArticles(query) {
    try {
      const response = await api.post('/support/search', { query });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to search articles');
      }
      throw error;
    }
  },

  async submitContact(formData) {
    try {
      const response = await api.post('/support/contact', formData);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to submit contact form');
      }
      throw error;
    }
  },

  async getOffices() {
    try {
      const response = await api.get('/support/offices');
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch offices');
      }
      throw error;
    }
  },

  async getChannels() {
    try {
      const response = await api.get('/support/channels');
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch channels');
      }
      throw error;
    }
  },

  async getFaq(category = null) {
    try {
      const url = category ? `/support/faq/${category}` : '/support/faq';
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch FAQ');
      }
      throw error;
    }
  },

  async searchFaq(query) {
    try {
      const response = await api.post('/support/faq/search', { query });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to search FAQ');
      }
      throw error;
    }
  }
};

