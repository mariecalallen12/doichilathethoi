import axios from 'axios';
import { handleApiError, getErrorMessage } from '../utils/errorHandler';
import { error as showErrorToast } from '../utils/toast';
import { getApiBaseUrl } from '../../utils/runtimeConfig';

const API_BASE_URL = getApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Error interceptor with user-friendly messages
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // #region agent log
    fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'client.js:28',message:'API error intercepted',data:{url:error.config?.url,method:error.config?.method,status:error.response?.status,statusText:error.response?.statusText,responseData:error.response?.data,pathname:window.location.pathname},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})).catch(()=>{});
    // #endregion
    
    const errorMessage = getErrorMessage(error);
    
    // #region agent log
    fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'client.js:32',message:'Error message generated',data:{errorMessage,status:error.response?.status,detail:error.response?.data?.detail,message:error.response?.data?.message},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})).catch(()=>{});
    // #endregion
    
    // Check if this is a 401 error on a public page (expected behavior)
    const isPublicPage = !['/personal', '/trading'].some(path => 
      window.location.pathname.startsWith(path)
    );
    
    // Suppress 401 errors on public pages (user not logged in is expected)
    if (error.response?.status === 401 && isPublicPage) {
      // Don't show toast for expected 401 on public pages
      return Promise.reject(error);
    }
    
    // Suppress 404 errors for certain endpoints that may not exist yet
    // These are non-critical endpoints that have fallback behavior
    const url = error.config?.url || error.request?.responseURL || error.config?.baseURL + error.config?.url || '';
    const urlPath = url.split('?')[0]; // Remove query params for matching
    // Extract just the path part (remove base URL if present)
    const pathMatch = urlPath.match(/\/api\/[^?]*/);
    const apiPath = pathMatch ? pathMatch[0] : urlPath;
    // Also check the original config URL
    const configUrl = error.config?.url || '';
    const fullUrl = error.config?.baseURL ? error.config.baseURL + configUrl : configUrl;
    
    const suppress404For = [
      '/api/market/symbols',  // Has fallback data
      '/api/market/orderbook', // Has fallback empty orderbook
      'market/symbols',  // Pattern match without /api prefix
      'market/orderbook', // Pattern match without /api prefix
    ];
    
    // Check if any suppression pattern matches
    const matchesPattern = suppress404For.some(pattern => 
      apiPath.includes(pattern) || 
      urlPath.includes(pattern) || 
      configUrl.includes(pattern) ||
      fullUrl.includes(pattern)
    );
    
    const shouldSuppress = error.response?.status === 404 && matchesPattern;
    
    // #region agent log
    console.log('[DEBUG] 404 check:', { 
      url, 
      urlPath, 
      apiPath, 
      configUrl,
      fullUrl,
      status: error.response?.status, 
      shouldSuppress, 
      matchesPattern,
      errorMessage,
      suppressPatterns: suppress404For
    });
    fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'client.js:60',message:'404 suppression check',data:{url,urlPath,apiPath,configUrl,fullUrl,status:error.response?.status,shouldSuppress,matchesPattern,errorMessage},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    
    if (shouldSuppress) {
      // #region agent log
      console.log('[DEBUG] Suppressing 404 for:', { apiPath, urlPath, configUrl });
      fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'client.js:75',message:'Suppressing 404 for endpoint with fallback',data:{url,apiPath,urlPath,configUrl,status:404},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
      // #endregion
      // Don't show toast for expected 404s on endpoints with fallback behavior
      return Promise.reject(error);
    }
    
    // #region agent log
    fetch('http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'client.js:52',message:'Showing error toast',data:{errorMessage,status:error.response?.status,isPublicPage,url},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})).catch(()=>{});
    // #endregion
    
    // Show toast notification for other errors
    showErrorToast(errorMessage);
    
    // Handle 401 - redirect to login (only on protected pages)
    if (error.response?.status === 401 && !isPublicPage) {
      localStorage.removeItem('auth_token');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

export const clientApi = {
  async getDashboard() {
    const response = await api.get('/client/dashboard');
    // Chuẩn hoá: trả về object dạng { overview, stats, recentTransactions, riskScore, complianceStatus, exchangeRates, ... }
    const data = response.data;
    if (data.data) {
      // Trường hợp backend bọc trong { success, data, exchangeRates, ... }
      return {
        ...data,
        data: {
          ...data.data,
          exchangeRates: data.exchangeRates || data.data.exchangeRates,
        },
      };
    }
    return data;
  },

  async getWalletBalances(params = {}) {
    const response = await api.get('/client/wallet-balances', { params });
    return response.data;
  },

  async getTransactions(params = {}) {
    const response = await api.get('/client/transactions', { params });
    return response.data;
  },

  async getExchangeRates() {
    const response = await api.get('/client/exchange-rates');
    return response.data;
  },

  /**
   * Create crypto deposit address based on selected currency and network
   * Returns the inner data object when available.
   */
  async createCryptoDepositAddress(payload) {
    const response = await api.post('/client/crypto-deposit-address', payload);
    const data = response.data;
    return data?.data || data;
  },

  /**
   * Generate VietQR payment data for bank transfer deposits
   * Returns the inner data object when available.
   */
  async generateVietQR(payload) {
    const response = await api.post('/client/generate-vietqr', payload);
    const data = response.data;
    return data?.data || data;
  },
};

// Export axios instance as default for direct API calls
export default api;
