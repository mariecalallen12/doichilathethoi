/**
 * DevTools Integration - Expose diagnostic functions to window object for manual use
 */

import { useDiagnosticsStore } from '../../stores/diagnostics';
import { generateJSONReport, generateHTMLReport, downloadReport } from './reportGenerator';
import { collectAllDiagnostics } from './tradingDiagnostics';
import { useWebSocketStore } from '../../stores/websocket';

/**
 * Setup global diagnostic functions for DevTools
 */
export function setupDevToolsIntegration() {
  if (typeof window === 'undefined') return;

  const diagnosticsStore = useDiagnosticsStore();
  const wsStore = useWebSocketStore();

  // Main diagnostic function
  window.generateDiagnosticReport = async (options = {}) => {
    const {
      download = false,
      format = 'json', // 'json' or 'html'
      sendToBackend = false,
      silent = false,
    } = options;

    try {
      if (!silent) {
        console.log('%c🔍 Running Trading Dashboard Diagnostics...', 'color: #a78bfa; font-weight: bold; font-size: 14px;');
      }

      const report = await diagnosticsStore.collectDiagnostics();

      if (!silent) {
        console.log('%c✅ Diagnostics collected successfully', 'color: #10b981; font-weight: bold;');
        console.log('Report summary:', report.summary);
        console.log('Full diagnostics:', report.diagnostics);
      }

      if (download) {
        if (format === 'html') {
          await diagnosticsStore.generateAndDownloadHTML();
          if (!silent) {
            console.log('%c📄 HTML report downloaded', 'color: #3b82f6;');
          }
        } else {
          await diagnosticsStore.generateAndDownloadJSON();
          if (!silent) {
            console.log('%c📄 JSON report downloaded', 'color: #3b82f6;');
          }
        }
      }

      if (sendToBackend) {
        await diagnosticsStore.sendReport();
        if (!silent) {
          console.log('%c📤 Report sent to backend', 'color: #10b981;');
        }
      }

      return report;
    } catch (error) {
      console.error('%c❌ Error generating diagnostic report:', 'color: #ef4444; font-weight: bold;', error);
      throw error;
    }
  };

  // Quick health check
  window.checkTradingHealth = async () => {
    try {
      const diagnostics = await collectAllDiagnostics(wsStore);
      
      console.log('%c📊 Trading Dashboard Health Check', 'color: #a78bfa; font-weight: bold; font-size: 14px;');
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      console.log(`Auth: ${diagnostics.auth?.hasToken ? '✅ Authenticated' : '❌ Not authenticated'}`);
      console.log(`API: ${diagnostics.api?.overallHealth || 'unknown'}`);
      console.log(`WebSocket: ${diagnostics.websocket?.connected ? '✅ Connected' : '❌ Disconnected'}`);
      console.log(`Empty Components: ${Object.entries(diagnostics.components || {})
        .filter(([_, comp]) => comp?.isEmpty)
        .map(([key]) => key)
        .join(', ') || 'None'}`);
      console.log(`Recommendations: ${diagnostics.recommendations?.length || 0}`);
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      
      return diagnostics;
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  };

  // Download report functions
  window.downloadDiagnosticJSON = async () => {
    await diagnosticsStore.generateAndDownloadJSON();
    console.log('%c📄 JSON report downloaded', 'color: #3b82f6;');
  };

  window.downloadDiagnosticHTML = async () => {
    await diagnosticsStore.generateAndDownloadHTML();
    console.log('%c📄 HTML report downloaded', 'color: #3b82f6;');
  };

  // Send to backend
  window.sendDiagnosticReport = async () => {
    try {
      await diagnosticsStore.sendReport();
      console.log('%c📤 Report sent to backend successfully', 'color: #10b981;');
    } catch (error) {
      console.error('%c❌ Failed to send report:', 'color: #ef4444;', error);
      throw error;
    }
  };

  // Get current health status
  window.getDiagnosticStatus = () => {
    const status = {
      overall: diagnosticsStore.overallHealth,
      hasIssues: diagnosticsStore.hasIssues,
      healthStatus: diagnosticsStore.healthStatus,
      lastReport: diagnosticsStore.lastReport,
    };
    console.log('%c📊 Current Diagnostic Status', 'color: #a78bfa; font-weight: bold;', status);
    return status;
  };

  // Toggle auto reporting
  window.toggleAutoReporting = (enabled) => {
    diagnosticsStore.setAutoReporting(enabled !== undefined ? enabled : !diagnosticsStore.autoReportingEnabled);
    console.log(`%c${diagnosticsStore.autoReportingEnabled ? '✅' : '❌'} Auto reporting ${diagnosticsStore.autoReportingEnabled ? 'enabled' : 'disabled'}`, 
      diagnosticsStore.autoReportingEnabled ? 'color: #10b981;' : 'color: #ef4444;');
  };

  // Help function
  window.diagnosticHelp = () => {
    console.log('%c🔧 Trading Dashboard Diagnostic Commands', 'color: #a78bfa; font-weight: bold; font-size: 16px;');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('%cgenerateDiagnosticReport(options)', 'color: #10b981; font-weight: bold;');
    console.log('  Generate and optionally download/send diagnostic report');
    console.log('  Options: { download: true/false, format: "json"/"html", sendToBackend: true/false, silent: true/false }');
    console.log('');
    console.log('%ccheckTradingHealth()', 'color: #10b981; font-weight: bold;');
    console.log('  Quick health check - shows summary in console');
    console.log('');
    console.log('%cdownloadDiagnosticJSON()', 'color: #10b981; font-weight: bold;');
    console.log('  Download diagnostic report as JSON file');
    console.log('');
    console.log('%cdownloadDiagnosticHTML()', 'color: #10b981; font-weight: bold;');
    console.log('  Download diagnostic report as HTML file');
    console.log('');
    console.log('%csendDiagnosticReport()', 'color: #10b981; font-weight: bold;');
    console.log('  Send diagnostic report to backend API');
    console.log('');
    console.log('%cgetDiagnosticStatus()', 'color: #10b981; font-weight: bold;');
    console.log('  Get current diagnostic status');
    console.log('');
    console.log('%ctoggleAutoReporting(enabled)', 'color: #10b981; font-weight: bold;');
    console.log('  Toggle automatic reporting (pass true/false or omit to toggle)');
    console.log('');
    console.log('%cdiagnosticHelp()', 'color: #10b981; font-weight: bold;');
    console.log('  Show this help message');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  };

  // Log help on setup - only in development
  if (import.meta.env.DEV) {
    console.log('%c🔧 Trading Dashboard Diagnostics loaded!', 'color: #a78bfa; font-weight: bold; font-size: 14px;');
    console.log('Type %cdiagnosticHelp()%c for available commands', 'color: #10b981; font-weight: bold;', 'color: inherit;');
  }
}

