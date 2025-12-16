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

export const educationApi = {
  async getVideos(params = {}) {
    try {
      const response = await api.get('/education/videos', { params });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch videos');
      }
      throw error;
    }
  },

  async getVideoById(videoId) {
    try {
      const response = await api.get(`/education/videos/${videoId}`);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch video');
      }
      throw error;
    }
  },

  async getEbooks(params = {}) {
    try {
      const response = await api.get('/education/ebooks', { params });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch ebooks');
      }
      throw error;
    }
  },

  async getEbookById(ebookId) {
    try {
      const response = await api.get(`/education/ebooks/${ebookId}`);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch ebook');
      }
      throw error;
    }
  },

  async getCalendar(startDate, endDate) {
    try {
      const params = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      const response = await api.get('/education/calendar', { params });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch calendar');
      }
      throw error;
    }
  },

  async getReports(params = {}) {
    try {
      const response = await api.get('/education/reports', { params });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch reports');
      }
      throw error;
    }
  },

  async getReportById(reportId) {
    try {
      const response = await api.get(`/education/reports/${reportId}`);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch report');
      }
      throw error;
    }
  },

  async updateProgress(itemId, itemType, progressData) {
    try {
      const response = await api.post('/education/progress', {
        item_id: itemId,
        item_type: itemType,
        ...progressData
      });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to update progress');
      }
      throw error;
    }
  }
};

