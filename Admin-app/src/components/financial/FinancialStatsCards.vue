<script setup>
import Card from '../ui/Card.vue';

const props = defineProps({
  stats: {
    type: Object,
    default: () => ({
      totalDeposits: 0,
      totalWithdrawals: 0,
      pendingDeposits: 0,
      pendingWithdrawals: 0,
    }),
  },
});
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    <Card class="relative overflow-hidden">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-white/60 text-sm mb-1">Tổng số tiền nạp</p>
          <p class="text-3xl font-bold text-white">${{ stats.totalDeposits.toLocaleString() }}</p>
        </div>
        <div class="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
          <i class="fas fa-arrow-down text-green-400 text-xl"></i>
        </div>
      </div>
    </Card>

    <Card class="relative overflow-hidden">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-white/60 text-sm mb-1">Tổng số tiền rút</p>
          <p class="text-3xl font-bold text-white">${{ stats.totalWithdrawals.toLocaleString() }}</p>
        </div>
        <div class="w-12 h-12 bg-red-500/20 rounded-lg flex items-center justify-center">
          <i class="fas fa-arrow-up text-red-400 text-xl"></i>
        </div>
      </div>
    </Card>

    <Card class="relative overflow-hidden">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-white/60 text-sm mb-1">Nạp tiền chờ xử lý</p>
          <p class="text-3xl font-bold text-white">${{ stats.pendingDeposits.toLocaleString() }}</p>
        </div>
        <div class="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center">
          <i class="fas fa-clock text-yellow-400 text-xl"></i>
        </div>
      </div>
    </Card>

    <Card class="relative overflow-hidden">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-white/60 text-sm mb-1">Rút tiền chờ xử lý</p>
          <p class="text-3xl font-bold text-white">${{ stats.pendingWithdrawals.toLocaleString() }}</p>
        </div>
        <div class="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center">
          <i class="fas fa-clock text-yellow-400 text-xl"></i>
        </div>
      </div>
    </Card>
  </div>
</template>

