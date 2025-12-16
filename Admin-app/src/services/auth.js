import api from './api';

class AuthService {
  async login(credentials) {
    try {
      console.log('[Auth] Attempting login for:', credentials.email);
      
      // API client returns data directly (not response.data)
      const responseData = await api.post('/api/auth/login', credentials);
      
      console.log('[Auth] Login response received:', {
        hasData: !!responseData.data,
        hasAccessToken: !!responseData.access_token,
        success: responseData.success
      });
      
      // Handle nested response structure from backend: {success, message, data: {...}}
      // Backend returns: {success: true, message: "...", data: {access_token, refresh_token, user, ...}}
      let tokenData, userData;
      
      if (responseData.data && typeof responseData.data === 'object') {
        // Nested structure: {success, message, data: {...}}
        tokenData = responseData.data;
        userData = responseData.data.user;
        console.log('[Auth] Using nested response structure');
      } else if (responseData.access_token) {
        // Flat structure: {access_token, refresh_token, user, ...}
        tokenData = responseData;
        userData = responseData.user;
        console.log('[Auth] Using flat response structure');
      } else {
        // Unexpected structure
        console.error('[Auth] Unexpected login response structure:', responseData);
        throw new Error('Cấu trúc response không hợp lệ từ server');
      }
      
      // Store tokens
      if (tokenData.access_token) {
        localStorage.setItem('access_token', tokenData.access_token);
        if (tokenData.refresh_token) {
          localStorage.setItem('refresh_token', tokenData.refresh_token);
        }
        if (userData) {
          localStorage.setItem('user', JSON.stringify(userData));
          console.log('[Auth] User data stored:', { email: userData.email, role: userData.role });
        }
        console.log('[Auth] Tokens stored successfully');
      } else {
        console.error('[Auth] No access token in response');
        throw new Error('Không nhận được token từ server');
      }
      
      return {
        access_token: tokenData.access_token,
        refresh_token: tokenData.refresh_token,
        user: userData,
        success: responseData.success !== undefined ? responseData.success : true,
        message: responseData.message || 'Đăng nhập thành công'
      };
    } catch (error) {
      console.error('[Auth] Login error:', error);
      // Re-throw with better error message
      if (error.message) {
        throw error;
      }
      throw new Error('Đăng nhập thất bại. Vui lòng thử lại.');
    }
  }

  async logout() {
    try {
      await api.post('/api/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  }

  async refreshToken() {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) throw new Error('No refresh token');
      
      // Use Authorization header instead of body
      const response = await api.post('/api/auth/refresh', {}, {
        headers: {
          Authorization: `Bearer ${refreshToken}`
        }
      });
      
      // Handle nested response structure
      const data = response.data.data || response.data;
      
      if (data.access_token) {
        localStorage.setItem('access_token', data.access_token);
      }
      
      return {
        ...data,
        success: response.data.success,
        message: response.data.message
      };
    } catch (error) {
      console.error('Refresh token error:', error);
      this.logout();
      throw error;
    }
  }

  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  }

  getCurrentUser() {
    try {
      const userStr = localStorage.getItem('user');
      if (!userStr) return null;
      return JSON.parse(userStr);
    } catch (error) {
      console.error('Error parsing user from localStorage:', error);
      // Clear invalid user data
      localStorage.removeItem('user');
      return null;
    }
  }

  getToken() {
    return localStorage.getItem('access_token');
  }

  hasPermission(permission) {
    const user = this.getCurrentUser();
    if (!user || !user.permissions) return false;
    return user.permissions.includes(permission) || user.role === 'SUPER_ADMIN';
  }

  hasRole(role) {
    const user = this.getCurrentUser();
    return user?.role === role || user?.role === 'SUPER_ADMIN';
  }
}

export default new AuthService();

