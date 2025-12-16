/**
 * Trading Dashboard Diagnostic Service
 * Thu thập thông tin về trạng thái hệ thống để phát hiện và báo cáo vấn đề
 */

import { getApiBaseUrl } from '../../utils/runtimeConfig';

/**
 * Kiểm tra trạng thái authentication
 */
export async function checkAuthStatus() {
  const token = localStorage.getItem('auth_token');
  const accessToken = localStorage.getItem('access_token');
  
  const authStatus = {
    hasToken: !!token || !!accessToken,
    tokenType: token ? 'auth_token' : accessToken ? 'access_token' : null,
    tokenLength: token?.length || accessToken?.length || 0,
    tokenPreview: token ? `${token.substring(0, 10)}...` : accessToken ? `${accessToken.substring(0, 10)}...` : null,
  };

  // Kiểm tra token expiry nếu có JWT
  if (token || accessToken) {
    try {
      const tokenToCheck = token || accessToken;
      const payload = JSON.parse(atob(tokenToCheck.split('.')[1]));
      authStatus.expiresAt = payload.exp ? new Date(payload.exp * 1000).toISOString() : null;
      authStatus.isExpired = payload.exp ? Date.now() > payload.exp * 1000 : null;
      authStatus.userId = payload.user_id || payload.sub || null;
    } catch (e) {
      authStatus.tokenParseError = e.message;
    }
  }

  return authStatus;
}

/**
 * Kiểm tra health của các API endpoints trading
 */
export async function checkApiHealth() {
  const API_BASE_URL = getApiBaseUrl();
  const token = localStorage.getItem('auth_token') || localStorage.getItem('access_token');
  
  const endpoints = [
    '/trading/orders',
    '/trading/positions',
    '/trading/orderbook',
    '/trading/statistics',
    '/market/instruments',
  ];

  const results = {
    baseUrl: API_BASE_URL,
    endpoints: {},
    overallHealth: 'unknown',
    errors: [],
  };

  const checkPromises = endpoints.map(async (endpoint) => {
    const url = `${API_BASE_URL}${endpoint}`;
    const startTime = performance.now();
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(5000), // 5s timeout
      });

      const duration = performance.now() - startTime;
      const hasData = response.ok && response.status === 200;
      
      let dataPreview = null;
      try {
        const data = await response.clone().json();
        dataPreview = Array.isArray(data) 
          ? `Array(${data.length})` 
          : typeof data === 'object' 
            ? Object.keys(data).slice(0, 3).join(', ') 
            : String(data).substring(0, 50);
      } catch {
        // Không parse được JSON
      }

      results.endpoints[endpoint] = {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        hasData,
        duration: Math.round(duration),
        dataPreview,
        timestamp: new Date().toISOString(),
      };

      if (!response.ok) {
        results.errors.push({
          endpoint,
          status: response.status,
          statusText: response.statusText,
        });
      }
    } catch (error) {
      const duration = performance.now() - startTime;
      results.endpoints[endpoint] = {
        error: error.name,
        message: error.message,
        duration: Math.round(duration),
        timestamp: new Date().toISOString(),
      };
      results.errors.push({
        endpoint,
        error: error.name,
        message: error.message,
      });
    }
  });

  await Promise.allSettled(checkPromises);

  // Đánh giá overall health
  const successCount = Object.values(results.endpoints).filter(e => e.ok).length;
  const totalCount = endpoints.length;
  
  if (successCount === totalCount) {
    results.overallHealth = 'healthy';
  } else if (successCount > 0) {
    results.overallHealth = 'degraded';
  } else {
    results.overallHealth = 'unhealthy';
  }

  return results;
}

/**
 * Kiểm tra trạng thái WebSocket
 */
export function checkWebSocketStatus(wsStore) {
  if (!wsStore) {
    return {
      available: false,
      error: 'WebSocket store not available',
    };
  }

  return {
    connected: wsStore.connected || wsStore.isConnected || false,
    reconnectAttempts: wsStore.reconnectAttempts || 0,
    lastLatencyMs: wsStore.lastLatencyMs || null,
    error: wsStore.error || null,
    timestamp: new Date().toISOString(),
  };
}

/**
 * Kiểm tra trạng thái component render
 */
export function checkComponentState() {
  const components = {
    chart: {
      container: document.querySelector('.flex-1.min-h-\\[300px\\], .flex-1.min-h-\\[400px\\]'),
      isEmpty: false,
      hasContent: false,
    },
    orderBook: {
      container: document.querySelector('[class*="OrderBook"]'),
      isEmpty: false,
      hasContent: false,
    },
    watchlist: {
      container: document.querySelector('[class*="MarketWatch"]'),
      isEmpty: false,
      hasContent: false,
    },
  };

  // Kiểm tra từng component
  Object.keys(components).forEach(key => {
    const comp = components[key];
    if (comp.container) {
      // Kiểm tra nếu container trống hoặc chỉ có background
      const children = comp.container.children;
      const hasVisibleContent = Array.from(children).some(child => {
        const style = window.getComputedStyle(child);
        return style.display !== 'none' && 
               style.visibility !== 'hidden' && 
               child.textContent.trim().length > 0;
      });
      
      comp.hasContent = hasVisibleContent || comp.container.textContent.trim().length > 0;
      comp.isEmpty = !comp.hasContent;
      comp.elementCount = children.length;
      comp.textLength = comp.container.textContent.trim().length;
    } else {
      comp.error = 'Container not found';
      comp.isEmpty = true;
    }
  });

  return components;
}

