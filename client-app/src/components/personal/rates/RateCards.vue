<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div
      v-for="rate in rates"
      :key="rate.pair"
      class="glass-panel rounded-lg p-6 hover:border-purple-500/40 transition-all"
    >
      <div class="flex items-center justify-between mb-4">
        <div>
          <div class="text-white font-bold text-lg">{{ rate.from }} → {{ rate.to }}</div>
          <div class="text-purple-300 text-xs">{{ getPairLabel(rate.pair) }}</div>
        </div>
        <div
          :class="[
            'w-3 h-3 rounded-full',
            updateStatus === 'fresh' ? 'bg-green-500' : updateStatus === 'recent' ? 'bg-yellow-500' : 'bg-red-500'
          ]"
          :title="updateStatusText"
        ></div>
      </div>

      <div class="mb-4">
        <div class="font-orbitron text-3xl font-bold text-white mb-2">
          {{ formatRate(rate.rate, rate.to) }}
        </div>
        <div
          :class="[
            'flex items-center space-x-2 text-sm font-medium',
            rate.change24h >= 0 ? 'text-green-400' : 'text-red-400'
          ]"
        >
          <i :class="rate.change24h >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
          <span>{{ Math.abs(rate.change24h).toFixed(2) }}%</span>
          <span>({{ rate.change24h >= 0 ? '+' : '' }}{{ formatChangeAmount(rate.changeAmount, rate.to) }})</span>
        </div>
      </div>

      <div class="pt-4 border-t border-purple-500/20 space-y-2">
        <div class="flex justify-between text-xs">
          <span class="text-purple-300">Cao</span>
          <span class="text-white">{{ formatRate(rate.high, rate.to) }}</span>
        </div>
        <div class="flex justify-between text-xs">
          <span class="text-purple-300">Thấp</span>
          <span class="text-white">{{ formatRate(rate.low, rate.to) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useExchangeRatesStore } from '../../../stores/exchangeRates';
import { formatNumber } from '../../../services/utils/formatters';

const exchangeRatesStore = useExchangeRatesStore();
const rates = computed(() => exchangeRatesStore.rates);
const updateStatus = computed(() => exchangeRatesStore.updateStatus);

const updateStatusText = computed(() => {
  const statusMap = {
    fresh: 'Cập nhật < 1 phút',
    recent: 'Cập nhật 1-5 phút',
    stale: 'Cập nhật > 5 phút',
  };
  return statusMap[updateStatus.value] || '';
});

const getPairLabel = (pair) => {
  const labels = {
    USDT_VND: 'Tether to Vietnamese Dong',
    USDT_USD: 'Tether to US Dollar',
    USDT_CNY: 'Tether to Chinese Yuan',
    USDT_EUR: 'Tether to Euro',
    USDT_GBP: 'Tether to British Pound',
  };
  return labels[pair] || pair;
};

const formatRate = (rate, currency) => {
  if (currency === 'VND') {
    return `${formatNumber(rate)} ₫`;
  }
  if (currency === 'USD') {
    return `$${formatNumber(rate, 4)}`;
  }
  if (currency === 'CNY') {
    return `¥${formatNumber(rate, 2)}`;
  }
  if (currency === 'EUR') {
    return `€${formatNumber(rate, 2)}`;
  }
  if (currency === 'GBP') {
    return `£${formatNumber(rate, 2)}`;
  }
  return formatNumber(rate, 4);
};

const formatChangeAmount = (amount, currency) => {
  if (currency === 'VND') {
    return `${amount >= 0 ? '+' : ''}${formatNumber(amount)} ₫`;
  }
  if (currency === 'USD') {
    return `${amount >= 0 ? '+' : ''}$${formatNumber(Math.abs(amount), 4)}`;
  }
  return `${amount >= 0 ? '+' : ''}${formatNumber(Math.abs(amount), 4)}`;
};
</script>

