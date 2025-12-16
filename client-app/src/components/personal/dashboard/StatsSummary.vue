<template>
  <div class="glass-panel rounded-lg p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-bold text-white flex items-center">
        <i class="fas fa-chart-line mr-2 text-purple-400"></i>
        Thống Kê Dòng Tiền
      </h3>
      <div v-if="loading" class="text-purple-300 text-xs">Đang tải...</div>
    </div>

    <div v-if="error" class="text-red-400 text-sm">
      {{ error }}
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-slate-800/50 rounded-lg p-4">
        <div class="text-purple-300 text-xs mb-1">Tổng Nạp</div>
        <div class="font-orbitron text-2xl font-bold text-green-400">
          {{ formatAmount(totalDeposits) }}
        </div>
        <div class="text-purple-300 text-xs mt-1">Số tiền đã nạp vào hệ thống</div>
      </div>

      <div class="bg-slate-800/50 rounded-lg p-4">
        <div class="text-purple-300 text-xs mb-1">Tổng Rút</div>
        <div class="font-orbitron text-2xl font-bold text-red-400">
          {{ formatAmount(totalWithdrawals) }}
        </div>
        <div class="text-purple-300 text-xs mt-1">Số tiền đã rút khỏi hệ thống</div>
      </div>

      <div class="bg-slate-800/50 rounded-lg p-4">
        <div class="text-purple-300 text-xs mb-1">Dòng Tiền Ròng</div>
        <div
          class="font-orbitron text-2xl font-bold"
          :class="netFlow >= 0 ? 'text-green-400' : 'text-red-400'"
        >
          {{ formatAmount(netFlow) }}
        </div>
        <div class="text-purple-300 text-xs mt-1">
          {{ netFlow >= 0 ? 'Tiền vào > tiền ra' : 'Tiền ra > tiền vào' }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { clientApi } from '../../../services/api/client';
import { formatNumber } from '../../../services/utils/formatters';

const totalDeposits = ref(0);
const totalWithdrawals = ref(0);
const netFlow = ref(0);
const loading = ref(false);
const error = ref('');

const formatAmount = (amount) => {
  return `${formatNumber(amount)} ₫`;
};

onMounted(async () => {
  try {
    loading.value = true;
    const dashboard = await clientApi.getDashboard();
    const data = dashboard.data || dashboard;
    const stats = data.stats || {};

    totalDeposits.value = stats.totalDeposits || 0;
    totalWithdrawals.value = stats.totalWithdrawals || 0;
    netFlow.value = stats.netFlow || (stats.totalDeposits || 0) - (stats.totalWithdrawals || 0);
  } catch (e) {
    console.error('Failed to load dashboard stats:', e);
    error.value = 'Không thể tải thống kê dòng tiền';
  } finally {
    loading.value = false;
  }
});
</script>

