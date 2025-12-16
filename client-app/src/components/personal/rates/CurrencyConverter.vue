<template>
  <div class="glass-panel rounded-lg p-6">
    <h3 class="text-lg font-bold text-white mb-6 flex items-center">
      <i class="fas fa-exchange-alt mr-2 text-purple-400"></i>
      Công Cụ Chuyển Đổi Tiền Tệ
    </h3>

    <div class="space-y-6">
      <!-- From Currency -->
      <div>
        <label class="text-purple-300 text-sm mb-2 block">Từ</label>
        <div class="flex space-x-3">
          <select
            v-model="fromCurrency"
            class="px-4 py-3 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white focus:border-purple-500/50 focus:outline-none"
          >
            <option value="USDT">USDT</option>
            <option value="VND">VND</option>
            <option value="USD">USD</option>
            <option value="CNY">CNY</option>
            <option value="EUR">EUR</option>
            <option value="GBP">GBP</option>
          </select>
          <input
            v-model.number="fromAmount"
            type="number"
            step="0.01"
            placeholder="Nhập số tiền"
            class="flex-1 px-4 py-3 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white placeholder-purple-300/50 focus:border-purple-500/50 focus:outline-none"
          />
        </div>
      </div>

      <!-- Swap Button -->
      <div class="flex justify-center">
        <button
          @click="swapCurrencies"
          class="w-12 h-12 bg-purple-500/20 border border-purple-500/30 rounded-full flex items-center justify-center text-purple-300 hover:bg-purple-500/30 transition-all"
        >
          <i class="fas fa-exchange-alt"></i>
        </button>
      </div>

      <!-- To Currency -->
      <div>
        <label class="text-purple-300 text-sm mb-2 block">Sang</label>
        <div class="flex space-x-3">
          <select
            v-model="toCurrency"
            class="px-4 py-3 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white focus:border-purple-500/50 focus:outline-none"
          >
            <option value="USDT">USDT</option>
            <option value="VND">VND</option>
            <option value="USD">USD</option>
            <option value="CNY">CNY</option>
            <option value="EUR">EUR</option>
            <option value="GBP">GBP</option>
          </select>
          <div class="flex-1 px-4 py-3 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white font-orbitron text-xl">
            {{ formatResult(toAmount) }}
          </div>
        </div>
      </div>

      <!-- Conversion Info -->
      <div v-if="fromAmount > 0" class="p-4 bg-slate-800/50 rounded-lg">
        <div class="text-purple-300 text-xs mb-2">Tỷ giá</div>
        <div class="text-white font-medium">
          1 {{ fromCurrency }} = {{ formatRate(conversionRate) }} {{ toCurrency }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useExchangeRatesStore } from '../../../stores/exchangeRates';
import { formatCurrency, formatNumber } from '../../../services/utils/formatters';

const exchangeRatesStore = useExchangeRatesStore();
const fromCurrency = ref('USDT');
const toCurrency = ref('VND');
const fromAmount = ref(0);

const conversionRate = computed(() => {
  if (fromCurrency.value === toCurrency.value) return 1;
  
  // If converting from USDT
  if (fromCurrency.value === 'USDT') {
    const rate = exchangeRatesStore.getRate('USDT', toCurrency.value);
    return rate || 1;
  }
  
  // If converting to USDT
  if (toCurrency.value === 'USDT') {
    const rate = exchangeRatesStore.getRate('USDT', fromCurrency.value);
    return rate ? 1 / rate : 1;
  }
  
  // Convert through USDT
  const fromRate = exchangeRatesStore.getRate('USDT', fromCurrency.value);
  const toRate = exchangeRatesStore.getRate('USDT', toCurrency.value);
  
  if (fromRate && toRate) {
    return toRate / fromRate;
  }
  
  return 1;
});

const toAmount = computed(() => {
  return fromAmount.value * conversionRate.value;
});

const swapCurrencies = () => {
  const temp = fromCurrency.value;
  fromCurrency.value = toCurrency.value;
  toCurrency.value = temp;
};

const formatResult = (amount) => {
  if (toCurrency.value === 'VND') {
    return `${formatNumber(amount)} ₫`;
  }
  return formatCurrency(amount, toCurrency.value);
};

const formatRate = (rate) => {
  return formatNumber(rate, 4);
};
</script>