/**
 * Thu thập console errors và warnings
 */
export function collectConsoleErrors() {
  // Lưu lại console errors nếu có
  // Note: Cần setup error handler trước khi component mount
  if (window.__diagnosticConsoleErrors) {
    return window.__diagnosticConsoleErrors;
  }
  
  return {
    errors: [],
    warnings: [],
    info: [],
    note: 'Console errors collection requires setup before page load',
  };
}

/**
 * Thu thập network requests summary
 */
export function collectNetworkSummary() {
  if (!window.performance || !window.performance.getEntriesByType) {
    return {
      available: false,
      note: 'Performance API not available',
    };
  }

  const resources = window.performance.getEntriesByType('resource');
  const networkRequests = resources.map(resource => ({
    name: resource.name,
    type: resource.initiatorType,
    duration: Math.round(resource.duration),
    size: resource.transferSize || 0,
    status: resource.responseStatus || null,
    timestamp: new Date(resource.startTime + performance.timeOrigin).toISOString(),
  }));

  // Phân loại requests
  const apiRequests = networkRequests.filter(r => 
    r.name.includes('/api/') || r.name.includes('trading')
  );
  const failedRequests = networkRequests.filter(r => 
    r.status && (r.status >= 400 || r.status === 0)
  );

  return {
    totalRequests: networkRequests.length,
    apiRequests: apiRequests.length,
    failedRequests: failedRequests.length,
    requests: networkRequests.slice(-50), // Last 50 requests
    failed: failedRequests,
  };
}

/**
 * Kiểm tra bundle loading status
 */
export function checkBundleStatus() {
  const scripts = Array.from(document.querySelectorAll('script[src]')).map(script => ({
    src: script.src,
    loaded: script.readyState === 'complete' || script.readyState === 'loaded',
    async: script.async,
    defer: script.defer,
  }));

  const stylesheets = Array.from(document.querySelectorAll('link[rel="stylesheet"]')).map(link => ({
    href: link.href,
    loaded: link.sheet !== null,
  }));

  const failedResources = window.performance?.getEntriesByType?.('resource')?.filter(
    r => r.transferSize === 0 && r.responseStatus >= 400
  ) || [];

  return {
    scripts: {
      total: scripts.length,
      loaded: scripts.filter(s => s.loaded).length,
      failed: scripts.filter(s => !s.loaded).length,
      details: scripts,
    },
    stylesheets: {
      total: stylesheets.length,
      loaded: stylesheets.filter(s => s.loaded).length,
      failed: stylesheets.filter(s => !s.loaded).length,
      details: stylesheets,
    },
    failedResources: failedResources.map(r => ({
      name: r.name,
      status: r.responseStatus,
    })),
  };
}

/**
 * Thu thập LocalStorage state
 */
export function collectLocalStorageState() {
  const storage = {};
  try {
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key) {
        const value = localStorage.getItem(key);
        // Mask sensitive data
        if (key.includes('token') || key.includes('password') || key.includes('secret')) {
          storage[key] = value ? `${value.substring(0, 10)}...` : null;
        } else {
          storage[key] = value;
        }
      }
    }
  } catch (e) {
    return {
      error: e.message,
      available: false,
    };
  }

  return {
    available: true,
    keys: Object.keys(storage),
    data: storage,
  };
}

/**
 * Thu thập tất cả diagnostic information
 */
export async function collectAllDiagnostics(wsStore = null) {
  const startTime = performance.now();
  
  const [
    authStatus,
    apiHealth,
    wsStatus,
    componentState,
    consoleErrors,
    networkSummary,
    bundleStatus,
    localStorageState,
  ] = await Promise.allSettled([
    checkAuthStatus(),
    checkApiHealth(),
    Promise.resolve(checkWebSocketStatus(wsStore)),
    Promise.resolve(checkComponentState()),
    Promise.resolve(collectConsoleErrors()),
    Promise.resolve(collectNetworkSummary()),
    Promise.resolve(checkBundleStatus()),
    Promise.resolve(collectLocalStorageState()),
  ]);

  const diagnostics = {
    timestamp: new Date().toISOString(),
    url: window.location.href,
    userAgent: navigator.userAgent,
    collectionDuration: Math.round(performance.now() - startTime),
    auth: authStatus.status === 'fulfilled' ? authStatus.value : { error: authStatus.reason?.message },
    api: apiHealth.status === 'fulfilled' ? apiHealth.value : { error: apiHealth.reason?.message },
    websocket: wsStatus.status === 'fulfilled' ? wsStatus.value : { error: wsStatus.reason?.message },
    components: componentState.status === 'fulfilled' ? componentState.value : { error: componentState.reason?.message },
    console: consoleErrors.status === 'fulfilled' ? consoleErrors.value : { error: consoleErrors.reason?.message },
    network: networkSummary.status === 'fulfilled' ? networkSummary.value : { error: networkSummary.reason?.message },
    bundles: bundleStatus.status === 'fulfilled' ? bundleStatus.value : { error: bundleStatus.reason?.message },
    storage: localStorageState.status === 'fulfilled' ? localStorageState.value : { error: localStorageState.reason?.message },
  };

  // Phân tích và đưa ra recommendations
  diagnostics.recommendations = generateRecommendations(diagnostics);

  return diagnostics;
}

