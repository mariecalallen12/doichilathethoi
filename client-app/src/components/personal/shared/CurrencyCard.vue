<template>
  <div class="glass-panel rounded-lg p-4 hover:border-purple-500/40 transition-all duration-300">
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center space-x-3">
        <div
          :class="[
            'w-12 h-12 rounded-lg flex items-center justify-center',
            currencyBgClasses[currency] || 'bg-purple-500/20'
          ]"
        >
          <i :class="[currencyIcons[currency] || 'fas fa-coins', 'text-xl']"></i>
        </div>
        <div>
          <div class="text-white font-bold text-lg">{{ currency }}</div>
          <div class="text-purple-300 text-xs">{{ currencyNames[currency] || currency }}</div>
        </div>
      </div>
      <div v-if="change24h !== null" :class="change24h >= 0 ? 'text-green-400' : 'text-red-400'">
        <i :class="change24h >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
        {{ Math.abs(change24h).toFixed(2) }}%
      </div>
    </div>

    <div class="space-y-2">
      <div>
        <div class="text-purple-300 text-xs mb-1">Tổng số dư</div>
        <div class="text-white font-orbitron text-xl font-bold">
          {{ formatAmount(totalBalance) }}
        </div>
      </div>

      <div class="grid grid-cols-2 gap-2 text-xs">
        <div>
          <div class="text-purple-300 mb-1">Khả dụng</div>
          <div class="text-green-400 font-medium">{{ formatAmount(availableBalance) }}</div>
        </div>
        <div>
          <div class="text-purple-300 mb-1">Bị khóa</div>
          <div class="text-yellow-400 font-medium">{{ formatAmount(lockedBalance) }}</div>
        </div>
      </div>

      <div v-if="pendingBalance > 0" class="pt-2 border-t border-purple-500/20">
        <div class="text-purple-300 text-xs mb-1">Chờ xử lý</div>
        <div class="text-blue-400 font-medium">{{ formatAmount(pendingBalance) }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatCurrency, formatNumber } from '../../../services/utils/formatters';

const props = defineProps({
  currency: {
    type: String,
    required: true,
  },
  totalBalance: {
    type: Number,
    default: 0,
  },
  availableBalance: {
    type: Number,
    default: 0,
  },
  lockedBalance: {
    type: Number,
    default: 0,
  },
  pendingBalance: {
    type: Number,
    default: 0,
  },
  change24h: {
    type: Number,
    default: null,
  },
});

const currencyNames = {
  USDT: 'Tether',
  BTC: 'Bitcoin',
  ETH: 'Ethereum',
  VND: 'Vietnamese Dong',
  USD: 'US Dollar',
  CNY: 'Chinese Yuan',
  GBP: 'British Pound',
  EUR: 'Euro',
};

const currencyIcons = {
  USDT: 'fas fa-coins',
  BTC: 'fab fa-bitcoin',
  ETH: 'fab fa-ethereum',
  VND: 'fas fa-money-bill-wave',
  USD: 'fas fa-dollar-sign',
  CNY: 'fas fa-yen-sign',
  GBP: 'fas fa-pound-sign',
  EUR: 'fas fa-euro-sign',
};

const currencyBgClasses = {
  USDT: 'bg-blue-500/20',
  BTC: 'bg-orange-500/20',
  ETH: 'bg-purple-500/20',
  VND: 'bg-green-500/20',
  USD: 'bg-green-500/20',
  CNY: 'bg-red-500/20',
  GBP: 'bg-indigo-500/20',
  EUR: 'bg-blue-500/20',
};

const formatAmount = (amount) => {
  if (props.currency === 'VND') {
    return `${formatNumber(amount)} ₫`;
  }
  if (props.currency === 'BTC') {
    return `₿${formatNumber(amount, 8)}`;
  }
  if (props.currency === 'ETH') {
    return `Ξ${formatNumber(amount, 6)}`;
  }
  return formatCurrency(amount, props.currency);
};
</script>

