<template>
  <div class="glass-panel rounded-lg p-6">
    <h3 class="text-lg font-bold text-white mb-4 flex items-center">
      <i class="fas fa-history mr-2 text-purple-400"></i>
      Lịch Sử Rút Tiền
    </h3>

    <div v-if="loading" class="space-y-3">
      <div v-for="i in 5" :key="i" class="h-16 bg-slate-800/50 rounded-lg animate-pulse"></div>
    </div>

    <div v-else-if="withdrawals.length === 0" class="text-center py-8 text-purple-300">
      <i class="fas fa-inbox text-4xl mb-2"></i>
      <p>Chưa có yêu cầu rút tiền nào</p>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="withdrawal in withdrawals"
        :key="withdrawal.id"
        class="p-4 bg-slate-800/50 rounded-lg hover:bg-slate-800/70 transition-all"
      >
        <div class="flex items-center justify-between">
          <div class="flex-1">
            <div class="flex items-center space-x-3 mb-2">
              <div class="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <i class="fas fa-arrow-up text-blue-300"></i>
              </div>
              <div>
                <div class="text-white font-medium">{{ formatAmount(withdrawal.amount, withdrawal.currency) }}</div>
                <div class="text-purple-300 text-xs">{{ formatDate(withdrawal.createdAt) }}</div>
              </div>
            </div>
            <div class="text-purple-300 text-xs ml-13">
              {{ withdrawal.method === 'crypto_withdrawal' ? 'Rút về ví crypto' : 'Rút về tài khoản ngân hàng' }}
            </div>
          </div>
          <StatusBadge :status="withdrawal.status" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useWithdrawStore } from '../../../stores/withdraw';
import StatusBadge from '../shared/StatusBadge.vue';
import { formatCurrency, formatNumber } from '../../../services/utils/formatters';

const withdrawStore = useWithdrawStore();
const withdrawals = ref([]);
const loading = ref(true);

const formatAmount = (amount, currency) => {
  if (currency === 'VND') {
    return `${formatNumber(amount)} ₫`;
  }
  return formatCurrency(amount, currency);
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

onMounted(async () => {
  try {
    loading.value = true;
    const response = await withdrawStore.fetchWithdrawals({ limit: 10 });
    withdrawals.value = response.data?.withdrawals || [];
  } catch (error) {
    console.error('Failed to fetch withdrawals:', error);
    withdrawals.value = [];
  } finally {
    loading.value = false;
  }
});
</script>

