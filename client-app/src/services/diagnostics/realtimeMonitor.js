/**
 * Real-time Monitor Service
 * Monitor diagnostic health real-time và nhận alerts qua WebSocket
 */

import { useWebSocketStore } from '../../stores/websocket';
import { useDiagnosticsStore } from '../../stores/diagnostics';
import { collectAllDiagnostics } from './tradingDiagnostics';

/**
 * Real-time Monitor class
 */
export class RealtimeMonitor {
  constructor() {
    this.wsStore = null;
    this.diagnosticsStore = null;
    this.monitoringInterval = null;
    this.isMonitoring = false;
    this.healthCheckInterval = 30000; // 30 seconds default
    this.onHealthChangeCallback = null;
    this.onAlertCallback = null;
  }

  /**
   * Initialize monitor với stores
   */
  initialize(wsStore, diagnosticsStore) {
    this.wsStore = wsStore;
    this.diagnosticsStore = diagnosticsStore;
  }

  /**
   * Bắt đầu monitoring
   */
  start(options = {}) {
    if (this.isMonitoring) {
      console.warn('[RealtimeMonitor] Already monitoring');
      return;
    }

    const {
      interval = this.healthCheckInterval,
      onHealthChange = null,
      onAlert = null,
    } = options;

    this.healthCheckInterval = interval;
    this.onHealthChangeCallback = onHealthChange;
    this.onAlertCallback = onAlert;

    this.isMonitoring = true;

    // Setup WebSocket listeners
    this._setupWebSocketListeners();

    // Start periodic health checks
    this._startHealthChecks();

    console.log('[RealtimeMonitor] Started monitoring');
  }

  /**
   * Dừng monitoring
   */
  stop() {
    if (!this.isMonitoring) {
      return;
    }

    this.isMonitoring = false;

    // Clear interval
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }

    // Remove WebSocket listeners
    this._removeWebSocketListeners();

