<template>
  <Card class="p-6">
    <h3 class="text-lg font-bold text-white mb-4 flex items-center">
      <i class="fas fa-chart-line mr-2 text-purple-400"></i>
      Health Trends
    </h3>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-green-500/20 border border-green-500/30 rounded-lg p-4">
        <div class="text-white/60 text-sm mb-1">Healthy</div>
        <div class="text-2xl font-bold text-green-400">{{ stats.healthy }}</div>
      </div>
      <div class="bg-yellow-500/20 border border-yellow-500/30 rounded-lg p-4">
        <div class="text-white/60 text-sm mb-1">Degraded</div>
        <div class="text-2xl font-bold text-yellow-400">{{ stats.degraded }}</div>
      </div>
      <div class="bg-red-500/20 border border-red-500/30 rounded-lg p-4">
        <div class="text-white/60 text-sm mb-1">Unhealthy</div>
        <div class="text-2xl font-bold text-red-400">{{ stats.unhealthy }}</div>
      </div>
      <div class="bg-blue-500/20 border border-blue-500/30 rounded-lg p-4">
        <div class="text-white/60 text-sm mb-1">Total Reports</div>
        <div class="text-2xl font-bold text-blue-400">{{ stats.total }}</div>
      </div>
    </div>

    <!-- Simple Bar Chart -->
    <div class="space-y-2">
      <div
        v-for="(count, health) in stats"
        :key="health"
        v-if="health !== 'total'"
        class="flex items-center"
      >
        <div class="w-24 text-white/70 text-sm capitalize">{{ health }}</div>
        <div class="flex-1 bg-slate-700/50 rounded-full h-6 overflow-hidden relative">
          <div
            :class="[
              'h-full rounded-full transition-all duration-500',
              health === 'healthy' ? 'bg-green-500' :
              health === 'degraded' ? 'bg-yellow-500' :
              'bg-red-500'
            ]"
            :style="{ width: `${(count / stats.total) * 100}%` }"
          ></div>
          <span class="absolute inset-0 flex items-center justify-center text-xs text-white font-medium">
            {{ count }} ({{ Math.round((count / stats.total) * 100) }}%)
          </span>
        </div>
      </div>
    </div>

    <!-- Time Range Selector -->
    <div class="mt-6 flex items-center gap-2">
      <label class="text-white/80 text-sm">Time Range:</label>
      <select
        v-model="timeRange"
        @change="updateStats"
        class="px-3 py-1 bg-slate-700/50 border border-slate-600 rounded text-white text-sm"
      >
        <option value="24h">Last 24 Hours</option>
        <option value="7d">Last 7 Days</option>
        <option value="30d">Last 30 Days</option>
        <option value="all">All Time</option>
      </select>
    </div>
  </Card>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import Card from '../ui/Card.vue';
import axios from 'axios';

const props = defineProps({
  reports: {
    type: Array,
    default: () => [],
  },
});

const timeRange = ref('7d');
const stats = ref({
  healthy: 0,
  degraded: 0,
  unhealthy: 0,
  total: 0,
});

const updateStats = () => {
  const now = new Date();
  let cutoffDate = new Date();

  switch (timeRange.value) {
    case '24h':
      cutoffDate.setHours(now.getHours() - 24);
      break;
    case '7d':
      cutoffDate.setDate(now.getDate() - 7);
      break;
    case '30d':
      cutoffDate.setDate(now.getDate() - 30);
      break;
    case 'all':
      cutoffDate = new Date(0);
      break;
  }

  const filteredReports = props.reports.filter(r => {
    const reportDate = new Date(r.created_at);
    return reportDate >= cutoffDate;
  });

  stats.value = {
    healthy: filteredReports.filter(r => r.overall_health === 'healthy').length,
    degraded: filteredReports.filter(r => r.overall_health === 'degraded').length,
    unhealthy: filteredReports.filter(r => r.overall_health === 'unhealthy').length,
    total: filteredReports.length,
  };
};

watch(() => props.reports, () => {
  updateStats();
}, { deep: true });

onMounted(() => {
  updateStats();
});
</script>

