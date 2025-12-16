/**
 * Build Information Utility
 * Provides build metadata and version information
 */

/**
 * Get build information
 */
export function getBuildInfo() {
  // Try to load deployment info if available
  try {
    // In production, this would be loaded from deployment-info.json
    const buildInfo = {
      version: import.meta.env.VITE_APP_VERSION || '2.0.0',
      buildTime: import.meta.env.VITE_BUILD_TIME || new Date().toISOString(),
      environment: import.meta.env.MODE || 'development',
      apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    };

    return buildInfo;
  } catch (error) {
    console.warn('Could not load build info:', error);
    return {
      version: 'unknown',
      buildTime: new Date().toISOString(),
      environment: 'development',
      apiBaseUrl: 'http://localhost:8000',
    };
  }
}

/**
 * Get version information
 */
export function getVersion() {
  const info = getBuildInfo();
  return info.version;
}

/**
 * Get environment information
 */
export function getEnvironment() {
  const info = getBuildInfo();
  return info.environment;
}

/**
 * Check if running in production
 */
export function isProduction() {
  return getEnvironment() === 'production';
}

/**
 * Check if running in development
 */
export function isDevelopment() {
  return getEnvironment() === 'development';
}

/**
 * Display build information in console
 */
export function displayBuildInfo() {
  if (isDevelopment()) {
    const info = getBuildInfo();
    console.log('%cBuild Information', 'color: #667eea; font-weight: bold; font-size: 14px');
    console.table(info);
  }
}

