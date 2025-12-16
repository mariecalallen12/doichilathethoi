<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import api from '../services/api';
import toastService from '../services/toast';
import DashboardStats from '../components/dashboard/DashboardStats.vue';
import SystemStatus from '../components/dashboard/SystemStatus.vue';
import SystemHealth from '../components/dashboard/SystemHealth.vue';
import RecentActivities from '../components/dashboard/RecentActivities.vue';

// Initialize with null/empty values - will be populated from API
const stats = ref({
  totalUsers: null,
  activeUsers: null,
  totalTrades: null,
  revenueToday: null,
});

const systemStatus = ref({
  uptime: null,
  systemLoad: null,
});

const services = ref([
  { name: 'Database', status: 'operational', icon: 'fa-database' },
  { name: 'API Services', status: 'active', icon: 'fa-server' },
  { name: 'Trading Engine', status: 'high-load', icon: 'fa-cogs' },
]);

const activities = ref([]);

const chartData = ref({
  labels: [],
  datasets: [
    {
      label: 'Trading Volume 24h',
      data: [],
    },
  ],
});

const loading = ref(false);
let refreshInterval = null;

const fetchDashboardData = async () => {
  loading.value = true;
  try {
    // Fetch dashboard stats
    const [dashboardResponse, platformStatsResponse, logsResponse, analyticsResponse] = await Promise.all([
      api.get('/api/admin/dashboard').catch(() => ({ data: {} })),
      api.get('/api/admin/platform/stats').catch(() => ({ data: {} })),
      api.get('/api/admin/logs', { limit: 10 }).catch(() => ({ data: { logs: [] } })),
      api.get('/api/admin/analytics').catch(() => ({ data: {} }))
    ]);
    
    // Update stats
    const dashboardData = dashboardResponse.data?.data || dashboardResponse.data || {};
    const platformData = platformStatsResponse.data?.data || platformStatsResponse.data || {};
    
    if (dashboardData.stats || platformData) {
      stats.value = {
        totalUsers: dashboardData.stats?.total_users || platformData.total_users || 0,
        activeUsers: dashboardData.stats?.active_users || platformData.active_users || 0,
        totalTrades: dashboardData.stats?.total_trades || platformData.total_trades || 0,
        revenueToday: dashboardData.stats?.revenue_today || platformData.revenue_today || 0,
      };
    }
    
    // Update system status
    if (platformData) {
      systemStatus.value = {
        uptime: platformData.uptime || 99.9,
        systemLoad: platformData.system_load || 45,
      };
    }
    
    // Update activities from logs
    const logsData = logsResponse.data?.data?.logs || logsResponse.data?.logs || [];
    if (logsData.length > 0) {
      activities.value = logsData.slice(0, 10).map(log => ({
        id: log.id,
        type: log.action_type || 'info',
        message: log.description || log.action_type,
        user: log.user_email || '',
        time: new Date(log.created_at).toLocaleString('vi-VN'),
        icon: 'fa-info-circle',
        color: 'text-blue-400',
      }));
    }
    
    // Update chart data from analytics
    const analyticsData = analyticsResponse.data?.data || analyticsResponse.data || {};
    if (analyticsData.trading_volume_chart) {
      chartData.value = analyticsData.trading_volume_chart;
    }
  } catch (error) {
    toastService.error('Không thể tải dữ liệu dashboard');
    console.error('Dashboard error:', error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchDashboardData();
  
  // Set up auto-refresh every 5 seconds
  refreshInterval = setInterval(() => {
    fetchDashboardData();
  }, 5000);
});

onBeforeUnmount(() => {
  // Clean up interval on component unmount
  if (refreshInterval) {
    clearInterval(refreshInterval);
    refreshInterval = null;
  }
});
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div>
      <h1 class="text-3xl font-bold text-white mb-2">Dashboard</h1>
      <p class="text-white/60">Tổng quan hệ thống và thống kê</p>
    </div>

    <!-- Stats Cards -->
    <DashboardStats :stats="stats" />

    <!-- Charts and Status -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Trading Volume Chart -->
      <div class="lg:col-span-2">
        <TradingVolumeChart :data="chartData" />
      </div>

      <!-- System Status -->
      <div class="space-y-6">
        <SystemStatus :uptime="systemStatus.uptime" :system-load="systemStatus.systemLoad" />
        <SystemHealth :services="services" />
      </div>
    </div>

    <!-- Recent Activities -->
    <RecentActivities :activities="activities" />
  </div>
</template>