    console.log('[RealtimeMonitor] Stopped monitoring');
  }

  /**
   * Setup WebSocket listeners cho diagnostic updates
   */
  _setupWebSocketListeners() {
    if (!this.wsStore || !this.wsStore.isConnected) {
      console.warn('[RealtimeMonitor] WebSocket not connected');
      return;
    }

    // Listen for health updates
    this.wsStore.subscribe('diagnostics', (message) => {
      if (message.type === 'health_update') {
        this._handleHealthUpdate(message.data);
      } else if (message.type === 'alert') {
        this._handleAlert(message.data);
      }
    });
  }

  /**
   * Remove WebSocket listeners
   */
  _removeWebSocketListeners() {
    if (this.wsStore) {
      this.wsStore.unsubscribe('diagnostics', this._handleHealthUpdate);
      this.wsStore.unsubscribe('diagnostics', this._handleAlert);
    }
  }

  /**
   * Start periodic health checks
   */
  _startHealthChecks() {
    // Run initial check
    this._performHealthCheck();

    // Set up interval
    this.monitoringInterval = setInterval(() => {
      if (this.isMonitoring) {
        this._performHealthCheck();
      }
    }, this.healthCheckInterval);
  }

  /**
   * Perform health check
   */
  async _performHealthCheck() {
    try {
      if (!this.diagnosticsStore) {
        return;
      }

      const previousHealth = this.diagnosticsStore.overallHealth;
      
      // Collect diagnostics
      await this.diagnosticsStore.collectDiagnostics();
      
      const currentHealth = this.diagnosticsStore.overallHealth;

      // Detect health change
      if (previousHealth && previousHealth !== currentHealth) {
        const change = {
          from: previousHealth,
          to: currentHealth,
          timestamp: new Date().toISOString(),
          hasIssues: this.diagnosticsStore.hasIssues,
        };

        this._handleHealthChange(change);
      }

      // Check for new alerts
      if (this.diagnosticsStore.hasIssues) {
        const lastReport = this.diagnosticsStore.lastReport;
        if (lastReport && lastReport.diagnostics?.recommendations) {
          const criticalIssues = lastReport.diagnostics.recommendations.filter(
            r => r.severity === 'high' || r.severity === 'critical'
          );

          if (criticalIssues.length > 0) {
            this._handlePotentialAlert(criticalIssues);
          }
        }
      }
    } catch (error) {
      console.error('[RealtimeMonitor] Health check error:', error);
    }
  }

  /**
   * Handle health update từ WebSocket
   */
  _handleHealthUpdate(data) {
    if (!data) return;

    const change = {
      from: data.previous_status,
      to: data.current_status,
      timestamp: data.timestamp,
      hasIssues: data.has_issues,
      issues: data.issues || [],
    };

    this._handleHealthChange(change);
  }

  /**
   * Handle health change
   */
  _handleHealthChange(change) {
    console.log('[RealtimeMonitor] Health changed:', change);

    // Update diagnostics store
    if (this.diagnosticsStore) {
      // Health status will be updated automatically by store
    }

    // Call callback
    if (this.onHealthChangeCallback) {
      this.onHealthChangeCallback(change);
    }

    // Emit custom event for components to listen
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('diagnostic-health-change', {
        detail: change,
      }));
    }
  }

  /**
   * Handle alert từ WebSocket
   */
  _handleAlert(data) {
    if (!data) return;

    console.log('[RealtimeMonitor] Alert received:', data);

    const alert = {
      id: data.id,
      rule_id: data.alert_rule_id,
      severity: data.severity,
      title: data.title || 'Alert: Trading Dashboard Issue',
      message: data.message,
      timestamp: data.timestamp || new Date().toISOString(),
      conditions_met: data.conditions_met,
    };

    // Call callback
    if (this.onAlertCallback) {
      this.onAlertCallback(alert);
    }

    // Emit custom event
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('diagnostic-alert', {
        detail: alert,
      }));
    }
  }

  /**
   * Handle potential alert từ health check
   */
  _handlePotentialAlert(issues) {
    // This could trigger a notification or alert
    // For now, just log it
    console.warn('[RealtimeMonitor] Potential alert detected:', issues);

    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('diagnostic-potential-alert', {
        detail: { issues },
      }));
    }
  }

  /**
   * Get current health status
   */
  getCurrentHealth() {
    if (!this.diagnosticsStore) {
      return null;
    }

    return {
      overall: this.diagnosticsStore.overallHealth,
      hasIssues: this.diagnosticsStore.hasIssues,
      healthStatus: this.diagnosticsStore.healthStatus,
      lastReport: this.diagnosticsStore.lastReport,
    };
  }

  /**
   * Set health check interval
   */
  setInterval(intervalMs) {
    this.healthCheckInterval = intervalMs;
    
    if (this.isMonitoring) {
      this.stop();
      this.start({
        interval: intervalMs,
        onHealthChange: this.onHealthChangeCallback,
        onAlert: this.onAlertCallback,
      });
    }
  }
}

// Singleton instance
let monitorInstance = null;

/**
 * Get singleton monitor instance
 */
export function getRealtimeMonitor() {
  if (!monitorInstance) {
    monitorInstance = new RealtimeMonitor();
  }
  return monitorInstance;
}

/**
 * Initialize và start monitoring
 */
export function startRealtimeMonitoring(options = {}) {
  const monitor = getRealtimeMonitor();
  
  // Import stores dynamically to avoid circular dependencies
  import('../../stores/websocket').then(({ useWebSocketStore }) => {
    import('../../stores/diagnostics').then(({ useDiagnosticsStore }) => {
      const wsStore = useWebSocketStore();
      const diagnosticsStore = useDiagnosticsStore();
      
      monitor.initialize(wsStore, diagnosticsStore);
      monitor.start(options);
    });
  });
  
  return monitor;
}

/**
 * Stop monitoring
 */
export function stopRealtimeMonitoring() {
  const monitor = getRealtimeMonitor();
  monitor.stop();
}

