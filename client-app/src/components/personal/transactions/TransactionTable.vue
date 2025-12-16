<template>
  <div class="glass-panel rounded-lg p-6 overflow-x-auto">
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 5" :key="i" class="h-16 bg-slate-800/50 rounded-lg animate-pulse"></div>
    </div>

    <div v-else-if="transactions.length === 0" class="text-center py-12 text-purple-300">
      <i class="fas fa-inbox text-4xl mb-2"></i>
      <p>Không có giao dịch nào</p>
    </div>

    <table v-else class="w-full">
      <thead>
        <tr class="border-b border-purple-500/20">
          <th class="text-left py-3 px-4 text-purple-300 text-sm font-medium">Ngày/Giờ</th>
          <th class="text-left py-3 px-4 text-purple-300 text-sm font-medium">Loại</th>
          <th class="text-left py-3 px-4 text-purple-300 text-sm font-medium">Tiền tệ</th>
          <th class="text-right py-3 px-4 text-purple-300 text-sm font-medium">Số tiền</th>
          <th class="text-right py-3 px-4 text-purple-300 text-sm font-medium">Phí</th>
          <th class="text-left py-3 px-4 text-purple-300 text-sm font-medium">Trạng thái</th>
          <th class="text-left py-3 px-4 text-purple-300 text-sm font-medium">Mã tham chiếu</th>
          <th class="text-center py-3 px-4 text-purple-300 text-sm font-medium">Thao tác</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="transaction in transactions"
          :key="transaction.id"
          class="border-b border-purple-500/10 hover:bg-slate-800/50 transition-colors"
        >
          <td class="py-3 px-4 text-white text-sm">{{ formatDate(transaction.createdAt) }}</td>
          <td class="py-3 px-4">
            <div class="flex items-center space-x-2">
              <i :class="[getTransactionIcon(transaction.type), getTransactionIconColor(transaction.type)]"></i>
              <span class="text-white text-sm">{{ getTransactionTypeLabel(transaction.type) }}</span>
            </div>
          </td>
          <td class="py-3 px-4 text-white text-sm">{{ transaction.currency }}</td>
          <td
            :class="[
              'py-3 px-4 text-right font-orbitron font-medium',
              transaction.type === 'deposit' ? 'text-green-400' : 'text-red-400'
            ]"
          >
            {{ transaction.type === 'deposit' ? '+' : '-' }}{{ formatAmount(transaction.amount, transaction.currency) }}
          </td>
          <td class="py-3 px-4 text-right text-purple-300 text-sm">
            {{ transaction.fee ? formatAmount(transaction.fee, transaction.currency) : '-' }}
          </td>
          <td class="py-3 px-4">
            <StatusBadge :status="transaction.status" />
          </td>
          <td class="py-3 px-4 text-purple-300 text-xs font-mono">{{ transaction.id.slice(0, 8) }}...</td>
          <td class="py-3 px-4 text-center">
            <button
              @click="$emit('view-detail', transaction)"
              class="px-3 py-1 bg-purple-500/20 text-purple-300 rounded hover:bg-purple-500/30 transition-colors text-sm"
            >
              Chi tiết
            </button>
          </td>
        </tr>
      </tbody>
    </table>
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
  loading: {
    type: Boolean,
    default: false,
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

const getTransactionIconColor = (type) => {
  const colors = {
    deposit: 'text-green-400',
    withdrawal: 'text-blue-400',
    trading: 'text-purple-400',
    fee: 'text-yellow-400',
  };
  return colors[type] || 'text-gray-400';
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

