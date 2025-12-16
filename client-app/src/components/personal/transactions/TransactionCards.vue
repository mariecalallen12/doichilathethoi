<template>
  <div class="space-y-3">
    <div
      v-for="transaction in transactions"
      :key="transaction.id"
      class="glass-panel rounded-lg p-4 hover:border-purple-500/40 transition-all"
      @click="$emit('view-detail', transaction)"
    >
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center space-x-3">
          <div
            :class="[
              'w-12 h-12 rounded-lg flex items-center justify-center',
              getTransactionIconBg(transaction.type)
            ]"
          >
            <i :class="[getTransactionIcon(transaction.type), 'text-xl']"></i>
          </div>
          <div>
            <div class="text-white font-medium">{{ getTransactionTypeLabel(transaction.type) }}</div>
            <div class="text-purple-300 text-xs">{{ formatDate(transaction.createdAt) }}</div>
          </div>
        </div>
        <StatusBadge :status="transaction.status" />
      </div>

      <div class="flex items-center justify-between">
        <div>
          <div class="text-purple-300 text-xs mb-1">{{ transaction.currency }}</div>
          <div
            :class="[
              'font-orbitron font-bold text-lg',
              transaction.type === 'deposit' ? 'text-green-400' : 'text-red-400'
            ]"
          >
            {{ transaction.type === 'deposit' ? '+' : '-' }}{{ formatAmount(transaction.amount, transaction.currency) }}
          </div>
        </div>
        <div class="text-right">
          <div class="text-purple-300 text-xs mb-1">Mã tham chiếu</div>
          <div class="text-purple-300 text-xs font-mono">{{ transaction.id.slice(0, 8) }}...</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import StatusBadge from '../shared/StatusBadge.vue';
import { formatCurrency, formatNumber } from '../../../services/utils/formatters';

defineProps({
  transactions: {
    type: Array,
    default: () => [],
  },
});

defineEmits(['view-detail']);

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
    fee: 'Phí',
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
</script>

