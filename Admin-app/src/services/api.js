// API Client with interceptors
// Smart API base URL detection with production-first logic
const getApiBaseUrl = () => {
  // Always check window.location first for runtime detection (more reliable)
  if (typeof window !== 'undefined') {
    const protocol = window.location.protocol;
    const hostname = window.location.hostname;
    const port = window.location.port;
    
    // Priority 1: For production domains, always use same origin (most reliable)
    // This ensures production builds work correctly even if env var is misconfigured
    const productionDomains = ['cmeetrading.com', 'digitalutopia.com', 'api.digitalutopia.com'];
    const isProductionDomain = productionDomains.some(domain => 
      hostname === domain || hostname.endsWith('.' + domain)
    );
    
    if (isProductionDomain) {
      // Use same origin for production - API should be on same domain or subdomain
      const baseUrl = `${protocol}//${hostname}`;
      console.log('[API] Using production domain base URL:', baseUrl);
      return baseUrl;
    }
    
    // Priority 2: For localhost, use localhost:8000
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'http://localhost:8000';
    }
    
    // Priority 3: Check build-time env var (only if not production domain)
    const envUrl = import.meta.env.VITE_API_BASE_URL;
    if (envUrl) {
      // Ignore localhost env on non-localhost hosts (avoid prod CORS)
      if (envUrl.includes('localhost') && hostname !== 'localhost' && hostname !== '127.0.0.1') {
        return `${protocol}//${hostname}`;
      }
      // Validate env URL - reject localhost in production
      if (envUrl.includes('localhost') && !isProductionDomain) {
        // Only use localhost env var if we're actually on localhost
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
          const baseUrl = envUrl.replace(/\/api\/?$/, '');
          console.log('[API] Using env var base URL (localhost):', baseUrl);
          return baseUrl;
        } else {
          // Ignore localhost env var in production, use same origin instead
          console.warn('[API] Ignoring localhost env var in production, using same origin');
          return `${protocol}//${hostname}`;
        }
      } else {
        // Use env var if it's not localhost
        const baseUrl = envUrl.replace(/\/api\/?$/, '');
        console.log('[API] Using env var base URL:', baseUrl);
        return baseUrl;
      }
    }
    
    // Priority 4: For reverse proxy setup (standard ports), use same origin
    if (!port || port === '80' || port === '443' || port === '8080') {
      return `${protocol}//${hostname}${port && port !== '80' && port !== '443' ? `:${port}` : ''}`;
    }
    
    // Priority 5: For production/docker, use same origin (no port)
    return `${protocol}//${hostname}`;
  }
  
  // Fallback for SSR or non-browser environments - use current origin if available
  if (typeof window !== 'undefined' && window.location) {
    return `${window.location.protocol}//${window.location.hostname}`;
  }
  return 'http://localhost:8000';
};

// Make baseURL dynamic - recalculate on each request to handle runtime changes
const getDynamicApiBaseUrl = () => getApiBaseUrl();

class ApiClient {
  constructor() {
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
  }

  // Always get fresh baseURL dynamically to handle runtime changes
  get baseURL() {
    return getDynamicApiBaseUrl();
  }

  async request(endpoint, options = {}) {
    // Get current baseURL for this request
    const baseURL = this.baseURL;
    const url = `${baseURL}${endpoint}`;
    const token = localStorage.getItem('access_token');
    
    const config = {
      ...options,
      headers: {
        ...this.defaultHeaders,
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      // Handle non-JSON responses
      const contentType = response.headers.get('content-type');
      const data = contentType?.includes('application/json')
        ? await response.json()
        : await response.text();

      if (!response.ok) {
        // Handle 401 Unauthorized
        if (response.status === 401) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/admin/login';
          throw new Error('Unauthorized');
        }
        
        // Handle 429 Rate Limit
        if (response.status === 429) {
          const rateLimitMessage = typeof data === 'object' && data !== null && data.message 
            ? data.message 
            : 'Quá nhiều yêu cầu. Vui lòng thử lại sau vài giây.';
          const error = new Error(rateLimitMessage);
          error.status = 429;
          error.data = data;
          throw error;
        }
        
        // Handle other error responses from backend
        // Backend returns: {error: true, message: "...", status_code: ...} or {detail: "..."}
        let errorMessage = `HTTP error! status: ${response.status}`;
        if (typeof data === 'object' && data !== null) {
          if (data.message) {
            errorMessage = data.message;
          } else if (data.detail) {
            errorMessage = data.detail;
          } else if (data.error) {
            errorMessage = typeof data.error === 'string' ? data.error : 'Có lỗi xảy ra';
          }
        } else if (typeof data === 'string') {
          errorMessage = data;
        }
        
        const error = new Error(errorMessage);
        error.status = response.status;
        error.data = data;
        throw error;
      }

      return data;
    } catch (error) {
      console.error('API Request Error:', error);
      // Enhance error object to include response-like structure for compatibility
      if (error instanceof TypeError && error.message.includes('fetch')) {
        const networkError = new Error('Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng.');
        networkError.name = 'NetworkError';
        throw networkError;
      }
      throw error;
    }
  }

  get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    return this.request(url, { method: 'GET' });
  }

  post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  patch(endpoint, data) {
    return this.request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }

  // File upload
  upload(endpoint, formData) {
    const token = localStorage.getItem('access_token');
    const baseURL = this.baseURL;
    return fetch(`${baseURL}${endpoint}`, {
      method: 'POST',
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: formData,
    }).then(response => {
      if (!response.ok) throw new Error('Upload failed');
      return response.json();
    });
  }

  // Registration Fields Config
  /**
   * Lấy cấu hình hiện tại của các trường đăng ký
   * @returns {Promise} Cấu hình các trường đăng ký
   */
  getRegistrationFieldsConfig() {
    return this.get('/api/admin/settings/registration-fields');
  }

  /**
   * Lưu cấu hình mới của các trường đăng ký
   * @param {Object} config - Cấu hình các trường đăng ký
   * @returns {Promise} Kết quả lưu cấu hình
   */
  saveRegistrationFieldsConfig(config) {
    return this.put('/api/admin/settings/registration-fields', config);
  }

  /**
   * Lấy số dư ví của tất cả khách hàng
   * @param {Object} params - Tham số tìm kiếm và lọc
   * @returns {Promise} Danh sách số dư ví khách hàng
   */
  getCustomerWalletBalances(params = {}) {
    return this.get('/api/admin/customers/wallet-balances', params);
  }
}

export default new ApiClient();
