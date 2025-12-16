<script setup>
import { ref, watch } from 'vue';
import Card from '../ui/Card.vue';

const props = defineProps({
  stats: {
    type: Object,
    default: () => ({
      totalUsers: 0,
      activeUsers: 0,
      totalTrades: 0,
      revenueToday: 0,
    }),
  },
});

const activeUsers = ref(props.stats.activeUsers);

// Watch for prop changes to update active users
watch(() => props.stats.activeUsers, (newValue) => {
  activeUsers.value = newValue;
}, { immediate: true });
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- Total Users -->
    <Card class="relative overflow-hidden">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-white/60 text-sm mb-1">Tổng số người dùng</p>
          <p class="text-3xl font-bold text-white">{{ stats.totalUsers.toLocaleString() }}</p>
        </div>
        <div class="w-12 h-12 bg-primary/20 rounded-lg flex items-center justify-center">
          <i class="fas fa-users text-primary text-xl"></i>
        </div>
      </div>
    </Card>

    <!-- Active Users -->
    <Card class="relative overflow-hidden">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-white/60 text-sm mb-1">Người dùng hoạt động</p>
          <p class="text-3xl font-bold text-white">{{ activeUsers.toLocaleString() }}</p>
          <p class="text-xs text-green-300 mt-1">
            <i class="fas fa-circle text-[6px] animate-pulse"></i> Đang cập nhật
          </p>
        </div>
        <div class="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
          <i class="fas fa-user-check text-green-400 text-xl"></i>
        </div>
      </div>
    </Card>

    <!-- Total Trades -->
    <Card class="relative overflow-hidden">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-white/60 text-sm mb-1">Tổng số giao dịch</p>
          <p class="text-3xl font-bold text-white">{{ stats.totalTrades.toLocaleString() }}</p>
        </div>
        <div class="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
          <i class="fas fa-exchange-alt text-blue-400 text-xl"></i>
        </div>
      </div>
    </Card>

    <!-- Revenue Today -->
    <Card class="relative overflow-hidden">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-white/60 text-sm mb-1">Doanh thu hôm nay</p>
          <p class="text-3xl font-bold text-white">${{ stats.revenueToday.toLocaleString() }}</p>
        </div>
        <div class="w-12 h-12 bg-purple-primary/20 rounded-lg flex items-center justify-center">
          <i class="fas fa-dollar-sign text-purple-primary text-xl"></i>
        </div>
      </div>
    </Card>
  </div>
</template>

