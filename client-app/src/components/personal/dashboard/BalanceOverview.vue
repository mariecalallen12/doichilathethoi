<template>
  <div class="glass-panel rounded-lg p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-xl font-bold text-white flex items-center">
        <i class="fas fa-wallet mr-2 text-purple-400"></i>
        Tổng Quan Số Dư Ví
      </h3>
      <button
        @click="toggleBalanceVisibility"
        class="p-2 text-purple-300 hover:text-white transition-colors"
        :title="balanceHidden ? 'Hiển thị số dư' : 'Ẩn số dư'"
      >
        <i :class="balanceHidden ? 'fas fa-eye' : 'fas fa-eye-slash'"></i>
      </button>
    </div>

    <!-- Total Balance in VND -->
    <div class="mb-6">
      <div class="text-purple-300 text-sm mb-2">Tổng số dư (VND)</div>
      <div v-if="!balanceHidden" class="font-orbitron text-3xl font-bold text-white">
        {{ formatVND(totalBalanceVND) }}
      </div>
      <div v-else class="font-orbitron text-3xl font-bold text-white">••••••</div>
    </div>

    <!-- Balance Breakdown -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-slate-800/50 rounded-lg p-4">
        <div class="text-purple-300 text-xs mb-1">Khả dụng</div>
        <div v-if="!balanceHidden" class="text-green-400 font-orbitron text-xl font-bold">
          {{ formatVND(availableBalance) }}
        </div>
        <div v-else class="text-green-400 font-orbitron text-xl font-bold">••••</div>
      </div>
      <div class="bg-slate-800/50 rounded-lg p-4">
        <div class="text-purple-300 text-xs mb-1">Bị khóa</div>
        <div v-if="!balanceHidden" class="text-yellow-400 font-orbitron text-xl font-bold">
          {{ formatVND(lockedBalance) }}
        </div>
        <div v-else class="text-yellow-400 font-orbitron text-xl font-bold">••••</div>
      </div>
      <div class="bg-slate-800/50 rounded-lg p-4">
        <div class="text-purple-300 text-xs mb-1">Chờ xử lý</div>
        <div v-if="!balanceHidden" class="text-blue-400 font-orbitron text-xl font-bold">
          {{ formatVND(pendingBalance) }}
        </div>
        <div v-else class="text-blue-400 font-orbitron text-xl font-bold">••••</div>
      </div>
    </div>

    <!-- Multi-Currency Balances -->
    <div class="mt-6 pt-6 border-t border-purple-500/20">
      <div class="text-purple-300 text-sm mb-4">Số dư theo loại tiền tệ</div>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div
          v-for="(balance, currency) in currencyBalances"
          :key="currency"
          class="bg-slate-800/50 rounded-lg p-3"
        >
          <div class="text-purple-300 text-xs mb-1">{{ currency }}</div>
          <div v-if="!balanceHidden" class="text-white font-medium text-sm">
            {{ formatCurrency(balance, currency) }}
          </div>
          <div v-else class="text-white font-medium text-sm">•••</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useAccountStore } from '../../../stores/account';
import { useExchangeRatesStore } from '../../../stores/exchangeRates';
import { useWebSocketStore } from '../../../stores/websocket';
import { formatCurrency, formatNumber } from '../../../services/utils/formatters';

const accountStore = useAccountStore();
const exchangeRatesStore = useExchangeRatesStore();
const wsStore = useWebSocketStore();
const balanceHidden = ref(false);
const exchangeRateUSDTtoVND = ref(24850); // Default rate, sẽ cập nhật từ store tỷ giá nếu có

const btcToUsdt = computed(() => {
  try {
    const rate = exchangeRatesStore.getRate('BTC', 'USDT');
    return rate || 43000; // fallback hợp lý nếu chưa có tỷ giá
  } catch (error) {
    console.warn('Error getting BTC/USDT rate:', error);
    return 43000; // fallback
  }
});

const ethToUsdt = computed(() => {
  try {
    const rate = exchangeRatesStore.getRate('ETH', 'USDT');
    return rate || 2650; // fallback hợp lý nếu chưa có tỷ giá
  } catch (error) {
    console.warn('Error getting ETH/USDT rate:', error);
    return 2650; // fallback
  }
});

