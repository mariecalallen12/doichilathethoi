/**
 * Report Generator - Tạo báo cáo diagnostic dưới dạng JSON và HTML
 */

import { collectAllDiagnostics } from './tradingDiagnostics';

/**
 * Tạo báo cáo JSON
 */
export async function generateJSONReport(wsStore = null) {
  const diagnostics = await collectAllDiagnostics(wsStore);
  
  const report = {
    version: '1.0',
    generatedAt: diagnostics.timestamp,
    url: diagnostics.url,
    userAgent: diagnostics.userAgent,
    collectionDuration: diagnostics.collectionDuration,
    summary: {
      authStatus: diagnostics.auth?.hasToken ? 'authenticated' : 'not_authenticated',
      apiHealth: diagnostics.api?.overallHealth || 'unknown',
      wsConnected: diagnostics.websocket?.connected || false,
      emptyComponents: Object.entries(diagnostics.components || {})
        .filter(([_, comp]) => comp?.isEmpty)
        .map(([key]) => key),
      recommendationsCount: diagnostics.recommendations?.length || 0,
    },
    diagnostics,
  };

  return JSON.stringify(report, null, 2);
}

/**
 * Tạo báo cáo HTML
 */
export async function generateHTMLReport(wsStore = null) {
  const diagnostics = await collectAllDiagnostics(wsStore);
  
  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#3b82f6';
      default: return '#6b7280';
    }
  };

  const formatStatus = (status) => {
    const statusMap = {
      healthy: { text: 'Khỏe mạnh', color: '#10b981' },
      degraded: { text: 'Suy giảm', color: '#f59e0b' },
      unhealthy: { text: 'Không hoạt động', color: '#ef4444' },
      unknown: { text: 'Không xác định', color: '#6b7280' },
    };
    const s = statusMap[status] || statusMap.unknown;
    return `<span style="color: ${s.color}; font-weight: bold;">${s.text}</span>`;
  };

  const html = `
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Trading Dashboard Diagnostic Report</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      background: #0f172a;
      color: #e2e8f0;
      padding: 20px;
      line-height: 1.6;
    }
    .container { max-width: 1200px; margin: 0 auto; }
    h1 {
      color: #a78bfa;
      margin-bottom: 10px;
      font-size: 2rem;
    }
    .meta {
      background: #1e293b;
      padding: 15px;
      border-radius: 8px;
      margin-bottom: 20px;
      border-left: 4px solid #8b5cf6;
    }
    .meta-item {
      margin: 5px 0;
      font-size: 0.9rem;
    }
    .section {
      background: #1e293b;
      padding: 20px;
      border-radius: 8px;
      margin-bottom: 20px;
      border: 1px solid #334155;
    }
    .section-title {
      color: #a78bfa;
      font-size: 1.3rem;
      margin-bottom: 15px;
      padding-bottom: 10px;
      border-bottom: 2px solid #334155;
    }
    .status-badge {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 0.85rem;
      font-weight: 600;
      margin: 5px 5px 5px 0;
    }
    .status-healthy { background: #065f46; color: #6ee7b7; }
    .status-degraded { background: #78350f; color: #fcd34d; }
    .status-unhealthy { background: #7f1d1d; color: #fca5a5; }
    .status-unknown { background: #374151; color: #9ca3af; }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
    }
    th, td {
      padding: 10px;
      text-align: left;
      border-bottom: 1px solid #334155;
    }
    th {
      background: #0f172a;
      color: #a78bfa;
      font-weight: 600;
    }
    tr:hover { background: #1e293b; }
    .code-block {
      background: #0f172a;
      padding: 15px;
      border-radius: 6px;
      overflow-x: auto;
      font-family: 'Courier New', monospace;
      font-size: 0.85rem;
      border: 1px solid #334155;
      margin: 10px 0;
    }
    .recommendation {
      background: #1e293b;
      padding: 15px;
      border-radius: 6px;
      margin: 10px 0;
      border-left: 4px solid;
    }
    .recommendation-high { border-left-color: #ef4444; }
    .recommendation-medium { border-left-color: #f59e0b; }
    .recommendation-low { border-left-color: #3b82f6; }
    .recommendation-title {
      font-weight: 600;
      margin-bottom: 5px;
      color: #a78bfa;
    }
    .recommendation-category {
      font-size: 0.85rem;
      color: #94a3b8;
      margin-bottom: 5px;
    }
    .recommendation-solution {
      color: #cbd5e1;
      margin-top: 8px;
      padding-top: 8px;
      border-top: 1px solid #334155;
    }
    .empty-state {
      color: #94a3b8;
      font-style: italic;
      padding: 20px;
      text-align: center;
    }
    .error-text {
      color: #f87171;
      font-family: monospace;
      font-size: 0.9rem;
    }
    .success-text {
      color: #34d399;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>📊 Trading Dashboard Diagnostic Report</h1>
    
    <div class="meta">
      <div class="meta-item"><strong>Thời gian:</strong> ${new Date(diagnostics.timestamp).toLocaleString('vi-VN')}</div>
      <div class="meta-item"><strong>URL:</strong> ${diagnostics.url}</div>
      <div class="meta-item"><strong>User Agent:</strong> ${diagnostics.userAgent}</div>
      <div class="meta-item"><strong>Thời gian thu thập:</strong> ${diagnostics.collectionDuration}ms</div>
    </div>

    <!-- Summary -->
    <div class="section">
      <h2 class="section-title">📋 Tóm tắt</h2>
      <div>
        <span class="status-badge ${diagnostics.auth?.hasToken ? 'status-healthy' : 'status-unhealthy'}">
          Auth: ${diagnostics.auth?.hasToken ? 'Đã đăng nhập' : 'Chưa đăng nhập'}
        </span>
        <span class="status-badge status-${diagnostics.api?.overallHealth || 'unknown'}">
          API: ${formatStatus(diagnostics.api?.overallHealth || 'unknown')}
        </span>
        <span class="status-badge ${diagnostics.websocket?.connected ? 'status-healthy' : 'status-degraded'}">
          WebSocket: ${diagnostics.websocket?.connected ? 'Đã kết nối' : 'Chưa kết nối'}
        </span>
      </div>
      <div style="margin-top: 15px;">
        <strong>Component trống:</strong> 
        ${Object.entries(diagnostics.components || {})
          .filter(([_, comp]) => comp?.isEmpty)
          .map(([key]) => key)
          .join(', ') || 'Không có'}
      </div>
      <div style="margin-top: 10px;">
        <strong>Số lượng khuyến nghị:</strong> ${diagnostics.recommendations?.length || 0}
      </div>
    </div>

    <!-- Recommendations -->
    ${diagnostics.recommendations && diagnostics.recommendations.length > 0 ? `
    <div class="section">
      <h2 class="section-title">💡 Khuyến nghị</h2>
      ${diagnostics.recommendations.map(rec => `
        <div class="recommendation recommendation-${rec.severity}">
          <div class="recommendation-title">${rec.issue}</div>
          <div class="recommendation-category">Category: ${rec.category} | Severity: ${rec.severity}</div>
          <div class="recommendation-solution"><strong>Giải pháp:</strong> ${rec.solution}</div>
        </div>
      `).join('')}
    </div>
    ` : ''}

    <!-- Authentication -->
    <div class="section">
      <h2 class="section-title">🔐 Authentication</h2>
      ${diagnostics.auth?.error ? `
        <div class="error-text">Lỗi: ${diagnostics.auth.error}</div>
      ` : `
        <table>
          <tr><th>Thuộc tính</th><th>Giá trị</th></tr>
          <tr><td>Có token</td><td class="${diagnostics.auth.hasToken ? 'success-text' : 'error-text'}">${diagnostics.auth.hasToken ? 'Có' : 'Không'}</td></tr>
          <tr><td>Loại token</td><td>${diagnostics.auth.tokenType || 'N/A'}</td></tr>
          <tr><td>Độ dài token</td><td>${diagnostics.auth.tokenLength}</td></tr>
          <tr><td>Token preview</td><td>${diagnostics.auth.tokenPreview || 'N/A'}</td></tr>
          <tr><td>Hết hạn lúc</td><td>${diagnostics.auth.expiresAt || 'N/A'}</td></tr>
          <tr><td>Đã hết hạn</td><td class="${diagnostics.auth.isExpired ? 'error-text' : 'success-text'}">${diagnostics.auth.isExpired ? 'Có' : diagnostics.auth.isExpired === null ? 'Không xác định' : 'Không'}</td></tr>
          <tr><td>User ID</td><td>${diagnostics.auth.userId || 'N/A'}</td></tr>
        </table>
      `}
    </div>

    <!-- API Health -->
    <div class="section">
      <h2 class="section-title">🌐 API Health</h2>
      ${diagnostics.api?.error ? `
        <div class="error-text">Lỗi: ${diagnostics.api.error}</div>
      ` : `
        <div style="margin-bottom: 15px;">
          <strong>Base URL:</strong> ${diagnostics.api.baseUrl}<br>
          <strong>Trạng thái tổng thể:</strong> ${formatStatus(diagnostics.api.overallHealth)}
        </div>
        <table>
          <tr>
            <th>Endpoint</th>
            <th>Status</th>
            <th>Duration (ms)</th>
            <th>Has Data</th>
            <th>Data Preview</th>
          </tr>
          ${Object.entries(diagnostics.api.endpoints || {}).map(([endpoint, data]) => `
            <tr>
              <td>${endpoint}</td>
              <td class="${data.ok ? 'success-text' : 'error-text'}">
                ${data.status || 'N/A'} ${data.statusText || data.error || ''}
              </td>
              <td>${data.duration || 'N/A'}</td>
              <td class="${data.hasData ? 'success-text' : 'error-text'}">${data.hasData ? 'Có' : 'Không'}</td>
              <td style="font-size: 0.85rem;">${data.dataPreview || 'N/A'}</td>
            </tr>
          `).join('')}
        </table>
        ${diagnostics.api.errors && diagnostics.api.errors.length > 0 ? `
          <div style="margin-top: 15px;">
            <strong style="color: #f87171;">Lỗi:</strong>
            <ul style="margin-top: 5px;">
              ${diagnostics.api.errors.map(err => `<li>${err.endpoint}: ${err.status || err.error} - ${err.statusText || err.message || ''}</li>`).join('')}
            </ul>
          </div>
        ` : ''}
      `}
    </div>

    <!-- WebSocket -->
    <div class="section">
      <h2 class="section-title">🔌 WebSocket</h2>
      ${diagnostics.websocket?.error ? `
        <div class="error-text">Lỗi: ${diagnostics.websocket.error}</div>
      ` : `
        <table>
          <tr><th>Thuộc tính</th><th>Giá trị</th></tr>
          <tr><td>Đã kết nối</td><td class="${diagnostics.websocket.connected ? 'success-text' : 'error-text'}">${diagnostics.websocket.connected ? 'Có' : 'Không'}</td></tr>
          <tr><td>Số lần reconnect</td><td>${diagnostics.websocket.reconnectAttempts || 0}</td></tr>
          <tr><td>Latency (ms)</td><td>${diagnostics.websocket.lastLatencyMs || 'N/A'}</td></tr>
          <tr><td>Lỗi</td><td class="error-text">${diagnostics.websocket.error || 'Không có'}</td></tr>
        </table>
      `}
    </div>

    <!-- Components -->
    <div class="section">
      <h2 class="section-title">🧩 Components</h2>
      <table>
        <tr>
          <th>Component</th>
          <th>Trạng thái</th>
          <th>Số element</th>
          <th>Độ dài text</th>
        </tr>
        ${Object.entries(diagnostics.components || {}).map(([key, comp]) => `
          <tr>
            <td>${key}</td>
            <td class="${comp.isEmpty ? 'error-text' : 'success-text'}">
              ${comp.isEmpty ? 'Trống' : 'Có nội dung'}
            </td>
            <td>${comp.elementCount || 0}</td>
            <td>${comp.textLength || 0}</td>
          </tr>
        `).join('')}
      </table>
    </div>

    <!-- Network -->
    <div class="section">
      <h2 class="section-title">📡 Network</h2>
      ${diagnostics.network?.error ? `
        <div class="error-text">Lỗi: ${diagnostics.network.error}</div>
      ` : diagnostics.network?.available === false ? `
        <div class="empty-state">Performance API không khả dụng</div>
      ` : `
        <div style="margin-bottom: 15px;">
          <strong>Tổng requests:</strong> ${diagnostics.network.totalRequests || 0}<br>
          <strong>API requests:</strong> ${diagnostics.network.apiRequests || 0}<br>
          <strong>Failed requests:</strong> <span class="error-text">${diagnostics.network.failedRequests || 0}</span>
        </div>
        ${diagnostics.network.failed && diagnostics.network.failed.length > 0 ? `
          <div style="margin-top: 15px;">
            <strong style="color: #f87171;">Failed Requests:</strong>
            <ul style="margin-top: 5px;">
              ${diagnostics.network.failed.slice(0, 10).map(req => `
                <li>${req.name} - Status: ${req.status || 'N/A'}</li>
              `).join('')}
            </ul>
          </div>
        ` : ''}
      `}
    </div>

    <!-- Bundles -->
    <div class="section">
      <h2 class="section-title">📦 Bundles</h2>
      ${diagnostics.bundles?.error ? `
        <div class="error-text">Lỗi: ${diagnostics.bundles.error}</div>
      ` : `
        <div style="margin-bottom: 15px;">
          <strong>Scripts:</strong> ${diagnostics.bundles.scripts?.loaded || 0}/${diagnostics.bundles.scripts?.total || 0} loaded
          ${diagnostics.bundles.scripts?.failed > 0 ? `<span class="error-text">(${diagnostics.bundles.scripts.failed} failed)</span>` : ''}<br>
          <strong>Stylesheets:</strong> ${diagnostics.bundles.stylesheets?.loaded || 0}/${diagnostics.bundles.stylesheets?.total || 0} loaded
          ${diagnostics.bundles.stylesheets?.failed > 0 ? `<span class="error-text">(${diagnostics.bundles.stylesheets.failed} failed)</span>` : ''}
        </div>
        ${diagnostics.bundles.failedResources && diagnostics.bundles.failedResources.length > 0 ? `
          <div style="margin-top: 15px;">
            <strong style="color: #f87171;">Failed Resources:</strong>
            <ul style="margin-top: 5px;">
              ${diagnostics.bundles.failedResources.map(res => `
                <li>${res.name} - Status: ${res.status}</li>
              `).join('')}
            </ul>
          </div>
        ` : ''}
      `}
    </div>

    <!-- Console Errors -->
    <div class="section">
      <h2 class="section-title">⚠️ Console</h2>
      ${diagnostics.console?.note ? `
        <div class="empty-state">${diagnostics.console.note}</div>
      ` : `
        <div>
          <strong>Errors:</strong> ${diagnostics.console.errors?.length || 0}<br>
          <strong>Warnings:</strong> ${diagnostics.console.warnings?.length || 0}<br>
          <strong>Info:</strong> ${diagnostics.console.info?.length || 0}
        </div>
        ${diagnostics.console.errors && diagnostics.console.errors.length > 0 ? `
          <div style="margin-top: 15px;">
            <strong style="color: #f87171;">Errors:</strong>
            <div class="code-block">
              ${diagnostics.console.errors.slice(0, 10).map(err => `${err.timestamp}: ${err.message}`).join('<br>')}
            </div>
          </div>
        ` : ''}
      `}
    </div>

    <!-- Raw Data -->
    <div class="section">
      <h2 class="section-title">🔍 Raw Data</h2>
      <div class="code-block">
        <pre>${JSON.stringify(diagnostics, null, 2)}</pre>
      </div>
    </div>

    <div style="text-align: center; margin-top: 40px; color: #94a3b8; font-size: 0.9rem;">
      Generated by Trading Dashboard Diagnostic System
    </div>
  </div>
</body>
</html>
  `;

  return html;
}

/**
 * Download report as file
 */
export function downloadReport(content, filename, mimeType = 'application/json') {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Gửi report lên backend
 */
export async function sendReportToBackend(report, wsStore = null) {
  try {
    const API_BASE_URL = window.location.origin;
    const token = localStorage.getItem('auth_token') || localStorage.getItem('access_token');
    
    const response = await fetch(`${API_BASE_URL}/api/diagnostics/trading-report`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
      },
      body: JSON.stringify({
        report: typeof report === 'string' ? JSON.parse(report) : report,
        timestamp: new Date().toISOString(),
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to send report: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error sending report to backend:', error);
    throw error;
  }
}