/**
 * Tạo recommendations dựa trên diagnostic results
 */
function generateRecommendations(diagnostics) {
  const recommendations = [];

  // Auth issues
  if (!diagnostics.auth?.hasToken) {
    recommendations.push({
      severity: 'high',
      category: 'authentication',
      issue: 'Không tìm thấy authentication token',
      solution: 'Vui lòng đăng nhập lại. Kiểm tra LocalStorage có key "auth_token" hoặc "access_token".',
    });
  } else if (diagnostics.auth?.isExpired) {
    recommendations.push({
      severity: 'high',
      category: 'authentication',
      issue: 'Token đã hết hạn',
      solution: 'Vui lòng đăng nhập lại để refresh token.',
    });
  }

  // API issues
  if (diagnostics.api?.overallHealth === 'unhealthy') {
    recommendations.push({
      severity: 'high',
      category: 'api',
      issue: 'Tất cả API endpoints không phản hồi',
      solution: 'Kiểm tra kết nối mạng, backend server có đang chạy không, và CORS settings.',
    });
  } else if (diagnostics.api?.overallHealth === 'degraded') {
    recommendations.push({
      severity: 'medium',
      category: 'api',
      issue: 'Một số API endpoints không hoạt động',
      solution: 'Kiểm tra backend logs và network tab trong DevTools để xem lỗi cụ thể.',
    });
  }

  // WebSocket issues
  if (!diagnostics.websocket?.connected) {
    recommendations.push({
      severity: 'medium',
      category: 'websocket',
      issue: 'WebSocket không kết nối',
      solution: 'Kiểm tra WebSocket server có đang chạy không. Thử reload trang.',
    });
  }

  // Component empty state
  const emptyComponents = Object.entries(diagnostics.components || {})
    .filter(([key, comp]) => comp?.isEmpty && key !== 'error');
  
  if (emptyComponents.length > 0) {
    recommendations.push({
      severity: 'medium',
      category: 'ui',
      issue: `Các component sau đang trống: ${emptyComponents.map(([key]) => key).join(', ')}`,
      solution: 'Kiểm tra API có trả dữ liệu không, WebSocket có gửi updates không, và component có đang chờ state không.',
    });
  }

  // Bundle loading issues
  if (diagnostics.bundles?.scripts?.failed > 0) {
    recommendations.push({
      severity: 'high',
      category: 'bundles',
      issue: 'Một số JavaScript bundles không tải được',
      solution: 'Kiểm tra network tab, có thể bị adblock/CSP chặn. Thử disable extensions và reload.',
    });
  }

  if (diagnostics.bundles?.stylesheets?.failed > 0) {
    recommendations.push({
      severity: 'medium',
      category: 'bundles',
      issue: 'Một số CSS files không tải được',
      solution: 'Kiểm tra network tab và CSP headers.',
    });
  }

  // Network errors
  if (diagnostics.network?.failedRequests > 0) {
    recommendations.push({
      severity: 'medium',
      category: 'network',
      issue: `Có ${diagnostics.network.failedRequests} requests thất bại`,
      solution: 'Xem chi tiết trong network tab của DevTools. Kiểm tra status codes (401/403/404/500).',
    });
  }

  return recommendations;
}

/**
 * Setup console error collection
 */
export function setupConsoleErrorCollection() {
  if (typeof window === 'undefined') return;

  window.__diagnosticConsoleErrors = {
    errors: [],
    warnings: [],
    info: [],
  };

  const originalError = console.error;
  const originalWarn = console.warn;
  const originalInfo = console.info;

  console.error = function(...args) {
    window.__diagnosticConsoleErrors.errors.push({
      message: args.map(a => String(a)).join(' '),
      timestamp: new Date().toISOString(),
      stack: new Error().stack,
    });
    originalError.apply(console, args);
  };

  console.warn = function(...args) {
    window.__diagnosticConsoleErrors.warnings.push({
      message: args.map(a => String(a)).join(' '),
      timestamp: new Date().toISOString(),
    });
    originalWarn.apply(console, args);
  };

  console.info = function(...args) {
    window.__diagnosticConsoleErrors.info.push({
      message: args.map(a => String(a)).join(' '),
      timestamp: new Date().toISOString(),
    });
    originalInfo.apply(console, args);
  };
}