const toggleBalanceVisibility = () => {
  balanceHidden.value = !balanceHidden.value;
};

const totalBalanceVND = computed(() => {
  // Calculate total balance in VND
  let total = 0;
  const usdtToVnd = exchangeRateUSDTtoVND.value;
  
  // Add crypto balances converted to VND
  if (accountStore.currencies?.crypto) {
    Object.entries(accountStore.currencies.crypto).forEach(([currency, data]) => {
      const normalizedCurrency = (currency || '').trim().toUpperCase();
      if (normalizedCurrency === 'USDT') {
        total += (data.value || 0) * usdtToVnd;
      } else if (normalizedCurrency === 'BTC') {
        total += (data.value || 0) * usdtToVnd * btcToUsdt.value;
      } else if (normalizedCurrency === 'ETH') {
        total += (data.value || 0) * usdtToVnd * ethToUsdt.value;
      }
    });
  }
  
  // Add fiat balances
  if (accountStore.currencies?.fiat) {
    if (accountStore.currencies.fiat.VND) {
      total += accountStore.currencies.fiat.VND.value || 0;
    }
    if (accountStore.currencies.fiat.USD) {
      total += (accountStore.currencies.fiat.USD.value || 0) * usdtToVnd;
    }
  }
  
  return total;
});

const availableBalance = computed(() => {
  return accountStore.balance?.available || 0;
});

const lockedBalance = computed(() => {
  return accountStore.balance?.locked || 0;
});

const pendingBalance = computed(() => {
  return accountStore.balance?.pending || 0;
});

const currencyBalances = computed(() => {
  const balances = {};
  
  if (accountStore.currencies?.crypto) {
    Object.entries(accountStore.currencies.crypto).forEach(([currency, data]) => {
      balances[currency] = data.balance || 0;
    });
  }
  
  if (accountStore.currencies?.fiat) {
    Object.entries(accountStore.currencies.fiat).forEach(([currency, data]) => {
      balances[currency] = data.balance || 0;
    });
  }
  
  return balances;
});

const formatVND = (amount) => {
  return `${formatNumber(amount)} ₫`;
};

// Auto-refresh fallback (if WebSocket fails)
let refreshInterval = null;

onMounted(async () => {
  // Initial fetch
  await accountStore.fetchBalance();
  
  // Lấy tỷ giá USDT → VND từ store exchangeRates nếu có
  try {
    await exchangeRatesStore.fetchRates();
    const rate = exchangeRatesStore.getRate('USDT', 'VND');
    if (rate && typeof rate === 'number' && !isNaN(rate)) {
      exchangeRateUSDTtoVND.value = rate;
    }
  } catch (e) {
    console.error('Failed to fetch exchange rates for BalanceOverview:', e);
  }
  
  // Connect WebSocket for real-time updates
  if (typeof window !== 'undefined') {
    const wsUrl = import.meta.env.VITE_WS_URL || window.location.origin.replace(/^http/, 'ws');
    if (!wsStore.isConnected) {
      wsStore.connect(wsUrl);
    }
    
    // Watch for exchange rate updates from WebSocket
    const unwatch = exchangeRatesStore.$subscribe((mutation, state) => {
      try {
        const rate = state.getRate('USDT', 'VND');
        if (rate && typeof rate === 'number' && !isNaN(rate)) {
          exchangeRateUSDTtoVND.value = rate;
        }
      } catch (error) {
        console.warn('Error updating USDT/VND rate from WebSocket:', error);
      }
    });
    
    // Fallback polling if WebSocket is not connected (every 30 seconds)
    refreshInterval = setInterval(async () => {
      if (!wsStore.isConnected) {
        await accountStore.fetchBalance();
        try {
          await exchangeRatesStore.fetchRates();
          const rate = exchangeRatesStore.getRate('USDT', 'VND');
          if (rate && typeof rate === 'number' && !isNaN(rate)) {
            exchangeRateUSDTtoVND.value = rate;
          }
        } catch (e) {
          console.error('Failed to refresh exchange rates:', e);
        }
      }
    }, 30000);
  }
});

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }
});
</script>
