import { defineStore } from 'pinia';
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { accountApi } from '../services/api/account';
import { clientApi } from '../services/api/client';
import { useWebSocketStore } from './websocket';
import websocketService from '../services/websocket';

export const useAccountStore = defineStore('account', () => {
  const balance = ref({
    available: 0,
    locked: 0,
    pending: 0,
    usedMargin: 0,
  });

  const equity = computed(() => {
    return balance.value.available + balance.value.locked;
  });

  const pnlToday = ref(0);
  const currencies = ref({}); // Will be populated from API

  const isLoading = ref(false);
  const error = ref(null);

  async function fetchBalance() {
    isLoading.value = true;
    error.value = null;
    
    // Check authentication trước khi gọi API
    const token = localStorage.getItem('auth_token');
    if (!token) {
      isLoading.value = false;
      return; // Không gọi API nếu chưa đăng nhập
    }
    
    try {
      // Ưu tiên dùng clientApi.getWalletBalances (module client),
      // fallback sang accountApi.getBalance nếu cần.
      let data;
      try {
        const clientResponse = await clientApi.getWalletBalances();
        data = clientResponse;
      } catch (err) {
        // Suppress 401 errors (expected khi token hết hạn hoặc chưa đăng nhập)
        if (err.response?.status === 401) {
          isLoading.value = false;
          return;
        }
        const response = await accountApi.getBalance();
        data = response.data || response;
      }

      const balances = data.data || data.balances || data;

      if (Array.isArray(balances)) {
        // Backend client module trả về list WalletBalance
        currencies.value = {};

        let totalAvailable = 0;
        let totalLocked = 0;
        let totalPending = 0;

        balances.forEach((bal) => {
          // Normalize currency code: trim whitespace and convert to uppercase
          const asset = (bal.asset || bal.currency || '').trim().toUpperCase();
          
          // Skip if asset is empty after normalization
          if (!asset) {
            console.warn('Skipping balance with invalid currency code:', bal);
            return;
          }
          
          const available = bal.availableBalance ?? bal.available ?? 0;
          const locked = bal.lockedBalance ?? bal.locked ?? 0;
          const pending = bal.pendingBalance ?? bal.pending ?? 0;
          const total = bal.totalBalance ?? bal.total ?? available + locked + pending;

          totalAvailable += available;
          totalLocked += locked;
          totalPending += pending;

          const targetKey =
            ['BTC', 'ETH', 'USDT', 'BNB'].includes(asset) ? 'crypto' : 'fiat';

          if (!currencies.value[targetKey]) currencies.value[targetKey] = {};
          currencies.value[targetKey][asset] = {
            balance: total,
            value: total,
          };
        });

        balance.value = {
          available: totalAvailable,
          locked: totalLocked,
          pending: totalPending,
          usedMargin: totalLocked,
        };
      }

      return balances;
    } catch (err) {
      // Chỉ set error cho các lỗi không phải 401 (expected behavior)
      if (err.response?.status !== 401) {
        error.value = err.message || 'Failed to fetch balance';
      }
      // Không throw error cho 401 (expected khi chưa đăng nhập)
      if (err.response?.status !== 401) {
        throw err;
      }
    } finally {
      isLoading.value = false;
    }
  }

  async function deposit(amount, currency = 'USD', method = 'bank') {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await accountApi.deposit({ amount, currency, method });
      await fetchBalance();
      return response;
    } catch (err) {
      error.value = err.message || 'Failed to deposit';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function withdraw(amount, currency = 'USD', method = 'bank') {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await accountApi.withdraw({ amount, currency, method });
      await fetchBalance();
      return response;
    } catch (err) {
      error.value = err.message || 'Failed to withdraw';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchTransactionHistory(filters = {}) {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await accountApi.getTransactionHistory(filters);
      return response;
    } catch (err) {
      error.value = err.message || 'Failed to fetch transaction history';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // WebSocket integration for real-time balance updates
  function setupWebSocketListeners() {
    if (typeof window === 'undefined') return;
    
    // Ensure WebSocket is connected
    const wsStore = useWebSocketStore();
    const wsUrl = import.meta.env.VITE_WS_URL || window.location.origin.replace(/^http/, 'ws');
    if (!wsStore.isConnected) {
      wsStore.connect(wsUrl);
    }
    
    // Listen for account balance updates via websocketService
    websocketService.subscribe('account', (message) => {
      const data = message.data || message;
      if (data.balance) {
        balance.value = { ...balance.value, ...data.balance };
      }
      if (data.currencies) {
        currencies.value = { ...currencies.value, ...data.currencies };
      }
      if (data.pnl_today !== undefined) {
        pnlToday.value = data.pnl_today;
      }
    });
  }

  // Setup WebSocket on store initialization
  if (typeof window !== 'undefined') {
    setupWebSocketListeners();
  }

  return {
    balance,
    equity,
    pnlToday,
    currencies,
    isLoading,
    error,
    fetchBalance,
    deposit,
    withdraw,
    fetchTransactionHistory,
    setupWebSocketListeners,
  };
});
