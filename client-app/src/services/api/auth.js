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

// Handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token: newRefreshToken } = response.data;
          localStorage.setItem('auth_token', access_token);
          if (newRefreshToken) {
            localStorage.setItem('refresh_token', newRefreshToken);
          }

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.removeItem('auth_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export const authApi = {
  /**
   * User registration
   * @param {Object} userData - Registration data
   * @returns {Promise} Registration response
   */
  async register(userData) {
    try {
      // Map frontend fields to backend format
      const registerData = {
        email: userData.email || null,
        password: userData.password,
        displayName: userData.fullName || userData.displayName || userData.phone,
        phoneNumber: userData.phone,
        customId: userData.customId || null,
        referralCode: userData.referralCode,
        agreeToTerms: userData.agreeTerms || false
      };
      
      const response = await api.post('/auth/register', registerData);
      // Handle nested response structure
      if (response.data.data) {
        return {
          ...response.data.data,
          success: response.data.success,
          message: response.data.message,
          needsApproval: response.data.needsApproval
        };
      }
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Registration failed');
      }
      throw error;
    }
  },

  /**
   * User login
   * @param {Object} credentials - Login credentials (phone/email, password, device_info)
   * @returns {Promise} Login response with tokens
   */
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
      // Preserve original axios error so callers can inspect error.response (status, data)
      throw error;
    }
  },

  /**
   * Refresh access token
   * @param {string} refreshToken - Refresh token
   * @returns {Promise} New tokens
   */
  async refreshToken(refreshToken) {
    try {
      // Use Authorization header instead of body
      const response = await api.post('/auth/refresh', {}, {
        headers: {
          Authorization: `Bearer ${refreshToken}`
        }
      });
      // Handle nested response structure
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
        throw new Error(error.response.data.detail || 'Token refresh failed');
      }
      throw error;
    }
  },

  /**
   * User logout
   * @returns {Promise} Logout response
   */
  async logout() {
    try {
      const response = await api.post('/auth/logout');
      // Clear local storage
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('remember_me');
      return response.data;
    } catch (error) {
      // Clear local storage even if API call fails
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('remember_me');
      if (error.response) {
        throw new Error(error.response.data.detail || 'Logout failed');
      }
      throw error;
    }
  },

  /**
   * Request password reset
   * @param {string} email - User email
   * @returns {Promise} Reset request response
   */
  async forgotPassword(email) {
    try {
      const response = await api.post('/auth/forgot-password', { email });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Password reset request failed');
      }
      throw error;
    }
  },

  /**
   * Reset password with token
   * @param {Object} resetData - Reset data (token, new_password)
   * @returns {Promise} Reset response
   */
  async resetPassword(resetData) {
    try {
      const response = await api.post('/auth/reset-password', resetData);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Password reset failed');
      }
      throw error;
    }
  },

  /**
   * Verify email with token
   * @param {string} token - Verification token
   * @returns {Promise} Verification response
   */
  async verifyEmail(token) {
    try {
      const response = await api.post('/auth/verify', { token });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Email verification failed');
      }
      throw error;
    }
  },

  /**
   * Get current user profile
   * @returns {Promise} User profile
   */
  async getProfile() {
    try {
      const response = await api.get('/client/profile');
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch profile');
      }
      throw error;
    }
  },

  /**
   * Check if user is authenticated
   * @returns {boolean} Authentication status
   */
  isAuthenticated() {
    return !!localStorage.getItem('auth_token');
  },

  /**
   * Get stored auth token
   * @returns {string|null} Auth token
   */
  getToken() {
    return localStorage.getItem('auth_token');
  },

  /**
   * Get registration fields configuration
   * @param {number} currentVersion - Current version to compare (optional)
   * @returns {Promise} Registration fields configuration
   */
  async getRegistrationFieldsConfig(currentVersion = null) {
    try {
      // Add cache-busting query parameter with timestamp
      const timestamp = Date.now();
      const url = currentVersion 
        ? `/client/settings/registration-fields?t=${timestamp}&v=${currentVersion}`
        : `/client/settings/registration-fields?t=${timestamp}`;
      
      const response = await api.get(url, {
        // Prevent caching
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        }
      });
      
      // Backend returns: { success: true, data: { fields: [...], version: ..., updated_at: ... } }
      // Axios wraps it in response.data, so:
      // response.data = { success: true, data: { fields: [...] } }
      // response.data.data = { fields: [...] }
      
      let config = null;
      if (response.data && response.data.data) {
        // Nested structure: response.data.data = { fields: [...], version: ..., updated_at: ... }
        config = response.data.data;
      } else if (response.data && response.data.fields) {
        // Direct structure: response.data = { fields: [...] }
        config = response.data;
      } else if (response.data) {
        config = response.data;
      } else {
        config = response;
      }
      
      return config;
    } catch (error) {
      // Fallback to default config if API fails
      console.warn('Failed to fetch registration fields config, using default:', error);
      // Return null to indicate fallback needed
      return null;
    }
  },
};

export default authApi;
