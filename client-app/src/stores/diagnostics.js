/**
 * Diagnostic Store - Quản lý diagnostic state và report history
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { collectAllDiagnostics } from '../services/diagnostics/tradingDiagnostics';
import { generateJSONReport, generateHTMLReport, downloadReport, sendReportToBackend } from '../services/diagnostics/reportGenerator';
import { useWebSocketStore } from './websocket';
import { setupConsoleErrorCollection } from '../services/diagnostics/tradingDiagnostics';

export const useDiagnosticsStore = defineStore('diagnostics', () => {
  const isCollecting = ref(false);
  const lastReport = ref(null);
  const reportHistory = ref([]);
  const healthStatus = ref({
    auth: 'unknown',
    api: 'unknown',
    websocket: 'unknown',
    components: {},
  });
  const autoReportingEnabled = ref(false);
  const healthCheckInterval = ref(null);
  const healthCheckIntervalMs = ref(60000); // 1 minute default

  // Computed
  const overallHealth = computed(() => {
    const statuses = [
      healthStatus.value.auth,
      healthStatus.value.api,
      healthStatus.value.websocket,
    ];
    
    if (statuses.every(s => s === 'healthy')) return 'healthy';
    if (statuses.some(s => s === 'unhealthy')) return 'unhealthy';
    if (statuses.some(s => s === 'degraded')) return 'degraded';
    return 'unknown';
  });

  const hasIssues = computed(() => {
    return overallHealth.value !== 'healthy';
  });

  /**
   * Thu thập diagnostics
   */
  async function collectDiagnostics() {
    if (isCollecting.value) {
      // Only warn in development
      if (import.meta.env.DEV) {
        console.warn('Diagnostic collection already in progress');
      }
      return lastReport.value;
    }

    isCollecting.value = true;
    try {
      const wsStore = useWebSocketStore();
      const diagnostics = await collectAllDiagnostics(wsStore);
      
      // Update health status
      updateHealthStatus(diagnostics);
      
      // Store report
      const report = {
        id: `report-${Date.now()}`,
        timestamp: diagnostics.timestamp,
        diagnostics,
        summary: {
          authStatus: diagnostics.auth?.hasToken ? 'authenticated' : 'not_authenticated',
          apiHealth: diagnostics.api?.overallHealth || 'unknown',
          wsConnected: diagnostics.websocket?.connected || false,
          recommendationsCount: diagnostics.recommendations?.length || 0,
        },
      };

      lastReport.value = report;
      reportHistory.value.unshift(report);
      
      // Keep only last 10 reports
      if (reportHistory.value.length > 10) {
        reportHistory.value = reportHistory.value.slice(0, 10);
      }

      return report;
    } catch (error) {
      console.error('Error collecting diagnostics:', error);
      throw error;
    } finally {
      isCollecting.value = false;
    }
  }

  /**
   * Update health status từ diagnostics
   */
  function updateHealthStatus(diagnostics) {
    // Auth status
    if (!diagnostics.auth?.hasToken) {
      healthStatus.value.auth = 'unhealthy';
    } else if (diagnostics.auth?.isExpired) {
      healthStatus.value.auth = 'unhealthy';
    } else {
      healthStatus.value.auth = 'healthy';
    }

    // API status
    healthStatus.value.api = diagnostics.api?.overallHealth || 'unknown';

    // WebSocket status
    if (diagnostics.websocket?.connected) {
      healthStatus.value.websocket = 'healthy';
    } else if (diagnostics.websocket?.error) {
      healthStatus.value.websocket = 'unhealthy';
    } else {
      healthStatus.value.websocket = 'degraded';
    }

    // Component status
    if (diagnostics.components) {
      Object.entries(diagnostics.components).forEach(([key, comp]) => {
        if (comp?.isEmpty) {
          healthStatus.value.components[key] = 'unhealthy';
        } else if (comp?.hasContent) {
          healthStatus.value.components[key] = 'healthy';
        } else {
          healthStatus.value.components[key] = 'unknown';
        }
      });
    }
  }

  /**
   * Generate và download JSON report
   */
  async function generateAndDownloadJSON() {
    try {
      const wsStore = useWebSocketStore();
      const report = await generateJSONReport(wsStore);
      const filename = `trading-diagnostic-${new Date().toISOString().replace(/:/g, '-')}.json`;
      downloadReport(report, filename, 'application/json');
      return report;
    } catch (error) {
      console.error('Error generating JSON report:', error);
      throw error;
    }
  }

  /**
   * Generate và download HTML report
   */
  async function generateAndDownloadHTML() {
    try {
      const wsStore = useWebSocketStore();
      const report = await generateHTMLReport(wsStore);
      const filename = `trading-diagnostic-${new Date().toISOString().replace(/:/g, '-')}.html`;
      downloadReport(report, filename, 'text/html');
      return report;
    } catch (error) {
      console.error('Error generating HTML report:', error);
      throw error;
    }
  }

  /**
   * Send report to backend
   */
  async function sendReport() {
    try {
      if (!lastReport.value) {
        await collectDiagnostics();
      }
      
      const wsStore = useWebSocketStore();
      const report = await generateJSONReport(wsStore);
      const result = await sendReportToBackend(report, wsStore);
      
      // Update last report with backend response
      if (lastReport.value) {
        lastReport.value.backendId = result.id || result.report_id;
        lastReport.value.sentAt = new Date().toISOString();
      }
      
      return result;
    } catch (error) {
      console.error('Error sending report to backend:', error);
      throw error;
    }
  }

  /**
   * Enable/disable auto reporting
   */
  function setAutoReporting(enabled) {
    autoReportingEnabled.value = enabled;
    
    if (enabled) {
      startHealthCheck();
    } else {
      stopHealthCheck();
    }
  }

  /**
   * Start periodic health check
   */
  function startHealthCheck() {
    if (healthCheckInterval.value) {
      clearInterval(healthCheckInterval.value);
    }

    healthCheckInterval.value = setInterval(async () => {
      try {
        await collectDiagnostics();
        
        // Auto-send report nếu có issues nghiêm trọng
        if (lastReport.value && overallHealth.value === 'unhealthy') {
          const criticalIssues = lastReport.value.diagnostics?.recommendations?.filter(
            r => r.severity === 'high'
          ) || [];
          
          if (criticalIssues.length > 0 && autoReportingEnabled.value) {
            try {
              await sendReport();
              if (import.meta.env.DEV) {
                console.info('[Diagnostics] Auto-sent report due to critical issues');
              }
            } catch (e) {
              if (import.meta.env.DEV) {
                console.warn('[Diagnostics] Failed to auto-send report:', e);
              }
            }
          }
        }
      } catch (error) {
        // Only log errors in development
        if (import.meta.env.DEV) {
          console.error('[Diagnostics] Health check error:', error);
        }
      }
    }, healthCheckIntervalMs.value);
  }

  /**
   * Stop periodic health check
   */
  function stopHealthCheck() {
    if (healthCheckInterval.value) {
      clearInterval(healthCheckInterval.value);
      healthCheckInterval.value = null;
    }
  }

  /**
   * Set health check interval
   */
  function setHealthCheckInterval(ms) {
    healthCheckIntervalMs.value = ms;
    if (autoReportingEnabled.value) {
      stopHealthCheck();
      startHealthCheck();
    }
  }

  /**
   * Initialize diagnostics (setup console error collection)
   */
  function initialize() {
    if (typeof window !== 'undefined') {
      setupConsoleErrorCollection();
    }
  }

  return {
    // State
    isCollecting,
    lastReport,
    reportHistory,
    healthStatus,
    autoReportingEnabled,
    overallHealth,
    hasIssues,
    
    // Actions
    collectDiagnostics,
    generateAndDownloadJSON,
    generateAndDownloadHTML,
    sendReport,
    setAutoReporting,
    startHealthCheck,
    stopHealthCheck,
    setHealthCheckInterval,
    initialize,
  };
});

