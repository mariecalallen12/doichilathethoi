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

export const legalApi = {
  async getTerms(version = null) {
    try {
      const url = version ? `/legal/terms/version/${version}` : '/legal/terms';
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch terms');
      }
      throw error;
    }
  },

  async getPrivacy(version = null) {
    try {
      const url = version ? `/legal/privacy/version/${version}` : '/legal/privacy';
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch privacy policy');
      }
      throw error;
    }
  },

  async getRiskWarning() {
    try {
      const response = await api.get('/legal/risk-warning');
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch risk warning');
      }
      throw error;
    }
  },

  async submitComplaint(complaintData) {
    try {
      const formData = new FormData();
      Object.keys(complaintData).forEach(key => {
        if (key === 'files' && Array.isArray(complaintData[key])) {
          complaintData[key].forEach((file, index) => {
            formData.append(`files`, file);
          });
        } else {
          formData.append(key, complaintData[key]);
        }
      });
      
      const response = await api.post('/legal/complaints', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to submit complaint');
      }
      throw error;
    }
  },

  async getComplaints() {
    try {
      const response = await api.get('/legal/complaints');
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch complaints');
      }
      throw error;
    }
  },

  async getComplaintById(complaintId) {
    try {
      const response = await api.get(`/legal/complaints/${complaintId}`);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch complaint');
      }
      throw error;
    }
  },

  async updateComplaint(complaintId, updateData) {
    try {
      const response = await api.put(`/legal/complaints/${complaintId}`, updateData);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to update complaint');
      }
      throw error;
    }
  }
};

