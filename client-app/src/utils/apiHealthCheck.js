/**
 * API Health Check Utility
 * Checks backend API availability and endpoint health
 */

import { getApiBaseUrl } from './runtimeConfig';

const API_BASE_URL = getApiBaseUrl();

/**
 * Check if API is available
 */
export async function checkApiHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: AbortSignal.timeout(5000), // 5 second timeout
    });

    if (response.ok) {
      const data = await response.json();
      return {
        available: true,
        status: response.status,
        data,
        timestamp: new Date().toISOString(),
      };
    }

    return {
      available: false,
      status: response.status,
      error: `API returned status ${response.status}`,
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    return {
      available: false,
      error: error.message || 'Network error',
      timestamp: new Date().toISOString(),
    };
  }
}

/**
 * Check specific endpoint availability
 */
export async function checkEndpoint(endpoint, method = 'GET') {
  try {
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      signal: AbortSignal.timeout(5000),
    });

    return {
      available: response.status < 500,
      status: response.status,
      endpoint,
      method,
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    return {
      available: false,
      endpoint,
      method,
      error: error.message,
      timestamp: new Date().toISOString(),
    };
  }
}

/**
 * Check multiple endpoints
 */
export async function checkEndpoints(endpoints) {
  const results = await Promise.all(
    endpoints.map(endpoint => checkEndpoint(endpoint))
  );

  return {
    total: endpoints.length,
    available: results.filter(r => r.available).length,
    unavailable: results.filter(r => !r.available).length,
    results,
    timestamp: new Date().toISOString(),
  };
}

/**
 * Monitor API health periodically
 */
export function monitorApiHealth(callback, interval = 30000) {
  let isMonitoring = false;
  let intervalId = null;

  const start = () => {
    if (isMonitoring) return;

    isMonitoring = true;
    intervalId = setInterval(async () => {
      const health = await checkApiHealth();
      callback(health);
    }, interval);

    // Initial check
    checkApiHealth().then(callback);
  };

  const stop = () => {
    if (intervalId) {
      clearInterval(intervalId);
      intervalId = null;
    }
    isMonitoring = false;
  };

  return { start, stop, isMonitoring: () => isMonitoring };
}


