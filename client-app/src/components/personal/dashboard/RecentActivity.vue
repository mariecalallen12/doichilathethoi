<template>
  <div class="glass-panel rounded-lg p-6">
    <div class="flex items-center justify-between mb-4">
      <div>
        <h3 class="text-lg font-bold text-white flex items-center">
          <i class="fas fa-stream mr-2 text-purple-400"></i>
          Hoạt Động Gần Đây
        </h3>
        <div v-if="lastDepositAt || lastWithdrawalAt" class="mt-1 text-purple-300 text-xs space-y-0.5">
          <div v-if="lastDepositAt">
            Lần nạp gần nhất:
            <span class="text-white">{{ formatDate(lastDepositAt) }}</span>
          </div>
          <div v-if="lastWithdrawalAt">
            Lần rút gần nhất:
            <span class="text-white">{{ formatDate(lastWithdrawalAt) }}</span>
          </div>
        </div>
      </div>
      <router-link
        to="/personal/transactions"
        class="text-purple-300 hover:text-white text-sm transition-colors"
      >
        Xem tất cả <i class="fas fa-arrow-right ml-1"></i>
      </router-link>
    </div>

    <div v-if="loading" class="space-y-3">
      <div v-for="i in 5" :key="i" class="h-16 bg-slate-800/50 rounded-lg animate-pulse"></div>
    </div>

    <div v-else-if="transactions.length === 0" class="text-center py-8 text-purple-300">
      <i class="fas fa-inbox text-4xl mb-2"></i>
      <p>Chưa có giao dịch nào</p>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="transaction in transactions"
        :key="transaction.id"
        class="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg hover:bg-slate-800/70 transition-all cursor-pointer"
        @click="$emit('view-detail', transaction)"
      >
        <div class="flex items-center space-x-4 flex-1">
          <div
            :class="[
              'w-12 h-12 rounded-lg flex items-center justify-center',
              getTransactionIconBg(transaction.type)
            ]"
          >
            <i :class="[getTransactionIcon(transaction.type), 'text-xl']"></i>
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-white font-medium mb-1">{{ getTransactionTypeLabel(transaction.type) }}</div>
            <div class="text-purple-300 text-xs">
              {{ formatDate(transaction.createdAt) }}
            </div>
          </div>
        </div>
        <div class="text-right">
          <div
            :class="[
              'font-orbitron font-bold text-lg',
              transaction.type === 'deposit' ? 'text-green-400' : 'text-red-400'
            ]"
          >
            {{ transaction.type === 'deposit' ? '+' : '-' }}{{ formatAmount(transaction.amount, transaction.currency) }}
          </div>
          <StatusBadge :status="transaction.status" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAccountStore } from '../../../stores/account';
import StatusBadge from '../shared/StatusBadge.vue';
import { formatCurrency, formatNumber } from '../../../services/utils/formatters';
import { clientApi } from '../../../services/api/client';

const accountStore = useAccountStore();
const transactions = ref([]);
const loading = ref(true);
const lastDepositAt = ref(null);
const lastWithdrawalAt = ref(null);

const getTransactionIcon = (type) => {
  const icons = {
    deposit: 'fas fa-arrow-down',
    withdrawal: 'fas fa-arrow-up',
    trading: 'fas fa-exchange-alt',
    fee: 'fas fa-coins',
  };
  return icons[type] || 'fas fa-circle';
};

const getTransactionIconBg = (type) => {
  const bgClasses = {
    deposit: 'bg-green-500/20',
    withdrawal: 'bg-blue-500/20',
    trading: 'bg-purple-500/20',
    fee: 'bg-yellow-500/20',
  };
  return bgClasses[type] || 'bg-gray-500/20';
};

const getTransactionTypeLabel = (type) => {
  const labels = {
    deposit: 'Nạp tiền',
    withdrawal: 'Rút tiền',
    trading: 'Giao dịch',
    fee: 'Phí giao dịch',
  };
  return labels[type] || type;
};

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
    // Ưu tiên dùng clientApi.getDashboard() để lấy recentTransactions,
    // fallback sang accountStore.fetchTransactionHistory nếu cần.
    try {
      const dashboard = await clientApi.getDashboard();
      const data = dashboard.data || dashboard;

      if (data.stats) {
        lastDepositAt.value = data.stats.lastDepositAt || null;
        lastWithdrawalAt.value = data.stats.lastWithdrawalAt || null;
      }

      if (Array.isArray(data.recentTransactions)) {
        transactions.value = data.recentTransactions;
      } else {
        throw new Error('No recentTransactions in dashboard response');
      }
    } catch {
      const response = await accountStore.fetchTransactionHistory({ limit: 10 });
      const payload = response.data || response;
      transactions.value =
        payload.transactions || payload.recentTransactions || payload.data || [];
    }
  } catch (error) {
    console.error('Failed to fetch recent transactions:', error);
    transactions.value = [];
  } finally {
    loading.value = false;
  }
});

defineEmits(['view-detail']);
</script>
