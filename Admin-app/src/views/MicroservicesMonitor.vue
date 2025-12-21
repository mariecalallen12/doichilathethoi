<template>
  <div class="microservices-monitor">
    <div class="monitor-header">
      <h1>
        <i class="fas fa-network-wired"></i>
        Microservices Health Monitor
      </h1>
      <div class="header-actions">
        <button @click="refreshAll" class="btn-refresh" :disabled="loading">
          <i class="fas fa-sync-alt" :class="{ spinning: loading }"></i>
          Refresh All
        </button>
        <div class="auto-refresh">
          <label>
            <input type="checkbox" v-model="autoRefresh" />
            Auto Refresh (30s)
          </label>
        </div>
      </div>
    </div>

    <!-- Overall System Status -->
    <div class="system-overview">
      <div class="overview-card" :class="overallStatus.class">
        <div class="status-icon">
          <i :class="overallStatus.icon"></i>
        </div>
        <div class="status-info">
          <h3>{{ overallStatus.text }}</h3>
          <p>{{ healthyServices }}/{{ totalServices }} services healthy</p>
        </div>
      </div>
    </div>

    <!-- Services Grid -->
    <div class="services-grid">
      <!-- Backend API -->
      <div class="service-card" :class="getServiceClass(backendHealth)">
        <div class="service-header">
          <div class="service-title">
            <i class="fas fa-server"></i>
            <h3>Backend API</h3>
          </div>
          <div class="service-status">
            <span class="status-badge" :class="getStatusBadge(backendHealth)">
              {{ getStatusText(backendHealth) }}
            </span>
          </div>
        </div>
        <div class="service-body">
          <div class="service-info">
            <div class="info-item">
              <span class="label">Endpoint:</span>
              <span class="value">{{ backendHealth?.endpoint || 'http://localhost:8000' }}</span>
            </div>
            <div class="info-item">
              <span class="label">Response Time:</span>
              <span class="value">{{ backendHealth?.responseTime || 'N/A' }}ms</span>
            </div>
            <div class="info-item">
              <span class="label">Uptime:</span>
              <span class="value">{{ backendHealth?.uptime || 'N/A' }}</span>
            </div>
            <div class="info-item">
              <span class="label">Version:</span>
              <span class="value">{{ backendHealth?.version || 'N/A' }}</span>
            </div>
          </div>
          <div class="service-metrics" v-if="backendHealth?.metrics">
            <div class="metric">
              <span class="metric-label">CPU:</span>
              <div class="metric-bar">
                <div class="metric-fill" :style="{ width: backendHealth.metrics.cpu + '%' }"></div>
              </div>
              <span class="metric-value">{{ backendHealth.metrics.cpu }}%</span>
            </div>
            <div class="metric">
              <span class="metric-label">Memory:</span>
              <div class="metric-bar">
                <div class="metric-fill" :style="{ width: backendHealth.metrics.memory + '%' }"></div>
              </div>
              <span class="metric-value">{{ backendHealth.metrics.memory }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- TradingSystemAPI -->
      <div class="service-card" :class="getServiceClass(tradingHealth)">
        <div class="service-header">
          <div class="service-title">
            <i class="fas fa-chart-line"></i>
            <h3>TradingSystem API</h3>
          </div>
          <div class="service-status">
            <span class="status-badge" :class="getStatusBadge(tradingHealth)">
              {{ getStatusText(tradingHealth) }}
            </span>
          </div>
        </div>
        <div class="service-body">
          <div class="service-info">
            <div class="info-item">
              <span class="label">Endpoint:</span>
              <span class="value">{{ tradingHealth?.endpoint || 'http://localhost:8001' }}</span>
            </div>
            <div class="info-item">
              <span class="label">Response Time:</span>
              <span class="value">{{ tradingHealth?.responseTime || 'N/A' }}ms</span>
            </div>
            <div class="info-item">
              <span class="label">Active Streams:</span>
              <span class="value">{{ tradingHealth?.activeStreams || 0 }}</span>
            </div>
            <div class="info-item">
              <span class="label">Market Status:</span>
              <span class="value">{{ tradingHealth?.marketStatus || 'N/A' }}</span>
            </div>
          </div>
          <div class="service-metrics" v-if="tradingHealth?.metrics">
            <div class="metric">
              <span class="metric-label">CPU:</span>
              <div class="metric-bar">
                <div class="metric-fill" :style="{ width: tradingHealth.metrics.cpu + '%' }"></div>
              </div>
              <span class="metric-value">{{ tradingHealth.metrics.cpu }}%</span>
            </div>
            <div class="metric">
              <span class="metric-label">Memory:</span>
              <div class="metric-bar">
                <div class="metric-fill" :style="{ width: tradingHealth.metrics.memory + '%' }"></div>
              </div>
              <span class="metric-value">{{ tradingHealth.metrics.memory }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Redis -->
      <div class="service-card" :class="getServiceClass(redisHealth)">
        <div class="service-header">
          <div class="service-title">
            <i class="fas fa-database"></i>
            <h3>Redis Cache</h3>
          </div>
          <div class="service-status">
            <span class="status-badge" :class="getStatusBadge(redisHealth)">
              {{ getStatusText(redisHealth) }}
            </span>
          </div>
        </div>
        <div class="service-body">
          <div class="service-info">
            <div class="info-item">
              <span class="label">Host:</span>
              <span class="value">{{ redisHealth?.host || 'redis:6379' }}</span>
            </div>
            <div class="info-item">
              <span class="label">Connections:</span>
              <span class="value">{{ redisHealth?.connections || 'N/A' }}</span>
            </div>
            <div class="info-item">
              <span class="label">Keys:</span>
              <span class="value">{{ redisHealth?.keys || 'N/A' }}</span>
            </div>
            <div class="info-item">
              <span class="label">Memory Used:</span>
              <span class="value">{{ redisHealth?.memoryUsed || 'N/A' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- PostgreSQL -->
      <div class="service-card" :class="getServiceClass(dbHealth)">
        <div class="service-header">
          <div class="service-title">
            <i class="fas fa-database"></i>
            <h3>PostgreSQL DB</h3>
          </div>
          <div class="service-status">
            <span class="status-badge" :class="getStatusBadge(dbHealth)">
              {{ getStatusText(dbHealth) }}
            </span>
          </div>
        </div>
        <div class="service-body">
          <div class="service-info">
            <div class="info-item">
              <span class="label">Host:</span>
              <span class="value">{{ dbHealth?.host || 'db:5432' }}</span>
            </div>
            <div class="info-item">
              <span class="label">Active Connections:</span>
              <span class="value">{{ dbHealth?.connections || 'N/A' }}</span>
            </div>
            <div class="info-item">
              <span class="label">DB Size:</span>
              <span class="value">{{ dbHealth?.size || 'N/A' }}</span>
            </div>
            <div class="info-item">
              <span class="label">Tables:</span>
              <span class="value">{{ dbHealth?.tables || 'N/A' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- WebSocket Connections -->
    <div class="websocket-section">
      <h2>
        <i class="fas fa-plug"></i>
        Active WebSocket Connections
      </h2>
      <div class="ws-stats">
        <div class="ws-stat-card">
          <i class="fas fa-users"></i>
          <div class="ws-stat-info">
            <h4>Total Connections</h4>
            <p class="ws-stat-value">{{ wsStats.total }}</p>
          </div>
        </div>
        <div class="ws-stat-card">
          <i class="fas fa-chart-line"></i>
          <div class="ws-stat-info">
            <h4>Market Streams</h4>
            <p class="ws-stat-value">{{ wsStats.market }}</p>
          </div>
        </div>
        <div class="ws-stat-card">
          <i class="fas fa-exchange-alt"></i>
          <div class="ws-stat-info">
            <h4>Trading Streams</h4>
            <p class="ws-stat-value">{{ wsStats.trading }}</p>
          </div>
        </div>
        <div class="ws-stat-card">
          <i class="fas fa-bell"></i>
          <div class="ws-stat-info">
            <h4>Notification Channels</h4>
            <p class="ws-stat-value">{{ wsStats.notifications }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Service Logs -->
    <div class="logs-section">
      <div class="logs-header">
        <h2>
          <i class="fas fa-file-alt"></i>
          Recent Service Logs
        </h2>
        <select v-model="selectedLogService" class="log-filter">
          <option value="all">All Services</option>
          <option value="backend">Backend API</option>
          <option value="trading">Trading API</option>
          <option value="redis">Redis</option>
          <option value="db">PostgreSQL</option>
        </select>
      </div>
      <div class="logs-container">
        <div v-for="log in filteredLogs" :key="log.id" class="log-entry" :class="'log-' + log.level">
          <span class="log-time">{{ formatTime(log.timestamp) }}</span>
          <span class="log-service">{{ log.service }}</span>
          <span class="log-level">{{ log.level }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import axios from 'axios';

export default {
  name: 'MicroservicesMonitor',
  setup() {
    const loading = ref(false);
    const autoRefresh = ref(true);
    const backendHealth = ref(null);
    const tradingHealth = ref(null);
    const redisHealth = ref(null);
    const dbHealth = ref(null);
    const wsStats = ref({ total: 0, market: 0, trading: 0, notifications: 0 });
    const logs = ref([]);
    const selectedLogService = ref('all');
    let refreshInterval = null;

    const totalServices = computed(() => 4);
    const healthyServices = computed(() => {
      let count = 0;
      if (backendHealth.value?.status === 'healthy') count++;
      if (tradingHealth.value?.status === 'healthy') count++;
      if (redisHealth.value?.status === 'healthy') count++;
      if (dbHealth.value?.status === 'healthy') count++;
      return count;
    });

    const overallStatus = computed(() => {
      const ratio = healthyServices.value / totalServices.value;
      if (ratio === 1) {
        return { text: 'All Systems Operational', class: 'status-healthy', icon: 'fas fa-check-circle' };
      } else if (ratio >= 0.5) {
        return { text: 'Partial Outage', class: 'status-warning', icon: 'fas fa-exclamation-triangle' };
      } else {
        return { text: 'Major Outage', class: 'status-critical', icon: 'fas fa-times-circle' };
      }
    });

    const filteredLogs = computed(() => {
      if (selectedLogService.value === 'all') return logs.value;
      return logs.value.filter(log => log.service === selectedLogService.value);
    });

    const getServiceClass = (health) => {
      if (!health) return 'service-unknown';
      return `service-${health.status}`;
    };

    const getStatusBadge = (health) => {
      if (!health) return 'badge-unknown';
      return `badge-${health.status}`;
    };

    const getStatusText = (health) => {
      if (!health) return 'Unknown';
      return health.status.charAt(0).toUpperCase() + health.status.slice(1);
    };

    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString();
    };

    const checkBackendHealth = async () => {
      try {
        const start = Date.now();
        const response = await axios.get('/api/health');
        const responseTime = Date.now() - start;
        backendHealth.value = {
          status: 'healthy',
          endpoint: window.location.origin + '/api',
          responseTime,
          ...response.data
        };
      } catch (error) {
        backendHealth.value = {
          status: 'unhealthy',
          endpoint: window.location.origin + '/api',
          error: error.message
        };
      }
    };

    const checkTradingHealth = async () => {
      try {
        const start = Date.now();
        const response = await axios.get('/trading/health');
        const responseTime = Date.now() - start;
        tradingHealth.value = {
          status: 'healthy',
          endpoint: window.location.origin + '/trading',
          responseTime,
          ...response.data
        };
      } catch (error) {
        tradingHealth.value = {
          status: 'unhealthy',
          endpoint: window.location.origin + '/trading',
          error: error.message
        };
      }
    };

    const checkRedisHealth = async () => {
      try {
        const response = await axios.get('/api/monitoring/redis/health');
        redisHealth.value = {
          status: 'healthy',
          ...response.data
        };
      } catch (error) {
        redisHealth.value = {
          status: 'unhealthy',
          error: error.message
        };
      }
    };

    const checkDbHealth = async () => {
      try {
        const response = await axios.get('/api/monitoring/db/health');
        dbHealth.value = {
          status: 'healthy',
          ...response.data
        };
      } catch (error) {
        dbHealth.value = {
          status: 'unhealthy',
          error: error.message
        };
      }
    };

    const fetchWebSocketStats = async () => {
      try {
        const response = await axios.get('/api/monitoring/websocket/stats');
        wsStats.value = response.data;
      } catch (error) {
        console.error('Failed to fetch WebSocket stats:', error);
      }
    };

    const fetchLogs = async () => {
      try {
        const response = await axios.get('/api/monitoring/logs', {
          params: { limit: 100 }
        });
        logs.value = response.data;
      } catch (error) {
        console.error('Failed to fetch logs:', error);
      }
    };

    const refreshAll = async () => {
      loading.value = true;
      try {
        await Promise.all([
          checkBackendHealth(),
          checkTradingHealth(),
          checkRedisHealth(),
          checkDbHealth(),
          fetchWebSocketStats(),
          fetchLogs()
        ]);
      } finally {
        loading.value = false;
      }
    };

    onMounted(() => {
      refreshAll();
      refreshInterval = setInterval(() => {
        if (autoRefresh.value) {
          refreshAll();
        }
      }, 30000);
    });

    onUnmounted(() => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    });

    return {
      loading,
      autoRefresh,
      backendHealth,
      tradingHealth,
      redisHealth,
      dbHealth,
      wsStats,
      logs,
      selectedLogService,
      totalServices,
      healthyServices,
      overallStatus,
      filteredLogs,
      getServiceClass,
      getStatusBadge,
      getStatusText,
      formatTime,
      refreshAll
    };
  }
};
</script>

<style scoped>
.microservices-monitor {
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  color: white;
}

.monitor-header h1 {
  font-size: 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.btn-refresh {
  padding: 0.75rem 1.5rem;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-refresh:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.auto-refresh label {
  color: white;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.system-overview {
  margin-bottom: 2rem;
}

.overview-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.status-icon i {
  font-size: 3rem;
}

.status-healthy .status-icon { color: #10b981; }
.status-warning .status-icon { color: #f59e0b; }
.status-critical .status-icon { color: #ef4444; }

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.service-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #d1d5db;
}

.service-healthy { border-left-color: #10b981; }
.service-unhealthy { border-left-color: #ef4444; }
.service-warning { border-left-color: #f59e0b; }

.service-header {
  padding: 1.5rem;
  background: #f9fafb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.service-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
}

.badge-healthy { background: #d1fae5; color: #065f46; }
.badge-unhealthy { background: #fee2e2; color: #991b1b; }
.badge-warning { background: #fed7aa; color: #92400e; }
.badge-unknown { background: #e5e7eb; color: #374151; }

.service-body {
  padding: 1.5rem;
}

.service-info {
  display: grid;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
}

.info-item .label {
  font-weight: 600;
  color: #6b7280;
}

.info-item .value {
  color: #111827;
}

.service-metrics {
  display: grid;
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.metric {
  display: grid;
  grid-template-columns: 60px 1fr 60px;
  align-items: center;
  gap: 1rem;
}

.metric-bar {
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #3b82f6);
  transition: width 0.3s;
}

.websocket-section, .logs-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.websocket-section h2, .logs-section h2 {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.ws-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.ws-stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: #f9fafb;
  border-radius: 8px;
}

.ws-stat-card i {
  font-size: 2rem;
  color: #667eea;
}

.ws-stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #111827;
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.log-filter {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
}

.logs-container {
  max-height: 400px;
  overflow-y: auto;
  background: #1f2937;
  border-radius: 8px;
  padding: 1rem;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
}

.log-entry {
  display: grid;
  grid-template-columns: 100px 120px 80px 1fr;
  gap: 1rem;
  padding: 0.5rem;
  border-bottom: 1px solid #374151;
  color: #d1d5db;
}

.log-time { color: #9ca3af; }
.log-service { color: #60a5fa; }
.log-level { font-weight: 600; }
.log-error .log-level { color: #ef4444; }
.log-warning .log-level { color: #f59e0b; }
.log-info .log-level { color: #10b981; }
.log-debug .log-level { color: #6b7280; }
</style>
