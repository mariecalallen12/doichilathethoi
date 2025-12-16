/**
 * Performance Monitoring Utility
 * Tracks and reports application performance metrics
 */

/**
 * Measure page load performance
 */
export function measurePageLoad() {
  if (typeof window === 'undefined' || !window.performance) {
    return null;
  }

  const navigation = performance.getEntriesByType('navigation')[0];
  if (!navigation) {
    return null;
  }

  return {
    // DNS lookup time
    dns: navigation.domainLookupEnd - navigation.domainLookupStart,
    
    // TCP connection time
    tcp: navigation.connectEnd - navigation.connectStart,
    
    // Request time
    request: navigation.responseStart - navigation.requestStart,
    
    // Response time
    response: navigation.responseEnd - navigation.responseStart,
    
    // DOM processing time
    domProcessing: navigation.domComplete - navigation.domInteractive,
    
    // Page load time
    loadTime: navigation.loadEventEnd - navigation.loadEventStart,
    
    // Total time
    total: navigation.loadEventEnd - navigation.fetchStart,
    
    // First Contentful Paint
    fcp: getFCP(),
    
    // Largest Contentful Paint
    lcp: getLCP(),
  };
}

/**
 * Get First Contentful Paint
 */
function getFCP() {
  try {
    const paintEntries = performance.getEntriesByType('paint');
    const fcpEntry = paintEntries.find(entry => entry.name === 'first-contentful-paint');
    return fcpEntry ? fcpEntry.startTime : null;
  } catch {
    return null;
  }
}

/**
 * Get Largest Contentful Paint
 */
function getLCP() {
  try {
    if ('PerformanceObserver' in window) {
      return new Promise((resolve) => {
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          resolve(lastEntry.renderTime || lastEntry.loadTime);
        });

        observer.observe({ entryTypes: ['largest-contentful-paint'] });

        // Resolve after 5 seconds if no LCP
        setTimeout(() => {
          observer.disconnect();
          resolve(null);
        }, 5000);
      });
    }
  } catch {
    return null;
  }
}

/**
 * Measure API call performance
 */
export function measureApiCall(apiCall) {
  const startTime = performance.now();
  
  return apiCall()
    .then((result) => {
      const endTime = performance.now();
      const duration = endTime - startTime;
      
      return {
        success: true,
        duration,
        result,
      };
    })
    .catch((error) => {
      const endTime = performance.now();
      const duration = endTime - startTime;
      
      return {
        success: false,
        duration,
        error: error.message,
      };
    });
}

/**
 * Track component render time
 */
export function trackComponentRender(componentName, renderFn) {
  const startTime = performance.now();
  
  const result = renderFn();
  
  const endTime = performance.now();
  const duration = endTime - startTime;
  
  if (duration > 16) { // More than one frame (16ms at 60fps)
    console.warn(`Component ${componentName} took ${duration.toFixed(2)}ms to render`);
  }
  
  return {
    componentName,
    duration,
    result,
  };
}

/**
 * Monitor memory usage
 */
export function getMemoryUsage() {
  if (typeof performance === 'undefined' || !performance.memory) {
    return null;
  }

  return {
    used: performance.memory.usedJSHeapSize,
    total: performance.memory.totalJSHeapSize,
    limit: performance.memory.jsHeapSizeLimit,
    percentage: (performance.memory.usedJSHeapSize / performance.memory.jsHeapSizeLimit) * 100,
  };
}

/**
 * Report performance metrics
 */
export function reportPerformanceMetrics() {
  const pageLoad = measurePageLoad();
  const memory = getMemoryUsage();

  const metrics = {
    timestamp: new Date().toISOString(),
    pageLoad,
    memory,
    userAgent: navigator.userAgent,
    connection: getConnectionInfo(),
  };

  // Log to console in development
  if (import.meta.env.DEV) {
    console.log('Performance Metrics:', metrics);
  }

  // Send to analytics/monitoring service in production
  if (import.meta.env.PROD) {
    // Example: send to analytics
    // analytics.track('performance_metrics', metrics);
  }

  return metrics;
}

/**
 * Get connection information
 */
function getConnectionInfo() {
  if ('connection' in navigator) {
    const conn = navigator.connection;
    return {
      effectiveType: conn.effectiveType,
      downlink: conn.downlink,
      rtt: conn.rtt,
      saveData: conn.saveData,
    };
  }
  return null;
}


