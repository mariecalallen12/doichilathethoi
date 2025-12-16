<script setup>
import Card from '../ui/Card.vue';

const props = defineProps({
  kpis: {
    type: Object,
    default: () => ({
      totalRevenue: { value: 1247832, change: 15.3 },
      activeUsers: { value: 8429, change: 8.2 },
      totalTrades: { value: 47293, change: 24.7 },
      conversionRate: { value: 12.8, change: 0.7 },
    }),
  },
});
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    <Card v-for="(kpi, key) in kpis" :key="key" class="relative overflow-hidden">
      <div>
        <p class="text-white/60 text-sm mb-1">{{ key === 'totalRevenue' ? 'Tổng doanh thu' : key === 'activeUsers' ? 'Người dùng hoạt động' : key === 'totalTrades' ? 'Tổng giao dịch' : 'Tỷ lệ chuyển đổi' }}</p>
        <p class="text-3xl font-bold text-white mb-2">
          {{ key === 'conversionRate' ? `${kpi.value}%` : key === 'totalRevenue' ? `$${kpi.value.toLocaleString()}` : kpi.value.toLocaleString() }}
        </p>
        <div class="flex items-center gap-2">
          <i :class="['fas', kpi.change >= 0 ? 'fa-arrow-up text-green-400' : 'fa-arrow-down text-red-400', 'text-xs']"></i>
          <span :class="['text-sm font-medium', kpi.change >= 0 ? 'text-green-400' : 'text-red-400']">
            {{ Math.abs(kpi.change) }}%
          </span>
        </div>
      </div>
    </Card>
  </div>
</template>

