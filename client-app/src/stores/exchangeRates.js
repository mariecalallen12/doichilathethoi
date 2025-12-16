import { defineStore } from 'pinia';
import { ref } from 'vue';
import { clientApi } from '../services/api/client';
import websocketService from '../services/websocket';
import { useWebSocketStore } from './websocket';
import { getWsBaseUrl } from '../utils/runtimeConfig';
import axios from 'axios';
import { getApiBaseUrl } from '../utils/runtimeConfig';

const API_BASE_URL = getApiBaseUrl();

// Fallback api instance cho các trường hợp đặc biệt nếu cần
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const useExchangeRatesStore = defineStore('exchangeRates', () => {
  const rates = ref([]);

  const isLoading = ref(false);
  const lastUpdate = ref(new Date());
  const updateStatus = ref('fresh'); // 'fresh', 'recent', 'stale'
  const error = ref(null);

  async function fetchRates() {
    isLoading.value = true;
    error.value = null;

    try {
      // Ưu tiên dùng clientApi.getExchangeRates() từ module client
      let payload;
      try {
        const clientResponse = await clientApi.getExchangeRates();
        payload = clientResponse;
      } catch {
        // Fallback: thử các endpoint cũ nếu có
        const response = await api.get('/financial/exchange-rates').catch(() => {
          return api.get('/market/market-data');
        });
        payload = response.data;
      }

      const data = payload.data || payload;

      if (Array.isArray(data)) {
        // Trường hợp client backend trả về list ExchangeRate
        rates.value = data.map((rate) => {
          const from = (rate.baseAsset || '').trim().toUpperCase();
          const to = (rate.targetAsset || '').trim().toUpperCase();
          return {
            pair: `${from}_${to}`,
            from,
            to,
            rate: rate.rate,
            change24h: rate.change24h || 0,
            changeAmount: rate.changeAmount || 0,
            high: rate.high || rate.rate,
            low: rate.low || rate.rate,
          };
        });
      } else if (Array.isArray(data.rates) || Array.isArray(data.exchange_rates)) {
        const ratesData = data.rates || data.exchange_rates;
        rates.value = ratesData.map((rate) => {
          const from = (rate.from_currency || '').trim().toUpperCase();
          const to = (rate.to_currency || '').trim().toUpperCase();
          return {
            pair: `${from}_${to}`,
            from,
            to,
            rate: rate.rate,
            change24h: rate.change_24h || 0,
            changeAmount: rate.change_amount || 0,
            high: rate.high_24h || rate.rate,
            low: rate.low_24h || rate.rate,
          };
        });
      }

      lastUpdate.value = new Date();
      updateStatus.value = 'fresh';

      return data;
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to fetch exchange rates';
      // Keep existing rates if fetch fails
      console.error('Error fetching exchange rates:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  function updateRates(newRates) {
    rates.value = newRates;
    lastUpdate.value = new Date();
    updateStatus.value = 'fresh';
  }

  function getRate(from, to) {
    // Normalize currency codes: trim whitespace and convert to uppercase
    const normalizedFrom = (from || '').trim().toUpperCase();
    const normalizedTo = (to || '').trim().toUpperCase();
    
    // Validate currency codes
    if (!normalizedFrom || !normalizedTo) {
      console.warn(`Invalid currency code: from="${from}", to="${to}"`);
      return null;
    }
    
    const pair = rates.value.find(r => r.from === normalizedFrom && r.to === normalizedTo);
    return pair ? pair.rate : null;
  }

  // Auto-refresh every minute
  let refreshInterval = null;

  function startAutoRefresh() {
    // Initial fetch
    fetchRates();
    
    // Set interval based on env or default to 60 seconds
    const intervalMs = parseInt(import.meta.env.VITE_MARKET_DATA_UPDATE_INTERVAL || '60000', 10);
    
    refreshInterval = setInterval(() => {
      fetchRates().catch(err => {
        console.error('Auto-refresh exchange rates failed:', err);
        // Update status to stale if fetch fails
        const minutesSinceUpdate = (new Date() - lastUpdate.value) / 60000;
        if (minutesSinceUpdate >= 5) {
          updateStatus.value = 'stale';
        }
      });
    }, intervalMs);
  }

  function stopAutoRefresh() {
    if (refreshInterval) {
      clearInterval(refreshInterval);
      refreshInterval = null;
    }
  }

  // WebSocket integration for real-time exchange rate updates
  function setupWebSocketListeners() {
    if (typeof window === 'undefined') return;
    
    // Ensure WebSocket is connected
    const wsStore = useWebSocketStore();
    const wsUrl = getWsBaseUrl();
    if (!wsStore.isConnected) {
      wsStore.connect(wsUrl);
    }
    
    // Listen for exchange rate updates
    websocketService.subscribe('exchange_rates', (message) => {
      const data = message.data || message;
      if (data.rates && Array.isArray(data.rates)) {
        // Update rates from WebSocket
        updateRates(data.rates);
      } else if (data.rate) {
        // Single rate update
        const from = (data.rate.from || '').trim().toUpperCase();
        const to = (data.rate.to || '').trim().toUpperCase();
        const rateIndex = rates.value.findIndex(r => 
          r.from === from && r.to === to
        );
        if (rateIndex >= 0) {
          rates.value[rateIndex] = { ...rates.value[rateIndex], ...data.rate, from, to };
        } else {
          rates.value.push({
            pair: `${from}_${to}`,
            from,
            to,
            rate: data.rate.rate,
            change24h: data.rate.change24h || 0,
            changeAmount: data.rate.changeAmount || 0,
            high: data.rate.high || data.rate.rate,
            low: data.rate.low || data.rate.rate,
          });
        }
        lastUpdate.value = new Date();
        updateStatus.value = 'fresh';
      }
    });
  }

  // Setup WebSocket on store initialization
  if (typeof window !== 'undefined') {
    setupWebSocketListeners();
  }

  return {
    rates,
    isLoading,
    lastUpdate,
    updateStatus,
    error,
    fetchRates,
    updateRates,
    getRate,
    startAutoRefresh,
    stopAutoRefresh,
    setupWebSocketListeners,
  };
});
